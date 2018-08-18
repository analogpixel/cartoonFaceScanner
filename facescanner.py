#!/usr/bin/env python

import wx
import cv2

class ShowCapture(wx.Panel):
    def __init__(self, parent, capture, fps=15):
        wx.Panel.__init__(self, parent)
        self.cw = 1280
        self.ch =  720
        self.capture = capture
        self.bmp = False

        # set the window size
        parent.SetSize((self.cw, self.ch))
        self.bmp = wx.Bitmap(self.cw, self.ch)

        self.timer = wx.Timer(self)
        self.timer.Start(1000./fps)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_TIMER, self.NextFrame)
        self.Bind(wx.EVT_KEY_DOWN, self.onKeyPress)

    def onKeyPress(self,event):
        print(event)

    def OnPaint(self, evt):
        dc = wx.BufferedPaintDC(self)
        dc.DrawBitmap(self.bmp, 0, 0)

    def NextFrame(self, event):
        ret, frame = self.capture.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.bmp.CopyFromBuffer(frame)
            self.Refresh()


capture = cv2.VideoCapture(0)
capture.set(3, 1280)
capture.set(4, 720)

app = wx.App()
frame = wx.Frame(None)
cap = ShowCapture(frame, capture)
frame.Show()
app.MainLoop()
