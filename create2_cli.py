#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 27 May 2015

###########################################################################
# Copyright (c) 2015 iRobot Corporation
# http://www.irobot.com/
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#   Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
#
#   Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in
#   the documentation and/or other materials provided with the
#   distribution.
#
#   Neither the name of iRobot Corporation nor the names
#   of its contributors may be used to endorse or promote products
#   derived from this software without specific prior written
#   permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
###########################################################################

import struct
import sys, glob # for listing serial ports

try:
    import serial
except ImportError:
    print 'ERROR: Install pyserial'
    raise

connection = None

VELOCITYCHANGE = 200
ROTATIONCHANGE = 300

helpText = """\
Supported Keys:
P\tPassive
S\tSafe
F\tFull
C\tClean
D\tDock
R\tReset
Space\tBeep
Arrows\tMotion

If nothing happens after you connect, try pressing 'P' and then 'S' to get into safe mode.
"""

class TetheredDriveApp():
    # static variables for keyboard callback -- I know, this is icky
    callbackKeyUp = False
    callbackKeyDown = False
    callbackKeyLeft = False
    callbackKeyRight = False
    callbackKeyLastDriveCommand = ''

    def __init__(self):
        if not self.onConnect():
            sys.exit()

    # sendCommandASCII takes a string of whitespace-separated, ASCII-encoded base 10 values to send
    def sendCommandASCII(self, command):
        cmd = ""
        for v in command.split():
            cmd += chr(int(v))

        self.sendCommandRaw(cmd)

    # sendCommandRaw takes a string interpreted as a byte array
    def sendCommandRaw(self, command):
        global connection

        try:
            if connection is not None:
                connection.write(command)
            else:
                print "Not connected."
        except serial.SerialException:
            print "Lost connection"
            connection = None

        print ' '.join([ str(ord(c)) for c in command ])

    # getDecodedBytes returns a n-byte value decoded using a format string.
    # Whether it blocks is based on how the connection was set up.
    def getDecodedBytes(self, n, fmt):
        global connection

        try:
            return struct.unpack(fmt, connection.read(n))[0]
        except serial.SerialException:
            print "Lost connection"
            connection = None
            return None
        except struct.error:
            print "Got unexpected data from serial port."
            return None

    # get8Unsigned returns an 8-bit unsigned value.
    def get8Unsigned(self):
        return getDecodedBytes(1, "B")

    # get8Signed returns an 8-bit signed value.
    def get8Signed(self):
        return getDecodedBytes(1, "b")

    # get16Unsigned returns a 16-bit unsigned value.
    def get16Unsigned(self):
        return getDecodedBytes(2, ">H")

    # get16Signed returns a 16-bit signed value.
    def get16Signed(self):
        return getDecodedBytes(2, ">h")

    def getCommands(self):
        while True:
            cmd = raw_input('> ')
            if (cmd == 'quit'):
                self.sendCommandASCII('128')
                break
            elif (cmd == 'stop'):
                self.stop()
            elif cmd == 'p': # Passive
                self.sendCommandASCII('128')
            elif cmd == 's': # Safe
                self.sendCommandASCII('131')
            elif cmd == 'f': # Full
                self.sendCommandASCII('132')
            elif cmd == 'c': # Clean
                self.sendCommandASCII('135')
            elif cmd == 'd': # Dock
                self.sendCommandASCII('143')
            elif cmd == 'b': # Beep
                self.sendCommandASCII('140 3 1 64 16 141 3')
            elif cmd == 'reset': # Reset
                self.sendCommandASCII('7')
            else:
                try:
                    self.sendCommandASCII(cmd)
                except ValueError:
                    print 'Invalid command'
        print 'Done'

    # A handler for keyboard events. Feel free to add more!
    def callbackKey(self, event):
        k = event.keysym.upper()
        motionChange = False

        if event.type == '2': # KeyPress; need to figure out how to get constant
            if k == 'P':   # Passive
                self.sendCommandASCII('128')
            elif k == 'S': # Safe
                self.sendCommandASCII('131')
            elif k == 'F': # Full
                self.sendCommandASCII('132')
            elif k == 'C': # Clean
                self.sendCommandASCII('135')
            elif k == 'D': # Dock
                self.sendCommandASCII('143')
            elif k == 'SPACE': # Beep
                self.sendCommandASCII('140 3 1 64 16 141 3')
            elif k == 'R': # Reset
                self.sendCommandASCII('7')
            elif k == 'UP':
                self.callbackKeyUp = True
                motionChange = True
            elif k == 'DOWN':
                self.callbackKeyDown = True
                motionChange = True
            elif k == 'LEFT':
                self.callbackKeyLeft = True
                motionChange = True
            elif k == 'RIGHT':
                self.callbackKeyRight = True
                motionChange = True
            elif k == 'Y':
                self.sendCommandASCII('139 3 255 255')
            else:
                print repr(k), "not handled"
        elif event.type == '3': # KeyRelease; need to figure out how to get constant
            if k == 'UP':
                self.callbackKeyUp = False
                motionChange = True
            elif k == 'DOWN':
                self.callbackKeyDown = False
                motionChange = True
            elif k == 'LEFT':
                self.callbackKeyLeft = False
                motionChange = True
            elif k == 'RIGHT':
                self.callbackKeyRight = False
                motionChange = True

        if motionChange == True:
            velocity = 0
            velocity += VELOCITYCHANGE if self.callbackKeyUp is True else 0
            velocity -= VELOCITYCHANGE if self.callbackKeyDown is True else 0
            rotation = 0
            rotation += ROTATIONCHANGE if self.callbackKeyLeft is True else 0
            rotation -= ROTATIONCHANGE if self.callbackKeyRight is True else 0

            # compute left and right wheel velocities
            vr = velocity + (rotation/2)
            vl = velocity - (rotation/2)

            # create drive command
            cmd = struct.pack(">Bhh", 145, vr, vl)
            if cmd != self.callbackKeyLastDriveCommand:
                self.sendCommandRaw(cmd)
                self.callbackKeyLastDriveCommand = cmd

    def stop(self):
        self.sendCommandASCII('145 0 0 0 0')

    def onConnect(self):
        global connection

        if connection is not None:
            print 'Oops, Already connected'
            return False

        try:
            ports = self.getSerialPorts()
            port = raw_input('Enter COM port to open.\nAvailable options:\n' + '\n'.join(ports) + '\n')
        except EnvironmentError:
            port = raw_input('Enter COM port to open. (environment error)')

        # Default to first choice in ports
        if len(port) == 0 and len(ports) > 0:
            port = ports[0]
        if port is not None:
            print "Trying " + str(port) + "... "
            try:
                connection = serial.Serial(port, baudrate=115200, timeout=1)
                print "Connected!"
                return True
            except:
                print "Failed."
                return False
        print 'Idk what happened'
        return False

    def getSerialPorts(self):
        """Lists serial ports
        From http://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of available serial ports
        """
        if sys.platform.startswith('win'):
            ports = ['COM' + str(i + 1) for i in range(256)]

        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this is to exclude your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')

        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')

        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result

if __name__ == "__main__":
    app = TetheredDriveApp()
    app.getCommands()
