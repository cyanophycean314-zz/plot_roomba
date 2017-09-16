# Plot a series of x-y points

# Version 1:
# At each point, point and turn.

import math
import create2cli

SCALING_FACTOR = 1

class RoombaNavigate():
    position = (0,0)    #in units of scaling
    theta = 0           #radians from x-axis
    def __init__(self):
        print 'start'

    def move_to_origin(self):
        print 'idk'

    def plot_xy(self, pts):
        self.move_to_origin()
        lastx, lasty = 0, 0
        for x, y in points:
            self.move(lastx, lasty, x, y)
            lastx, lasty = x, y

    def move(lastx, lasty, x, y):
        new_theta = math.atan2(y, x)
        diff_theta = new_theta - new_theta
        self.rotate(diff_theta)
        dist = math.sqrt((x - lastx) ** 2 + (y - lasty) ** 2)
        self.travel(dist)

    def rotate

    def travel(dist):


if __name__ == "__main__":
    roomba = RoombaNavigate()
