#!/usr/bin/env python3.6

from asyncore import dispatcher
from asynchat import async_chat
from threading import Thread
import socket, asyncore

from Room import CommandHandler, EndSession
     

class Channel(CommandHandler):
    def __init__(self, server):
        self.server = server
        self.sessions = []
    
    def add_session(self, session):
        self.sessions.append(session)
        
    def remove_session(self, session):
        self.sessions.remove(session)    
    
    def do_logout(self, session, line):
        raise EndSession 


class LoginChannel(Channel): 
    def do_login(self, session, name):
        session.name = name
        print(session.name)
        self.server.users[session.name] = session
        session.enter(self.server.main_channel)
        
class FileChannel(Channel):
    def add_session(self, session):
        Channel.add_session(self, session)
        
    def do_send_file(self, session, line):
        line = line.split(b' ', 3)
        print(line)
        self.server.users[line[1]].push(b'receive ' + line[0] + b' ' + line[2] + b' ' + line[3])
        print(line[3])
        
class FileSession(async_chat):
    def __init__(self, server, sock):
        async_chat.__init__(self, sock)
        self.server = server
        self.set_terminator(b'EOFEOFEOFEOF')
        self.ibuffer = []
        self.name = None
        self.enter(LoginChannel(server))

    def enter(self, channel):
        try:
            cur = self.channel
        except AttributeError:
            pass
        else:
            cur.remove_session(self)
        self.channel = channel
        channel.add_session(self)
    
    def collect_incoming_data(self, data):
        self.ibuffer.append(data)

    def found_terminator(self):
        buffer = b"".join(self.ibuffer)
        self.ibuffer = []
        line = buffer
        try:
            self.channel.handle(self, line)
        except EndSession:
            self.handle_close()

    def handle_close(self):
        async_chat.handle_close(self)
        self.enter(LogoutChannel(self.server))

class LogoutChannel(Channel):
    def add_session(self, session):
        try:
            del self.server.users[session.name]
        except KeyError:
            pass


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