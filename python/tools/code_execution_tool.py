from dataclasses import dataclass
import os, json, contextlib, subprocess, ast, shlex
from io import StringIO
import time
from typing import Literal
from python.helpers import files, messages
from agent import Agent
from python.helpers.tool import Tool, Response
from python.helpers import files
from python.helpers.print_style import PrintStyle
from python.helpers.shell_local import LocalInteractiveSession
from python.helpers.shell_ssh import SSHInteractiveSession
from python.helpers.docker import DockerContainerManager

@dataclass
class State:
    shell: LocalInteractiveSession | SSHInteractiveSession
    docker: DockerContainerManager | None
        

class CodeExecution(Tool):

    def execute(self,**kwargs):

        if self.agent.handle_intervention(): return Response(message="", break_loop=False)  # wait for intervention and handle it, if paused
        
        #self.prepare_state()

        # os.chdir(files.get_abs_path("./work_dir")) #change CWD to work_dir
        
        runtime = self.args["runtime"].lower().strip()
        if runtime == "python":
            response = self.execute_python_code(self.args["code"])
        elif runtime == "nodejs":
            response = self.execute_nodejs_code(self.args["code"])
        elif runtime == "terminal":
            response = self.execute_terminal_command(self.args["code"])
        elif runtime == "output":
            response = self.get_terminal_output()
        else:
            response = files.read_file("./prompts/fw.code_runtime_wrong.md", runtime=runtime)

        if not response: response = files.read_file("./prompts/fw.code_no_output.md")
        return Response(message=response, break_loop=False)

    def after_execution(self, response, **kwargs):
        msg_response = files.read_file("./prompts/fw.tool_response.md", tool_name=self.name, tool_response=response.message)
        self.agent.append_message(msg_response, human=True)

    def make_custom_open(self,base_path):
        def custom_open(file, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True, opener=None):
            # Create the full path by joining the base path with the provided file name
            full_path = os.path.join(base_path, file)
            return open(full_path, mode, buffering, encoding, errors, newline, closefd, opener)
        return custom_open
    
    def prepare_state(self):
        self.state = self.agent.get_data("cot_state")
        if not self.state:

            #initialize docker container if execution in docker is configured
            if self.agent.config.code_exec_docker_enabled:
                print("Starting docker container...")
                docker = DockerContainerManager(name=self.agent.config.code_exec_docker_name, image=self.agent.config.code_exec_docker_image, ports=self.agent.config.code_exec_docker_ports, volumes=self.agent.config.code_exec_docker_volumes)
                docker.start_container()
            else: docker = None

            #initialize local or remote interactive shell insterface
            if self.agent.config.code_exec_ssh_enabled:
                print("Starting SSH session...")
                shell = SSHInteractiveSession(self.agent.config.code_exec_ssh_addr,self.agent.config.code_exec_ssh_port,self.agent.config.code_exec_ssh_user,self.agent.config.code_exec_ssh_pass)
            else: shell = LocalInteractiveSession()
                
            self.state = State(shell=shell,docker=docker)
            shell.connect()
        self.agent.set_data("cot_state", self.state)
    
    def execute_python_code(self, code):
        # Path of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Path to the 'work_dir' directory
        work_dir_path = os.path.join(script_dir, '..', '..', 'work_dir')
        work_dir_path = os.path.normpath(work_dir_path)  # Normalize the path to remove any relative path elements

        print("Working Directory Path:", work_dir_path)
                # Create a custom open function that operates within the specified working directory
        custom_open = self.make_custom_open(work_dir_path)
        
        # Environment for code execution
        local_context = {'__builtins__': {}}
        for builtin_name in dir(__builtins__):
            if builtin_name != 'open':  # Exclude the standard open to replace it with custom_open
                local_context['__builtins__'][builtin_name] = getattr(__builtins__, builtin_name)
        local_context['open'] = custom_open  # Use the custom open
        
        # Execute the code in the local environment
        try:
            exec(code, {}, local_context)
            return local_context  # You might want to return specific values or handle the output differently
        except Exception as e:
            return str(e)

    def execute_nodejs_code(self, code):
        escaped_code = shlex.quote(code)
        command = f'node -e {escaped_code}'
        return self.terminal_session(command)

    def execute_terminal_command(self, command):
        return self.terminal_session(command)

    def terminal_session(self, command):

        if self.agent.handle_intervention(): return ""  # wait for intervention and handle it, if paused
       
        self.state.shell.send_command(command)

        PrintStyle(background_color="white",font_color="#1B4F72",bold=True).print(f"{self.agent.agent_name} code execution output:")
        return self.get_terminal_output()

    def get_terminal_output(self):
        idle=0
        while True:       
            time.sleep(0.1)  # Wait for some output to be generated
            full_output, partial_output = self.state.shell.read_output()

            if self.agent.handle_intervention(): return full_output  # wait for intervention and handle it, if paused
        
            if partial_output:
                PrintStyle(font_color="#85C1E9").stream(partial_output)
                idle=0    
            else:
                idle+=1
                if ( full_output and idle > 30 ) or ( not full_output and idle > 100 ): return full_output
                           