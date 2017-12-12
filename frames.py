#!/usr/bin/env python3.6

import gettext
import telnetlib
from threading import Thread
from time import sleep

from wx.lib.pubsub import setupkwargs
from wx.lib.pubsub import pub

import wx


CON = telnetlib.Telnet()


def receive_users_list_thread():
    pre_users = []
    while 1:
        CON.write(b'list_users\n')
        users = CON.read_some().decode("utf-8").split(' ')
        wx.CallAfter(pub.sendMessage, "LIST_USERS", users_list = users, pre_users_list = pre_users)
        pre_users = users[:]
        sleep(100)        
        
class ChatButton(wx.Button):
    def __init__(self, parent, id, Label, user):
        wx.Button.__init__(self, parent, id, Label)
        self.owner = user


class LoginFrame(wx.Frame):
    # login frame
    def __init__(self, parent, id, title, size):
        wx.Frame.__init__(self, parent, id, title)
        self.server_address_label = wx.StaticText(self, label = "Server Address", pos = (10, 50), size = (120, 25))
        self.user_name_label = wx.StaticText(self, label = "UserName", pos = (40, 100), size = (120, 25))
        self.server_address = wx.TextCtrl(self, pos = (120, 47), size = (150, 25), value="127.0.0.1:6666")
        self.user_name_text = wx.TextCtrl(self, pos = (120, 97), size = (150, 25), value="a")
        self.login_button = wx.Button(self, label = 'Login', pos = (80, 145), size = (130, 30))
        self.login_button.Bind(wx.EVT_BUTTON, self.login)
        
        self.SetSize(size)
        self.Center()        
        self.Show()

    def login(self, event):
        server_address = self.server_address.GetLineText(0).split(':')
        user_name = str(self.user_name_text.GetLineText(0))
            
        CON.open(server_address[0], port = int(server_address[1]), timeout = 10)
        response = CON.read_some()
        if response != b'Connect Success':
            self.showDialog('Connect Fail!', (135, 50))
            return
            
        mess = 'login ' + user_name + '\n'
        CON.write(mess.encode('utf-8'))
        response = CON.read_some()
        if response == b'The name can not be blank':
            self.showDialog('名字不能为空哦', (175, 50))
        elif response == b'The name already exists':
            self.showDialog('名字被人用啦', (175, 50))
        elif response == b'Login Success':
            self.Close()
            ListFrame(None, -1, user_name, server_address)
                

    def showDialog(self, content, size):
        dialog = wx.Dialog(self, title = '出错啦♪(^∇^*)', size = size)
        dialog.Center()
        wx.StaticText(dialog, label = content)
        dialog.ShowModal()


class ListFrame(wx.Frame):
    # list online user frame
    def __init__(self, parent, id, user_name, server_address):
        wx.Frame.__init__(self, parent, id)
        self.count_label = wx.StaticText(self, wx.ID_ANY, "在线用户：")
        self.owner = user_name
        self.user_name = user_name
        self.users = {}
        self.cons = {}
        self.server_address = server_address
        
        self.__set_properties()
        self.__do_layout()
        pub.subscribe(self.list_users, "LIST_USERS")
        
        receive_thread = Thread(target=receive_users_list_thread)
        receive_thread.start()
        
        self.Center()    
        self.Show()    
            
    def __set_properties(self):
        self.SetTitle(self.user_name + "  小小聊天软件~\(≧▽≦)/~啦啦啦")
        self.SetSize((300, 450))
        self.count_label.SetMinSize((300, 50))
        self.count_label.SetFont(wx.Font(20, wx.MODERN, wx.NORMAL, wx.BOLD, 0, "Sans"))

    def __do_layout(self):
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.count_sizer = wx.GridSizer(5, 2, 10, 50)
        self.main_sizer.Add(self.count_label, 0, wx.LEFT, 0)
        
        self.main_sizer.Add(self.count_sizer, 1, 0, 0)
        self.SetSizer(self.main_sizer)
        self.Layout()
    
    def list_users(self, users_list, pre_users_list):
        add_users = set(users_list).difference(pre_users_list)
        del_users = set(pre_users_list).difference(users_list)

        for user in add_users:
            
            self.users[user] = wx.StaticText(self, wx.ID_ANY, user), ChatButton(self, wx.ID_ANY, "与ta聊天", user)
            self.users[user][0].SetMinSize((150, 40))
            self.users[user][0].SetFont(wx.Font(20, wx.MODERN, wx.NORMAL, wx.NORMAL, 0, "Noto Sans CJK SC"))
            self.users[user][1].SetMinSize((120, 40))
            self.users[user][1].SetFont(wx.Font(20, wx.MODERN, wx.NORMAL, wx.NORMAL, 0, "Sans"))    
            self.users[user][1].Bind(wx.EVT_BUTTON, lambda evt, one=self.owner, two=user : self.chat(evt, one, two))
            self.count_sizer.Add(self.users[user][0])
            self.count_sizer.Add(self.users[user][1])
  
        for user in del_users:
            self.count_sizer.Detach(self.users[user][0])
            self.count_sizer.Detach(self.users[user][1])
            self.users[user][1].Destroy()
            self.users[user][0].Destroy()
            del self.users[user]
            
        self.Layout()           
    
    def chat(self, evt, one, two):
        mess = 'chat %s %s\n' % (one, two)
        CON.write(mess.encode('utf-8'))
        response = CON.read_some()
        self.cons[two] = telnetlib.Telnet()
        self.cons[two].open(self.server_address[0], port = int(response.decode("utf-8")), timeout = 10)
        print(int(response.decode("utf-8")))
        response = self.cons[two].read_some()
        
        if response == b'Enter Success':
            self.cons[two].write(b'check %s\n' % self.owner.encode("utf-8"))
            response = self.cons[two].read_some()
            if response == b'Check success':
                ChatFrame(self, wx.ID_ANY, "Chat with %s" % two, self.cons[two], two)
    
    def receive(self):
        while True:
            result = CON.read_some()
            print(result)
            sleep(0.6)


class ChatFrame(wx.Frame):
    def __init__(self, parent, id, title, con, other):
        wx.Frame.__init__(self, parent, id, title)
        self.message_text_ctrl = wx.TextCtrl(self, wx.ID_ANY, "", style = wx.TE_MULTILINE | wx.TE_READONLY)
        self.sen_text_ctrl = wx.TextCtrl(self, wx.ID_ANY, "", style = wx.TE_MULTILINE)
        self.send_button = wx.Button(self, wx.ID_ANY, "发送信息")
        self.mess_button = wx.Button(self, wx.ID_ANY, "聊天记录")
        self.file_button = wx.Button(self, wx.ID_ANY, "传送文件")
        
        self.send_button.Bind(wx.EVT_BUTTON, self.send)
        self.mess_button.Bind(wx.EVT_BUTTON, self.logs)
        
        self.con = con
        self.other = other
        
        self.receive_thread = Thread(target=self.receive)
        self.receive_thread.start()
        
        self.__set_properties()
        self.__do_layout()
        self.Show()
        # self.receive()

    def __set_properties(self):
        self.SetSize((800, 530))
        self.message_text_ctrl.SetMinSize((800, 300))
        self.sen_text_ctrl.SetMinSize((800, 150))
        self.send_button.SetMinSize((200, 45))
        self.send_button.SetFont(wx.Font(20, wx.MODERN, wx.NORMAL, wx.BOLD, 0, "Noto Sans CJK SC"))
        self.mess_button.SetMinSize((200, 45))
        self.mess_button.SetFont(wx.Font(20, wx.MODERN, wx.NORMAL, wx.BOLD, 0, "Noto Sans CJK SC"))
        self.file_button.SetMinSize((200, 45))
        self.file_button.SetFont(wx.Font(20, wx.MODERN, wx.NORMAL, wx.BOLD, 0, "Noto Sans CJK SC"))
        self.message_text_ctrl.SetFont(wx.Font(16, wx.MODERN, wx.NORMAL, wx.BOLD, 0, "Noto Sans CJK SC"))
        self.sen_text_ctrl.SetFont(wx.Font(20, wx.MODERN, wx.NORMAL, wx.BOLD, 0, "Noto Sans CJK SC"))

    def __do_layout(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        buttoms_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(self.message_text_ctrl, 0, 0, 0)
        main_sizer.Add(self.sen_text_ctrl, 0, 0, 0)
        buttoms_sizer.Add(self.send_button, 0, 0, 0)
        buttoms_sizer.Add(self.mess_button, 0, 0, 0)
        buttoms_sizer.Add(self.file_button, 0, 0, 0)
        main_sizer.Add(buttoms_sizer, 1, 0, 0)
        self.SetSizer(main_sizer)
        self.Layout()
    
    def send(self, event):
        message = 'say ' + str(self.sen_text_ctrl.GetLineText(0)).strip() + '\n'
        if message:
            self.con.write(message.encode("utf-8"))
            self.sen_text_ctrl.Clear()
    
    def logs(self, event):
        self.con.write(b'logs\n')
        response = self.con.read_some()
        LogsFrame(self, wx.ID_ANY, "chat logs with %s" % self.other, response)
            
    def receive(self):
        while True:
            sleep(0.6)
            result = self.con.read_very_eager()
            if result != b'':
                print(result.decode("utf-8"))
                self.message_text_ctrl.AppendText(result)
                

class LogsFrame(wx.Frame):
    def __init__(self, parent, id, title, logs):
        wx.Frame.__init__(self, parent, id, title)
        self.logs_text_ctrl = wx.TextCtrl(self, wx.ID_ANY, "", style = wx.TE_MULTILINE | wx.TE_READONLY)
        self.logs_text_ctrl.SetFont(wx.Font(16, wx.MODERN, wx.NORMAL, wx.BOLD, 0, "Noto Sans CJK SC"))
        self.logs_text_ctrl.AppendText(logs.decode("utf-8"))
        self.logs_text_ctrl.SetMinSize((800, 530))
        self.SetSize((800, 530))
        self.Show()