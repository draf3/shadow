import sys
sys.path.append('Library')

import numpy as np
import argparse
import time
import SpoutSDK
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GL.framebufferobjects import *
from OpenGL.GLU import *

class SPOUT:
    def __init__(self):
        self.width = 256
        self.height = 256
        self.display = (self.width, self.height)

        self.senderName = 'output'
        self.silent = True

        # window setup
        pygame.init()
        pygame.display.set_caption(self.senderName)
        pygame.display.set_mode(self.display, DOUBLEBUF | OPENGL)

        # OpenGL init
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.width, self.height, 0, 1, -1)
        glMatrixMode(GL_MODELVIEW)
        glDisable(GL_DEPTH_TEST)
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glEnable(GL_TEXTURE_2D)

        # init spout sender
        self.spoutSender = SpoutSDK.SpoutSender()
        self.spoutSenderWidth = self.width
        self.spoutSenderHeight = self.height
        # Its signature in c++ looks like this: bool CreateSender(const char *Sendername, unsigned int width, unsigned int height, DWORD dwFormat = 0);
        self.spoutSender.CreateSender(self.senderName, self.spoutSenderWidth, self.spoutSenderHeight, 0)

        # create textures for spout receiver and spout sender
        self.textureSendID = glGenTextures(1)

    def pipeline(self, data):
        # print(data.shape)
        output = data
        return output

    def render(self, img):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # call our main function
        output = self.pipeline(img)

        # setup the texture so we can load the output into it
        glBindTexture(GL_TEXTURE_2D, self.textureSendID);
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        # copy output into texture
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.width, self.height, 0, GL_RGB, GL_UNSIGNED_BYTE, output)

        # setup window to draw to screen
        glActiveTexture(GL_TEXTURE0)
        # clean start
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # reset drawing perspective
        glLoadIdentity()
        # draw texture on screen
        glBegin(GL_QUADS)

        glTexCoord(0, 0)
        glVertex2f(0, 0)

        glTexCoord(1, 0)
        glVertex2f(self.width, 0)

        glTexCoord(1, 1)
        glVertex2f(self.width, self.height)

        glTexCoord(0, 1)
        glVertex2f(0, self.height)

        glEnd()

        if self.silent:
            pygame.display.iconify()

        # update window
        pygame.display.flip()

        # Send texture to spout...
        # Its signature in C++ looks like this: bool SendTexture(GLuint TextureID, GLuint TextureTarget, unsigned int width, unsigned int height, bool bInvert=true, GLuint HostFBO = 0);
        if sys.version_info[1] == 5:
            self.spoutSender.SendTexture(self.textureSendID, GL_TEXTURE_2D, self.spoutSenderWidth, self.spoutSenderHeight, False, 0)
        else:
            self.spoutSender.SendTexture(self.textureSendID.item(), GL_TEXTURE_2D, self.spoutSenderWidth, self.spoutSenderHeight, False, 0)
