#!/usr/bin/env python3.6

from asyncore import dispatcher
from asynchat import async_chat
from threading import Thread
import socket, asyncore


class EndSession(Exception):
    pass


class CommandHandler:
    #def unknown(self, session, cmd):
    #    session.push('Unknown command: %s\n'.encode('utf-8') % cmd)

    def handle(self, session, line):
        if not line.strip():
            return
        parts = line.split(b' ', 1)
        cmd = parts[0].decode("utf-8")
        try:
            line = parts[1].strip()
        except IndexError:
            line = ''
        method = getattr(self, 'do_' + cmd, None)
        #try:
        method(session, line)
        #except TypeError:
        #    self.unknown(session, cmd)
            

class Room(CommandHandler):
    def __init__(self, room_server):
        self.room_server = room_server
        self.sessions = []
    
    def add_session(self, session):
        self.sessions.append(session)
        
    def remove_session(self, session):
        try:
            self.sessions.remove(session)  
        except ValueError:
            pass  
        
    def broadcast(self, line):
        for session in self.sessions:
            session.push(line)    
    
    # def do_logout(self, session, line):
        # raise EndSession 
    

class ChatRoom(Room):
    
    def add_session(self, session):
        Room.add_session(self, session)
        session.push(b'Enter Success')
    
    def do_say(self, session, line):
        self.broadcast(session.name + b': ' + line + b'\n')    
     
    def do_check(self, session, name):
        if name.decode("utf-8") not in self.room_server.users_list:
            session.handle_close()
        else:
            session.name = name
            self.room_server.users[session.name] = session
            session.push(b'Check success')
            
      
class LogoutRoom(Room):
    def add_session(self, session):
        try:
            del self.room_server.users[session.name]
        except KeyError:
            pass    


class RoomSession(async_chat):
    def __init__(self, room_server, sock):
        async_chat.__init__(self, sock)
        self.room_server = room_server
        self.set_terminator(b'\n')
        self.ibuffer = []
        self.name = None
        self.enter(self.room_server.main_room)

    def enter(self, room):
        try:
            cur = self.room
        except AttributeError:
            pass
        else:
            cur.remove_session(self)
        self.room = room
        room.add_session(self)
    
    def collect_incoming_data(self, data):
        self.ibuffer.append(data)

    def found_terminator(self):
        buffer = b"".join(self.ibuffer)
        self.ibuffer = []
        line = buffer
        try:
            self.room.handle(self, line)
        except EndSession:
            self.handle_close()

    def handle_close(self):
        async_chat.handle_close(self)
        # self.enter(Logoutroom(self.server))
        
        
class RoomServer(dispatcher):
    def __init__(self, server, port, users_list):
        dispatcher.__init__(self)
        self.server = server
        self.port = port
        self.users_list = users_list
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(('', port))
        self.listen(5)
        self.main_room = ChatRoom(self)
        self.users = {}     
               
    def handle_accept(self):
        conn, addr = self.accept()       
        RoomSession(self, conn)
    
