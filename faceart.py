#!/usr/bin/env python

import wx

class faceArt:
    def __init__(self):
        self.imgPath = "./resources/3x/"

        self.eyesR  =[]
        self.eyesL  =[]
        self.maxEyes = 12
        self.maxMouth = 9

        print("Loading eyes")
        for i in range(1,self.maxEyes+1):
            self.eyesR.append( self.loadImage(self.imgPath + "eye" + str(i) + "_R@3x.png" ) )
            self.eyesL.append( self.loadImage(self.imgPath + "eye" + str(i) + "_L@3x.png" ) )

        print("Loading Mouths")
        self.mouths = []
        for i in range(1,self.maxMouth + 1):
            self.mouths.append( self.loadImage(self.imgPath + "mouth" + str(i) + "@3x.png" ) )

    def loadImage(self, filename):
        image = wx.Image(filename, type=wx.BITMAP_TYPE_PNG)
        return image

    def bitmap(self, image, **kwargs):
        if 'w' in kwargs:
            size = image.GetSize()
            wscale = kwargs['w'] / size.width
            image = image.Scale(size.width * wscale, size.height * wscale, wx.IMAGE_QUALITY_HIGH)

        return image.ConvertToBitmap()
