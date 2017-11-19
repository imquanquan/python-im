#!/usr/bin/env python3.6

import wx
import gettext


class ListFrame(wx.Frame):
    # list online user frame
    def __init__(self, *args, **kwds):
        wx.Frame.__init__(self, *args, **kwds)
        self.count_label = wx.StaticText(self, wx.ID_ANY, "在线人数：")
        self.my_name_label = wx.StaticText(self, wx.ID_ANY, "label_1")
        self.exit_button = wx.Button(self, wx.ID_ANY, "退出吧")

        self.__set_properties()
        self.__do_layout()
        self.Center()        
        self.Show()


    def __set_properties(self):
        self.SetTitle("小小聊天软件~\(≧▽≦)/~啦啦啦")
        self.SetSize((300, 450))
        self.count_label.SetMinSize((300, 50))
        self.count_label.SetFont(wx.Font(20, wx.MODERN, wx.NORMAL, wx.BOLD, 0, "Sans"))
        self.my_name_label.SetMinSize((150, 40))
        self.my_name_label.SetFont(wx.Font(20, wx.MODERN, wx.NORMAL, wx.NORMAL, 0, "Noto Sans CJK SC"))
        self.exit_button.SetMinSize((100, 40))
        self.exit_button.SetFont(wx.Font(20, wx.MODERN, wx.NORMAL, wx.NORMAL, 0, "Sans"))

    def __do_layout(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        count_sizer = wx.GridSizer(5, 2, 10, 50)
        main_sizer.Add(self.count_label, 0, wx.LEFT, 0)
        count_sizer.Add(self.my_name_label, 0, 0, 0)
        count_sizer.Add(self.exit_button, 0, 0, 0)
        main_sizer.Add(count_sizer, 1, 0, 0)
        self.SetSizer(main_sizer)
        self.Layout()
