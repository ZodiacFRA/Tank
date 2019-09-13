#!/usr/bin/env python3
from App import *
from conf import *

import socket
import time

def main():
    IP = getIP()
    print(T_COLOR_GREEN + "Rasp IP is:\t", IP + T_COLOR_RESET)
    app = App(IP, False)
    time.sleep(1)
    app.run()

def getIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

if __name__ == '__main__':
    main()
