#!/usr/bin/env python3

import sys
from App import *

def main():
    app = App()
    if len(sys.argv) == 1:
        print("Connecting to the Rasp...")
        app.initUDPConnection()
        app.initTCPConnection()
    else:
        print(T_COLOR_YELLOW + "Client Dev mode, no comms" + T_COLOR_RESET)
    app.run()

if __name__ == '__main__':
    main()
