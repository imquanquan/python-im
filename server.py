#!/usr/bin/env python3.6

from asyncore import dispatcher
from asynchat import async_chat
import socket, asyncore

class EndSession(Exception):
    pass

class CommandHandler:
    def unknown(self, session, cmd):
        session.push('Unknown command: %s\n'.encode('utf-8') % cmd)

    def handle(self, session, line):
        print(line)
        if not line.strip():
            return
        parts = line.split(' ', 1)
        cmd = parts[0]
        try:
            line = parts[1].strip()
        except IndexError:
            line = ''
        print('do_' + cmd)
        print(getattr(self, 'do_' + cmd, None))
        method = getattr(self, 'do_' + cmd, None)
        try:
            method(session, line)
        except TypeError:
            self.unknown(session, cmd)
            
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
    def add_session(self, session):
        Channel.add_session(self, session)
        session.push(b'Connect Success')
    
    def do_login(self, session, name):
        print(self.server.users)
        name = name.encode('utf-8')
        if not name:
            session.push(b'The name can not be blank')
        elif name in self.server.users:
            session.push(b'The name already exists')
        else:
            session.name = name
            session.enter(self.server.main_channel)


class ListChannel(Channel):
    def add_session(self, session):
        Channel.add_session(self, session)
        session.push(b'Login Success')
        self.server.users[session.name] = session
        
    def do_list_users(self, session, line):
        users = b' '.join(self.server.users.keys())
        session.push(users)
        
        
class LogoutChannel(Channel):
    def add_session(self, session):
        try:
            del self.server.users[session.name]
        except KeyError:
            pass
        

class ChatSession(async_chat):
    def __init__(self, server, sock):
        async_chat.__init__(self, sock)
        self.server = server
        self.set_terminator(b'\n')
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
        line = buffer.decode('utf-8')
        print(line)
        try:
            self.channel.handle(self, line)
        except EndSession:
            self.handle_close()

    def handle_close(self):
        async_chat.handle_close(self)
        self.enter(LogoutChannel(self.server))


class ChatServer(dispatcher):
    def __init__(self, port):
        dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(('', port))
        self.listen(5)
        self.users = {}
        self.main_channel = ListChannel(self)

    def handle_accept(self):
        conn, addr = self.accept()
        ChatSession(self, conn)

if __name__ == '__main__':
    s = ChatServer(6666)
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        print

