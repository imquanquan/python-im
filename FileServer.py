#!/usr/bin/env python3.6

from asyncore import dispatcher
from asynchat import async_chat
from threading import Thread
import time
import socket, asyncore

from Room import CommandHandler, EndSession
     
                    
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
                send, target, file_name = data.split(b' ', 2)
                i = 0
                with open(file_name, 'wb') as f:
                    while True:
                        data = self.socket.recv(1024)
                        i += len(data)
                        if len(data) != 1024 or data == b' ':
                            break                        
                        f.write(data)
                    print(i)
                
                self.send_file(target, file_name)
                        
    def send_file(self, name, file_name):
        with open(file_name, 'rb') as f:
            file_size = len(f.read())        
        self.server.users[name].socket.send(b'recv ' + name + b' ' + str(file_size).encode('utf-8') + b' ' + file_name)
        time.sleep(1)
        i = 0
        with open(file_name, 'rb') as f:
            l = f.read(1024)
            flag = 1
            while (l):
                self.server.users[name].socket.send(l)
                i += len(l)
                l = f.read(1024)
                if len(l) != 1024:
                    flag = 0
            if flag:
                self.server.users[name].socket.send(b' ')
            print(i)
        
        

class FileServer(dispatcher):
    def __init__(self, port):
        dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(('', port))
        self.listen(5)
        self.users = {}
        self.main_channel = FileChannel(self)

    def handle_accept(self):
        conn, addr = self.accept()
        FileSession(self, conn)
