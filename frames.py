#!/usr/bin/env python3.6

import gettext
import telnetlib
from threading import Thread
from time import sleep

from wx.lib.pubsub import setupkwargs
from wx.lib.pubsub import pub

import wx

CON = telnetlib.Telnet()

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
            ListFrame(None, -1, user_name)
                

    def showDialog(self, content, size):
        dialog = wx.Dialog(self, title = '出错啦♪(^∇^*)', size = size)
        dialog.Center()
        wx.StaticText(dialog, label = content)
        dialog.ShowModal()


class ListFrame(wx.Frame):
    # list online user frame
    def __init__(self, parent, id, user_name):
        wx.Frame.__init__(self, parent, id)
        self.count_label = wx.StaticText(self, wx.ID_ANY, "在线用户：")
        self.users = {}
        
        self.__set_properties()
        self.__do_layout()
        pub.subscribe(self.list_users, "LIST_USERS")
        
        receive_thread = Thread(target=receive_users_list_thread)
        receive_thread.start()
        
        self.Center()    
        self.Show()    
            
    def __set_properties(self):
        self.SetTitle("小小聊天软件~\(≧▽≦)/~啦啦啦")
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
            self.users[user] = wx.StaticText(self, wx.ID_ANY, user), wx.Button(self, wx.ID_ANY, "与ta聊天")
            self.users[user][0].SetMinSize((150, 40))
            self.users[user][0].SetFont(wx.Font(20, wx.MODERN, wx.NORMAL, wx.NORMAL, 0, "Noto Sans CJK SC"))
            self.users[user][1].SetMinSize((120, 40))
            self.users[user][1].SetFont(wx.Font(20, wx.MODERN, wx.NORMAL, wx.NORMAL, 0, "Sans"))
            self.count_sizer.Add(self.users[user][0])
            self.count_sizer.Add(self.users[user][1])
  
        for user in del_users:
            self.count_sizer.Detach(self.users[user][0])
            self.count_sizer.Detach(self.users[user][1])
            self.users[user][1].Destroy()
            self.users[user][0].Destroy()
            del self.users[user]
            
        self.Layout()           
    
    def receive(self):
        while True:
            result = CON.read_some()
            print(result)
            sleep(0.6)


def receive_users_list_thread():
    pre_users = []
    while 1:
        CON.write(b'list_users\n')
        users = CON.read_some().decode("utf-8").split(' ')
        wx.CallAfter(pub.sendMessage, "LIST_USERS", users_list = users, pre_users_list = pre_users)
        pre_users = users[:]
        sleep(0.5)        
        
    

