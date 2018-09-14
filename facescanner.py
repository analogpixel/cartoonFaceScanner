#!/usr/bin/env python

import wx
import cv2
import dlib
from imutils import face_utils
import pprint
import numpy as np
import faceart
import os
import subprocess
import time

## password for pi is pi!

try:
  import RPi.GPIO as GPIO
  PI = True
  gw=800
  gh=600
except:
  print("not a pi")
  PI = False
  gw=1280
  gh=720

class cartoonFace(wx.Frame):
    def __init__(self, parent, capture,  w=800, h=600, fps=15):
        wx.Frame.__init__(self, parent)

        self.stage = 0
        self.debounce = 0
        self.damt = 5   # wait this many cycles before allowing input again
        self.cw = w # width of camera and display
        self.ch = h # heigh of camera and display
        self.capture = capture
        self.bmp = wx.Bitmap(self.cw,self.ch, depth=16)
        self.detector = False
        self.predictor = False
        self.cannyBottom = 110
        self.cannyTop = 80
        self.faceArt = False
        self.faceFeatures = False
        self.faceDetectFrame = False
        self.toPrint = False
        self.loadingImage = wx.Image("resources/loading.png", type=wx.BITMAP_TYPE_PNG).ConvertToBitmap()

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
        self.Bind(wx.EVT_TIMER, self.NextFrame, self.timer)

        # If we are on a PI, configure the buttons to do stuff
        if PI:
            GPIO.setmode (GPIO.BCM)
            GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            self.piTimer = wx.Timer(self)
            self.piTimer.Start(100)
            self.Bind(wx.EVT_TIMER, self.checkPI, self.piTimer)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        inside.Bind(wx.EVT_KEY_DOWN, self.onKeyPress)
        inside.SetFocus()

    def timerEvent(self, event):
        print(event.GetEventObject() )

        if event.GetEventObject() == self.timer:
            self.NextFrame()
        if event.GetEventObject() == self.piTimer:
            self.checkPI()



    def printImage(self):
        # check if we are already printing
        result = subprocess.run(['/usr/bin/lpstat', '-o'], stdout=subprocess.PIPE).stdout
        if len(result) > 1:
          print("Already printing")
          return

        # then print
        self.toPrint.SaveFile("toprint.png", wx.BITMAP_TYPE_PNG)
        os.system("lp toprint.png")

    def checkPI(self,event):
        if self.debounce > 0:
           self.debounce -= 1
           return

        # up pressed
        if ( not GPIO.input(12) ):
            time.sleep(.01)
            self.debounce = self.damt
            self.faceArt.switchFeatureTypeDown()
            self.toPrint = False

        # down pressed
        if ( not GPIO.input(16) ):
            time.sleep(.01)
            self.debounce = self.damt
            self.faceArt.switchFeatureTypeUp()
            self.toPrint = False

        # left pressed
        if ( not GPIO.input(13)):
            time.sleep(.01)
            self.debounce = self.damt
            self.faceArt.switchFeatureDown()
            self.toPrint = False

        # right pressed
        if (not GPIO.input(17)):
            time.sleep(.01)
            self.debounce = self.damt
            self.faceArt.switchFeatureUp()
            self.toPrint = False


        # red Button pressed
        # print
        if (not GPIO.input(6)):
            time.sleep(.01)
            self.debounce = self.damt
            # if we are in the correct statge, and not already printing something
            if self.stage == 2:
                self.printImage();

        # black button pressed
        # capture and switch modes
        if ( not GPIO.input(5)) and (self.stage !=1):
            time.sleep(.01)
            self.debounce = self.damt
            print("button pressed")
            if self.stage == 0:
                self.stage = 1
                self.staticBitmap.SetBitmap(self.loadingImage)
            else:
                self.stage = 0
                self.detector = False
                self.predictor = False
                self.cannyBottom = 120
                self.cannyTop = 80
                self.faceArt = False
                self.faceFeatures = False
                self.faceDetectFrame = False


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
        
        self.toPrint = False
        return faceFeatures




    def onKeyPress(self,event):
        keycode = event.GetKeyCode()

        if (ord('Q') == keycode):
            quit()

        if (ord('C') == keycode):
            if self.stage == 0:
                self.stage = 3
            else:
                self.stage = 0
                self.detector = False
                self.predictor = False
                self.cannyBottom = 120
                self.cannyTop = 80
                self.faceArt = False
                self.faceFeatures = False
                self.faceDetectFrame = False

        if ( ord('P') == keycode):
            if self.stage == 2:
                self.printImage();

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

        # force an image refresh
        self.toPrint = False

        #print(self.cannyBottom, self.cannyTop)
        #print(event)

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
                dc.DrawRectangle(self.cw/3 ,20 , self.cw/3 ,self.ch-100)

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

            if  len(self.faceFeatures) == 0:
                print("No features found")
                self.stage = 0
            else:
                self.bmp.CopyFromBuffer(self.processImage())
                self.stage = 2

        # Stage 2, show the final image
        elif self.stage == 2:

            if not self.toPrint:
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

                noseX = self.faceFeatures[0][28][0]
                noseYTop = self.faceFeatures[0][28][1]
                noseYBottom = self.faceFeatures[0][34][1]
                noseWidth = (self.faceFeatures[0][32][0] - self.faceFeatures[0][36][0]) * 1


                self.toPrint = wx.Bitmap(self.cw, self.ch)
                dc     = wx.MemoryDC(self.toPrint)
                dc.Clear()
                dc.DrawBitmap( self.bmp, 0,0 )

                rwidth = (eyeR2-eyeR1)*4
                lwidth = (eyeL2-eyeL1)*4
                mwidth = (mouthR-mouthL)*2.2

                dc.DrawBitmap( self.faceArt.bitmap( self.faceArt.noses[self.faceArt.currentNose], w=noseWidth), noseX-(noseWidth/2), (noseYTop+noseYBottom)/2 , True)
                dc.DrawBitmap( self.faceArt.bitmap( self.faceArt.eyesR[self.faceArt.currentEyes], w=rwidth) , eyeRC - (rwidth /2) -10  ,eyeR1y-15, True)
                dc.DrawBitmap( self.faceArt.bitmap( self.faceArt.eyesL[self.faceArt.currentEyes], w=rwidth) , eyeLC - (lwidth /2) +10  ,eyeR1y-15, True)

                dc.DrawBitmap( self.faceArt.bitmap( self.faceArt.mouths[self.faceArt.currentMouth],
                                                    w=mwidth),
                                                    mouthC - ( mwidth /2) +1 ,
                                                    mouthLy+4,
                                                    True)

            else:
                self.overlay = wx.Bitmap(self.cw, self.ch)
                dc = wx.MemoryDC(self.overlay)
                dc.SetBrush(wx.Brush("white", wx.SOLID))
                font = wx.Font(30, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
                dc.SetFont(font)
                dc.DrawBitmap( self.toPrint,0,0)
                dc.DrawRectangle( 0,0, self.cw, 60)
                dc.DrawText( "Change the " + self.faceArt.featureList[self.faceArt.featureType] , 10,10)
                self.staticBitmap.SetBitmap(self.overlay)
        elif self.stage == 3:
            self.staticBitmap.SetBitmap(self.loadingImage)
            self.stage = 1

        self.Refresh()

capture = cv2.VideoCapture(0)
#capture.set(3, 1280)
#capture.set(4, 720)

capture.set(3,gw)
capture.set(4,gh)

app = wx.App()
cap = cartoonFace(None, capture, gw,gh)
cap.Show()
app.MainLoop()
