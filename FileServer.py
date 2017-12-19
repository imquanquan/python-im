#!/usr/bin/env python3.6

from asyncore import dispatcher
from threading import Thread
import time
import socket, asyncore

                   
class FileSession:
    def __init__(self, server, sock):
        self.socket = sock
        self.server = server
        self.name = None
        t = Thread(target=self.handle)
        t.start()
        
    def handle(self):
        while True:
            data = self.socket.recv(1024)
            if data[:4] == b'name':
                self.name = data[5:]
                self.server.users[self.name] = self
            elif data[:4] == b'send':
                self.flag = 0
                print(data)
                send, target, file_size, file_name = data.split(b' ', 3)
                i = 0
                file_size = int(file_size.decode("utf-8"))
                print(file_size)
                file_byte = b''
                while True:
                    data = self.socket.recv(1024)
                                       
                    file_byte += data
                    print(len(file_byte))
                    if len(file_byte) == file_size:
                        break                     
                with open(file_name.decode('utf-8'), 'wb') as f:
                    f.write(file_byte)
                
                self.send_file(target, file_name)
                        
    def send_file(self, name, file_name):
        
        with open(file_name, 'rb') as f:
            file_size = len(f.read())        
        self.server.users[name].socket.send(b'recv ' + name + b' ' + str(file_size).encode('utf-8') + b' ' + file_name)
        print(b'recv ' + name + b' ' + str(file_size).encode('utf-8') + b' ' + file_name)
        response = self.socket.recv(1024)
        print(response)
        if response == b'ok':        
            i = 0
            with open(file_name, 'rb') as f:
                l = f.read(1024)
                while (l):
                    self.server.users[name].socket.send(l)
                    i += len(l)
                    l = f.read(1024)
                    print(i)
                print('sent')
        
        

class FileServer(dispatcher):
    def __init__(self, port):
        dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(('', port))
        self.listen(5)
        self.users = {}

    def handle_accept(self):
        conn, addr = self.accept()
        FileSession(self, conn)
