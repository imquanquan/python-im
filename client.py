#!/usr/bin/env python3.6

import socket   

from frames import *

        

        

            
if __name__ == '__main__':
    app = wx.App()
    # ListFrame(None, -1)
    LoginFrame(None, -1, title = "Login", size = (280, 220))
    app.MainLoop()