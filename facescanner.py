#!/usr/bin/env python

import wx
import cv2
import dlib
from imutils import face_utils
import pprint
import numpy as np
import faceart

class cartoonFace(wx.Frame):
    def __init__(self, parent, capture,  fps=15):
        wx.Frame.__init__(self, parent)

        self.stage = 0

        # configure global variables
        self.cw = 1280
        self.ch =  720
        self.capture = capture
        self.bmp = wx.Bitmap(self.cw,self.ch, depth=16)
        self.detector = False
        self.predictor = False
        self.cannyBottom = 120
        self.cannyTop = 80
        self.faceArt = False
        self.faceFeatures = False
        self.faceDetectFrame = False

        super(cartoonFace, self).__init__(parent,title="Facer", size=(self.cw, self.ch) )

        # Configure the UI

        # confgure the main box
        panel = wx.Panel(self)
        panel.SetBackgroundColour("#4f5049")
        vbox = wx.BoxSizer(wx.VERTICAL)

        # configure the middle part that holds the image
        inside = wx.Panel(panel)
        inside.SetBackgroundColour('#ededed')
        self.staticBitmap = wx.StaticBitmap(inside)

        # add the inside to the vbox with a border of 20 pixels
        vbox.Add(inside, wx.ID_ANY, wx.EXPAND | wx.ALL, 20)
        panel.SetSizer(vbox)

        self.timer = wx.Timer(self)
        self.timer.Start(1000./fps)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_TIMER, self.NextFrame)
        inside.Bind(wx.EVT_KEY_DOWN, self.onKeyPress)
        inside.SetFocus()

    def detectFace(self):
        faceFeatures = []

        # load the detector and predictor if not already loaded (takes a few seconds on the pi)
        if not self.detector:
            print("Loading detector")
            self.detector = dlib.get_frontal_face_detector()
        if not self.predictor:
            print("Loading predictor")
            self.predictor = dlib.shape_predictor("detect-face-parts/shape_predictor_68_face_landmarks.dat")

        # ret, image = self.capture.read()
        gray = cv2.cvtColor(self.faceDetectFrame, cv2.COLOR_BGR2GRAY)
        rects = self.detector(gray,1)

        print("rects found", rects)

        for (i, rect) in enumerate(rects):
            shape = self.predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)
            faceFeatures.append(shape)

        return faceFeatures




    def onKeyPress(self,event):
        keycode = event.GetKeyCode()

        if (ord('Q') == keycode):
            quit()

        if (ord('C') == keycode):
            if self.stage == 0:
                self.stage = 1
            else:
                self.stage = 0
                self.detector = False
                self.predictor = False
                self.cannyBottom = 120
                self.cannyTop = 80
                self.faceArt = False
                self.faceFeatures = False
                self.faceDetectFrame = False

        # up arrow
        if keycode == 315:
            self.faceArt.switchFeatureTypeDown()
        # down arrow
        if keycode == 317:
            self.faceArt.switchFeatureTypeUp()
        # left arrow
        if keycode == 314:
            self.faceArt.switchFeatureDown()
        # right arrow
        if keycode == 316:
            self.faceArt.switchFeatureUp()

        print(self.cannyBottom, self.cannyTop)


        print(event)

    def processImage(self):
        # convert to grayscale
        gray = cv2.cvtColor(self.faceDetectFrame, cv2.COLOR_BGR2GRAY)
        # run Canny on it
        edged = cv2.Canny(gray, self.cannyBottom ,self.cannyTop)
        # convert from white on black  to black on white
        edged = cv2.bitwise_not(edged)
        # convert back to rgb so wxPython can use it correctly
        edged = cv2.cvtColor(edged, cv2.COLOR_GRAY2BGR)

        return edged

    def OnPaint(self, evt):
        dc = wx.BufferedPaintDC(self)
        dc.DrawBitmap(self.bmp, 0, 0)

    def NextFrame(self, event):

        # Stage 0, live video to align your face in the box
        if self.stage == 0:
            ret, frame = self.capture.read()
            # flip the image horizontaly so it doesn't look mirrored
            frame = cv2.flip( frame, 1 )
            self.faceDetectFrame = frame

            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.bmp.CopyFromBuffer(frame)
                buffer = wx.Bitmap(self.cw,self.ch)
                dc = wx.MemoryDC(buffer)
                dc.DrawBitmap(self.bmp, 0,0)
                dc.SetPen(wx.Pen("blue", width=10))
                dc.SetBrush(wx.Brush("blue", wx.TRANSPARENT))
                dc.DrawRectangle(self.cw/3 ,20 , self.cw/3 ,self.ch-60)

                #self.staticBitmap.SetBitmap(self.bmp)
                self.staticBitmap.SetBitmap(buffer)

        # Stage 1, process the image
        elif self.stage == 1:
            # display loading image tag
            print("stage 1")
            if not self.faceArt:
                print("Loading Face art")
                self.faceArt = faceart.faceArt()

            print("Detecting Facial Features")
            self.faceFeatures = self.detectFace()

            self.bmp.CopyFromBuffer(self.processImage())
            self.stage = 2

        # Stage 2, show the final image
        elif self.stage == 2:

            eyeR1   = self.faceFeatures[0][43][0]
            eyeR1y  = self.faceFeatures[0][44][1]
            eyeR2   = self.faceFeatures[0][46][0]
            eyeRC   = self.faceFeatures[0][48][0]

            eyeL1   = self.faceFeatures[0][37][0]
            eyeL1y  = self.faceFeatures[0][38][1]
            eyeL2   = self.faceFeatures[0][40][0]
            eyeLC   = self.faceFeatures[0][42][0]

            mouthL  = self.faceFeatures[0][49][0]
            mouthLy = self.faceFeatures[0][51][1]
            mouthR  = self.faceFeatures[0][55][0]
            mouthC  = self.faceFeatures[0][67][0]

            buffer = wx.Bitmap(self.cw, self.ch)
            dc     = wx.MemoryDC(buffer)
            dc.Clear()
            dc.DrawBitmap( self.bmp, 0,0 )

            rwidth = (eyeR2-eyeR1)*3.5
            lwidth = (eyeL2-eyeL1)*3.5
            mwidth = (mouthR-mouthL)*1.8

            dc.DrawBitmap( self.faceArt.bitmap( self.faceArt.eyesR[self.faceArt.currentEyes], w=rwidth) , eyeRC - (rwidth /2) -10  ,eyeR1y-25, True)
            dc.DrawBitmap( self.faceArt.bitmap( self.faceArt.eyesL[self.faceArt.currentEyes], w=lwidth) , eyeLC - (lwidth /2) +10  ,eyeR1y-25, True)

            dc.DrawBitmap( self.faceArt.bitmap( self.faceArt.mouths[self.faceArt.currentMouth],
                                                w=mwidth),
                                                mouthC - ( mwidth /2) +10 ,
                                                mouthLy+4,
                                                True)


            self.staticBitmap.SetBitmap(buffer)

        self.Refresh()

capture = cv2.VideoCapture(0)
capture.set(3, 1280)
capture.set(4, 720)

app = wx.App()
cap = cartoonFace(None, capture)
cap.Show()
app.MainLoop()
