#!/usr/bin/env python3

import socket
import time

from picamera.array import PiRGBArray
from picamera import PiCamera

from adafruit_motorkit import MotorKit

from conf import *
from Packet import *

class App(object):
    def __init__(self, IP, camOn):
        self.packetID = 0
        self.camOn = camOn
        self.kit = MotorKit()
        self.IP = IP
        self.throttle = 0.0
        self.oldThrottle = 0.0
        self.turnFactor = 3.5
        if camOn:
            self.cam = PiCamera()
            self.cam.resolution = (X_RES, Y_RES)
            self.cam.framerate = FPS
            self.rawCapture = PiRGBArray(self.cam, size=(X_RES, Y_RES))
        self.getTCPConnection()
        self.getUDPConnection()

    def getUDPConnection(self):
        self.socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def getTCPConnection(self):
        self.socketTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socketTCP.bind((self.IP, TCP_PORT))
        self.socketTCP.listen(1)
        self.conn, self.addr = self.socketTCP.accept()
        print(T_COLOR_GREEN + "Client connected from:\t", self.addr[0] + ':' + str(self.addr[1]) + T_COLOR_RESET)
        buffer = ""
        while buffer.find("*") == -1:
            buffer += self.conn.recv(BUFFER_SIZE).decode("utf-8")
        self.UDP_PORT = buffer[(buffer.find(":") + 1):]
        self.UDP_PORT = int(self.UDP_PORT[:-1])
        self.remoteIP = buffer[:buffer.find(":")]
        print(T_COLOR_GREEN + "Received remote IP and UDP port: ", self.remoteIP + ":" + str(self.UDP_PORT), T_COLOR_RESET)

    def sendVideo(self):
        #print("SENDING UDP TEST MSG TO:", self.remoteIP + ":" + str(self.UDP_PORT))
        #self.socketUDP.sendto("".join("hello").encode(), (self.remoteIP, self.UDP_PORT))

        #print(type(self.image.tobytes()), len(self.image.tobytes()))
        Packet = Packets(self.image.tobytes(), self.packetID)
        self.packetID += 1
        if self.packetID == 1000:
            self.packetID = 0
        first = True
        while 1:
            tmp = Packet.popFirst()
            if tmp == False:
                break
            if first:
                print(tmp)
            self.socketUDP.sendto(tmp, (self.remoteIP, self.UDP_PORT))
        print("Frame sent!")

    def run(self):
        tmp = True
        while 1:
            self.data = self.conn.recv(BUFFER_SIZE)
            self.dataTime = time.time()
            if not self.data: break
            #print("received:", self.data, type(self.data[0]))
            #conn.send(data) #echo
            self.handleData()
            if self.camOn and tmp:
                self.captureVideo()
                self.sendVideo()
                tmp = False
        print(T_COLOR_RED + "Client\t\t", self.addr[0] + ':' + str(self.addr[1]) + " disconnected" + T_COLOR_RESET)
        self.conn.close()
        self.MotorStop()

    def handleData(self):
        #ERROR HANDLING
        if len(self.data) != 6:
            print(T_COLOR_YELLOW + "Corrupted data received:", str(self.data) + T_COLOR_RESET)
            return
        if self.data[2] < 48 or self.data[2] > 58:
            print(T_COLOR_YELLOW + "Invalid throttle data received:", str(self.data[2]), "using last valid value received:", str(self.throttle) + T_COLOR_RESET)
        else:
            self.oldThrottle = self.throttle
            self.throttle = (self.data[2] - 48) / 10
            if self.oldThrottle != self.throttle:
                print(T_COLOR_GREEN + "Throttle: " + ('=' * int(self.throttle * 10)) + ('-' * (10 - int(self.throttle * 10))))
        #48 VALUE DIFF
        if self.data[0] == 48 and self.data[1] == 48:
            self.MotorStop()
            return
        # if self.data[1] == 49:
        #     if self.data[0] == 49:
        #         self.MotorTurnRight()
        #     else:
        #         self.MotorRotateRight()
        # elif self.data[1] == 50:
        #     self.MotorRotateLeft()

        if self.data[0] == 49: #FORWARD
            if self.data[1] == 49: #LEFT
                self.MotorTurnLeft()
            elif self.data[1] == 50: #RIGHT
                self.MotorTurnRight()
            else:
                self.MotorAntiClockwise() #FORWARD
        elif self.data[0] == 50: #BACKWARDS
            if self.data[1] == 49: #LEFT
                self.MotorReverseRight()
            elif self.data[1] == 50: #RIGHT
                self.MotorReverseLeft()
            else:
                self.MotorClockwise() #BACKWARDS
        elif self.data[1] == 50: #LEFT
            self.MotorRotateLeft()
        elif self.data[1] == 49: #RIGHT
            self.MotorRotateRight()
        else:
            self.MotorStop()

    def captureVideo(self):
        for frame in self.cam.capture_continuous(self.rawCapture, format="bgr", use_video_port=True):
            # grab the raw NumPy array representing the image, then initialize the timestamp
            # and occupied/unoccupied text
            self.image = frame.array
            # show the frame
            # cv2.imshow("Frame", image)
            # key = cv2.waitKey(1) & 0xFF
            # clear the stream in preparation for the next frame
            self.rawCapture.truncate(0)
            break

#MOTOR1 = UPPER LEFT
#MOTOR2 = LOWER LEFT
#MOTOR3 = UPPER RIGHT
#MOTOR4 = LOWER RIGHT

    def MotorClockwise(self):
        self.kit.motor1.throttle = self.throttle
        self.kit.motor2.throttle = self.throttle
        self.kit.motor3.throttle = self.throttle
        self.kit.motor4.throttle = self.throttle

    def MotorAntiClockwise(self):
        self.kit.motor1.throttle = -self.throttle
        self.kit.motor2.throttle = -self.throttle
        self.kit.motor3.throttle = -self.throttle
        self.kit.motor4.throttle = -self.throttle

    def MotorStop(self):
        self.kit.motor1.throttle = 0
        self.kit.motor2.throttle = 0
        self.kit.motor3.throttle = 0
        self.kit.motor4.throttle = 0

    def MotorRotateLeft(self):
        self.kit.motor1.throttle = -self.throttle
        self.kit.motor2.throttle = -self.throttle
        self.kit.motor3.throttle = self.throttle
        self.kit.motor4.throttle = self.throttle

    def MotorRotateRight(self):
        self.kit.motor1.throttle = self.throttle
        self.kit.motor2.throttle = self.throttle
        self.kit.motor3.throttle = -self.throttle
        self.kit.motor4.throttle = -self.throttle

    def MotorTurnLeft(self):
        self.kit.motor1.throttle = -self.throttle / self.turnFactor
        self.kit.motor2.throttle = -self.throttle / self.turnFactor
        self.kit.motor3.throttle = -self.throttle
        self.kit.motor4.throttle = -self.throttle

    def MotorTurnRight(self):
        self.kit.motor1.throttle = -self.throttle
        self.kit.motor2.throttle = -self.throttle
        self.kit.motor3.throttle = -self.throttle / self.turnFactor
        self.kit.motor4.throttle = -self.throttle / self.turnFactor

    def MotorReverseLeft(self):
        self.kit.motor1.throttle = self.throttle
        self.kit.motor2.throttle = self.throttle
        self.kit.motor3.throttle = self.throttle / self.turnFactor
        self.kit.motor4.throttle = self.throttle / self.turnFactor

    def MotorReverseRight(self):
        self.kit.motor1.throttle = self.throttle / self.turnFactor
        self.kit.motor2.throttle = self.throttle / self.turnFactor
        self.kit.motor3.throttle = self.throttle
        self.kit.motor4.throttle = self.throttle
