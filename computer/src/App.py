#!/usr/bin/env python3

import socket
import time
import sys

import pygame
from pygame.locals import *

from conf import *


class App(object):
    def __init__(self):
        self.initPyGame()
        self.borderSize = 10
        self.throttle = 9
        self.IP = self.getIP()

    def run(self):
        deltaTime = 0.05
        startTime = endTime = time.time()
        continueFlag = True
        while continueFlag:
            if (endTime - startTime > deltaTime):
                self.message = ["0", "0", str(self.throttle), "0", "0", "0"]
                startTime = time.time()
                self.getKeys()
                self.displayWindow()
                self.sendCommands()
                #self.receiveVideo()
                for event in pygame.event.get():
                    if event.type == QUIT:
                        continueFlag = False
            endTime = time.time()
        self.terminate()

    def getKeys(self):
        keys = pygame.key.get_pressed()
        if keys[K_UP]:
            self.message[0] = "1"
        elif keys[K_DOWN]:
            self.message[0] = "2"
        if keys[K_LEFT]:
            self.message[1] = "1"
        elif keys[K_RIGHT]:
            self.message[1] = "2"
        #w(-) AND x(+) for throttle value
        if keys[K_w] and self.throttle > 0:
            self.throttle -= 1
            self.message[2] = str(self.throttle)
        elif keys[K_x] and self.throttle < 9:
            self.throttle += 1
            self.message[2] = str(self.throttle)

    def sendCommands(self):
        if not hasattr(self, 'socketTCP'):
            return
        self.socketTCP.send("".join(self.message).encode())

    def receiveVideo(self):
        #frame = []
        data, addr = self.socketUDP.recvfrom(62210)
        print("----->: ", len(data), data[0:5])
        #frame.append(data)
        #print((len(data)))

    def getIP(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]

    def initTCPConnection(self):
        self.socketTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socketTCP.connect((IP, TCP_PORT))
        print(T_COLOR_GREEN + "Connected with TCP on:\t", IP + ":" + str(self.socketTCP.getsockname()[1]) + T_COLOR_RESET)
        self.message = self.IP + ":" + str(self.socketUDP.getsockname()[1]) + "*"
        self.sendCommands()
        print("UDP config message sent")

    def initUDPConnection(self):
        self.socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socketUDP.bind((self.IP, 0))
        #self.socketUDP.setblocking(0)
        print(T_COLOR_GREEN + "Listening with UDP on:\t", str(self.socketUDP.getsockname()[0]) + ":" + str(self.socketUDP.getsockname()[1]) + T_COLOR_RESET)

    def terminate(self):
        if hasattr(self, 's'):
            self.socketTCP.close()
        pygame.quit()
        sys.exit()

############################################
# GRAPHICS
############################################

    def initPyGame(self):
        pygame.init()
        self.display = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Tank control center')
        self.assets = {}
        self.assets["ArrowUp"] = pygame.image.load("../rsc/img/ArrowUp.bmp")
        self.assets["ArrowNone"] = pygame.image.load("../rsc/img/ArrowNone.bmp")
        #RESIZE HALF-SIZE
        self.assets["ArrowUp"] = pygame.transform.scale(self.assets["ArrowUp"], (self.assets["ArrowUp"].get_rect()[2] // 2, self.assets["ArrowUp"].get_rect()[3] // 2))
        self.assets["ArrowNone"] = pygame.transform.scale(self.assets["ArrowNone"], (self.assets["ArrowNone"].get_rect()[2] // 2, self.assets["ArrowNone"].get_rect()[3] // 2))
        #ROTATE FOR DOWN ARROW
        self.assets["ArrowDown"] = pygame.transform.rotate(self.assets["ArrowUp"], 180)
        self.computeTirePositions()
        self.assets["Pixel_M"] = pygame.font.Font('../rsc/typos/Pixel.ttf', 40)
        self.assets["text_w"] = self.assets["Pixel_M"].render('W', False, COLOR_BLACK)
        self.assets["text_x"] = self.assets["Pixel_M"].render('X', False, COLOR_BLACK)
        # self.assets["ArrowLeft"] = pygame.transform.rotate(self.assets["ArrowUp"], 90)
        # self.assets["ArrowRight"] = pygame.transform.rotate(self.assets["ArrowUp"], -90)

    def displayWindow(self):
        self.display.fill(COLOR_BLACK)
        pygame.draw.rect(self.display, COLOR_WHITE, (self.borderSize, self.borderSize, WINDOW_WIDTH - self.borderSize * 2, WINDOW_HEIGHT - self.borderSize * 2))
        self.drawTires()
        self.drawThrottle()
        pygame.display.update()

    def drawThrottle(self):
        self.display.blit(self.assets["text_x"], (37, (WINDOW_HEIGHT // 4) - self.borderSize))
        self.display.blit(self.assets["text_w"], (37, (WINDOW_HEIGHT // 4) + 37 - self.borderSize + (WINDOW_HEIGHT // 2) - 27 + self.borderSize * 2))
        self.display.blit(self.assets["Pixel_M"].render(str((self.throttle + 1) * 10), False, COLOR_BLACK), (100, WINDOW_HEIGHT // 2))
        pygame.draw.rect(self.display, COLOR_BLACK, (0, (WINDOW_HEIGHT // 4) + 40 - self.borderSize, 75 + self.borderSize * 2, (WINDOW_HEIGHT // 2) - 27 + self.borderSize * 2))
        pygame.draw.rect(self.display, COLOR_GREY, (self.borderSize, (WINDOW_HEIGHT // 4) + 40, 75, (WINDOW_HEIGHT // 2) - 28))
        #9 doit etre egal a (WINDOW_HEIGHT // 4)
        #self.throttle * x = (WINDOW_HEIGHT // 4)
        throttleY = (self.throttle) * ((WINDOW_HEIGHT // 2) / (self.throttle + 1)) - 5
        pygame.draw.line(self.display, COLOR_RED,
                (self.borderSize, (WINDOW_HEIGHT - (WINDOW_HEIGHT // 4)) - throttleY),
                (self.borderSize + 74, (WINDOW_HEIGHT - (WINDOW_HEIGHT // 4)) - throttleY),
                10)

    def computeTirePositions(self):
        arrowSize = self.assets["ArrowUp"].get_rect()[2] // 2 - 40
        arrowHeight = self.assets["ArrowUp"].get_rect()[2]
        self.upperLeftTirePos = ((WINDOW_WIDTH // 3) - arrowSize, (WINDOW_HEIGHT // 4) - arrowHeight)
        self.lowerLeftTirePos = ((WINDOW_WIDTH // 3) - arrowSize, (WINDOW_HEIGHT - (WINDOW_HEIGHT // 4) - arrowHeight))
        self.upperRightTirePos = (WINDOW_WIDTH - (WINDOW_WIDTH // 3) - arrowSize, (WINDOW_HEIGHT // 4) - arrowHeight)
        self.lowerRightTirePos = (WINDOW_WIDTH - (WINDOW_WIDTH // 3) - arrowSize, (WINDOW_HEIGHT - (WINDOW_HEIGHT // 4) - arrowHeight))

    def drawTires(self):
        if self.message[1] == "1":
            self.display.blit(self.assets["ArrowDown"], self.upperLeftTirePos)
            self.display.blit(self.assets["ArrowDown"], self.lowerLeftTirePos)
            self.display.blit(self.assets["ArrowUp"], self.upperRightTirePos)
            self.display.blit(self.assets["ArrowUp"], self.lowerRightTirePos)
        elif self.message[1] == "2":
            self.display.blit(self.assets["ArrowUp"], self.upperLeftTirePos)
            self.display.blit(self.assets["ArrowUp"], self.lowerLeftTirePos)
            self.display.blit(self.assets["ArrowDown"], self.upperRightTirePos)
            self.display.blit(self.assets["ArrowDown"], self.lowerRightTirePos)
        else:
            if self.message[0] == "1":
                self.display.blit(self.assets["ArrowUp"], self.upperLeftTirePos)
                self.display.blit(self.assets["ArrowUp"], self.lowerLeftTirePos)
                self.display.blit(self.assets["ArrowUp"], self.upperRightTirePos)
                self.display.blit(self.assets["ArrowUp"], self.lowerRightTirePos)
            elif self.message[0]  == "2":
                self.display.blit(self.assets["ArrowDown"], self.upperLeftTirePos)
                self.display.blit(self.assets["ArrowDown"], self.lowerLeftTirePos)
                self.display.blit(self.assets["ArrowDown"], self.upperRightTirePos)
                self.display.blit(self.assets["ArrowDown"], self.lowerRightTirePos)
            else:
                self.display.blit(self.assets["ArrowNone"], self.upperLeftTirePos)
                self.display.blit(self.assets["ArrowNone"], self.lowerLeftTirePos)
                self.display.blit(self.assets["ArrowNone"], self.upperRightTirePos)
                self.display.blit(self.assets["ArrowNone"], self.lowerRightTirePos)
