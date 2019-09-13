#!/usr/bin/env python3

UDP_MAX_SIZE = 65507
#HD frame size: 6220800
PacketSize = 62208
#updated packet size = 62210, 2 de plus
class Packets(object): #recoit bytes
    def __init__(self, data, ID):
        self.packetsList = []
        #start = '#' + str(ID) + '!!' + str(PacketSize)
        #self.packetsList.append(start.encode('utf-8')) #START
        mid = str(ID) + '#'
        #tmpFlag = True
        for i in range (0, PacketSize * 100, PacketSize):
            packet = mid.encode('utf-8') + data[i:(i + PacketSize)]
            self.packetsList.append(packet)
            # if tmpFlag:
            #     print(dataSlice)
            #     tmpFlag = False
        print("data n°", str(ID), "with", len(self.packetsList), "packets from", len(data), "bytes created!")

    def popFirst(self):
        if len(self.packetsList) <= 0:
            return False
        return self.packetsList.pop(0)
