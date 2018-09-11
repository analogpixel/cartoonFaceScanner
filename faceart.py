#!/usr/bin/env python

import wx

class faceArt:
    def __init__(self):
        self.imgPath = "./resources/3x/"

        self.eyesR  =[]
        self.eyesL  =[]
        self.maxEyes = 12
        self.maxMouth = 9
        self.maxNose = 5

        self.currentEyes = 0
        self.currentMouth = 0
        self.currentNose = 0
        self.featureType = 0
        self.featureList = ['eyes','mouths', 'nose']


        print("Loading eyes")
        for i in range(1,self.maxEyes+1):
            self.eyesR.append( self.loadImage(self.imgPath + "eye" + str(i) + "_R@3x.png" ) )
            self.eyesL.append( self.loadImage(self.imgPath + "eye" + str(i) + "_L@3x.png" ) )

        print("Loading Mouths")
        self.mouths = []
        for i in range(1,self.maxMouth + 1):
            self.mouths.append( self.loadImage(self.imgPath + "mouth" + str(i) + "@3x.png" ) )

        print("Loading Noses")
        self.noses = []
        for i in range(1, self.maxNose + 1):
            self.noses.append( self.loadImage( self.imgPath + "nose" + str(i) + "@3x.png") )

    def loadImage(self, filename):
        image = wx.Image(filename, type=wx.BITMAP_TYPE_PNG)
        return image

    def bitmap(self, image, **kwargs):
        if 'w' in kwargs:
            size = image.GetSize()
            wscale = kwargs['w'] / size.width
            image = image.Scale(size.width * wscale, size.height * wscale, wx.IMAGE_QUALITY_HIGH)

        return image.ConvertToBitmap()

    def switchFeatureTypeUp(self):
        self.featureType += 1
        if self.featureType > len(self.featureList)-1:
            self.featureType = 0

    def switchFeatureTypeDown(self):
        self.featureType -= 1
        if self.featureType < 0:
            self.featureType = len(self.featureList)-1

    def switchFeatureUp(self):
        if self.featureType == 0:
            self.currentEyes +=1
            if self.currentEyes >= self.maxEyes:
                self.currentEyes = 0
        elif self.featureType == 1:
            self.currentMouth +=1
            if self.currentMouth >= self.maxMouth:
                self.currentMouth = 0
        elif self.featureType == 2:
            self.currentNose +=1
            if self.currentNose >= self.maxNose:
                self.currentNose = 0

    def switchFeatureDown(self):
        if self.featureType == 0:
            self.currentEyes -=1
            if self.currentEyes <  0:
                self.currentEyes = self.maxEyes -1
        elif self.featureType == 1:
            self.currentMouth -=1
            if self.currentMouth < 0:
                self.currentMouth = self.maxMouth -1
        elif self.featureType == 2:
            self.currentNose -=1
            if self.currentNose < 0:
                self.currentNose = self.maxNose -1
