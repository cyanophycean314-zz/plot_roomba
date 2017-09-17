# Plot a series of x-y points

# Version 1:
# At each point, point and turn.

import math
#import create2cli
import urllib
import time

MAGIC_URL = 'https://www.wolframcloud.com/objects/user-0bd94b55-72c1-466a-8c79-c0ad96a59807/output?y=1'

class RoombaNavigate():
    position = (0,0)    #in units of scaling
    theta = 0           #radians from x-axis
    prev_data = ''

    def __init__(self):
        print 'start'

    def start(self):
        while True:
            try:
                file_handler = urllib.urlopen(MAGIC_URL)
            except IOError:
                print 'Connection Error: could not connect'
                continue
            data = file_handler.readline()
            if data != prev_data:
                prev_data = data
                points = self.download_points(data)
                self.plot_xy(points)
                self.move_to_origin()
            time.sleep(2)
        

    def download_points(self, data):
        try:
            file_handler = urllib.urlopen(MAGIC_URL)
        except IOError:
            print 'Connection Error: could not connect'
        data = file_handler.readline()
        wolfram_string = data[:-6]
        end_str = wolfram_string.rfind('}}', 2)
        points_string = wolfram_string[3:end_str + 1]
        points_array = points_string.split('}, {')
        request_time = points_array.pop()
        points = []
        maxy = float('-inf')
        for point in points_array:
            points.append(point.split(', ').map(int))
            if (points[1] > maxy):
                maxy = points[1]
        for i in range(len(points)):
            points[i][1] *= SCALING_FACTOR / maxy
        print points
        return points

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

    def rotate(angle):
        print 'rotate ' + angle

    def travel(dist):
        print 'travel ' + dist

if __name__ == "__main__":
    roomba = RoombaNavigate()
    roomba.start()
