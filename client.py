#!/usr/bin/env python3.6

import telnetlib

import wx

from frames import *

        
class ChatFrame(wx.Frame):
    def __init__(self, parent, id, title, size):
        wx.Frame.__init__(self, parent, id, title)
        self.SetSize(size)
        self.Center()
        self.chatFrame = wx.TextCtrl(self, pos = (5, 5), size = (490, 310), style = wx.TE_MULTILINE | wx.TE_READONLY)
        self.message = wx.TextCtrl(self, pos = (5, 320), size = (300, 25))
        self.Show()
        

            
if __name__ == '__main__':
    app = wx.App()
    # ListFrame(None, -1)
    LoginFrame(None, -1, title = "Login", size = (280, 220))
    app.MainLoop()