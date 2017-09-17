# Plot a series of x-y points

# Version 1:
# At each point, point and turn.

import math
import create2_cli
import urllib
import time

SCALING_FACTOR = 20

MAGIC_URL = 'https://www.wolframcloud.com/objects/user-0bd94b55-72c1-466a-8c79-c0ad96a59807/output?y=1'
TEST_DATA = "{{{0, 0}, {1, 1}, {2, 8}, {3, 27}, {4, 64}, {5, 125}, {6, 216}, {7, 343}, {8, 512}, {9, 729}, {10, 1000}, {11, 1331}, {12, 1728}, {13, 2197}, {14, 2744}, {15, 3375}, {16, 4096}, {17, 4913}, {18, 5832}, {19, 6859}, {20, 8000}, {21, 9261}, {22, 10648}, {23, 12167}, {24, 13824}, {25, 15625}, {26, 17576}, {27, 19683}, {28, 21952}, {29, 24389}, {30, 27000}, {31, 29791}, {32, 32768}, {33, 35937}, {34, 39304}, {35, 42875}, {36, 46656}, {37, 50653}, {38, 54872}, {39, 59319}, {40, 64000}, {41, 68921}, {42, 74088}, {43, 79507}, {44, 85184}, {45, 91125}, {46, 97336}, {47, 103823}, {48, 110592}, {49, 117649}, {50, 125000}, {51, 132651}, {52, 140608}, {53, 148877}, {54, 157464}, {55, 166375}, {56, 175616}, {57, 185193}, {58, 195112}, {59, 205379}, {60, 216000}, {61, 226981}, {62, 238328}, {63, 250047}, {64, 262144}, {65, 274625}, {66, 287496}, {67, 300763}, {68, 314432}, {69, 328509}, {70, 343000}, {71, 357911}, {72, 373248}, {73, 389017}, {74, 405224}, {75, 421875}, {76, 438976}, {77, 456533}, {78, 474552}, {79, 493039}, {80, 512000}, {81, 531441}, {82, 551368}, {83, 571787}, {84, 592704}, {85, 614125}, {86, 636056}, {87, 658503}, {88, 681472}, {89, 704969}, {90, 729000}, {91, 753571}, {92, 778688}, {93, 804357}, {94, 830584}, {95, 857375}, {96, 884736}, {97, 912673}, {98, 941192}, {99, 970299}, {100, 1000000}, {101, 1030301}, {102, 1061208}, {103, 1092727}, {104, 1124864}, {105, 1157625}, {106, 1191016}, {107, 1225043}, {108, 1259712}, {109, 1295029}, {110, 1331000}, {111, 1367631}, {112, 1404928}, {113, 1442897}, {114, 1481544}, {115, 1520875}, {116, 1560896}, {117, 1601613}, {118, 1643032}, {119, 1685159}, {120, 1728000}, {121, 1771561}, {122, 1815848}, {123, 1860867}, {124, 1906624}, {125, 1953125}, {126, 2000376}, {127, 2048383}, {128, 2097152}, {129, 2146689}, {130, 2197000}, {131, 2248091}, {132, 2299968}, {133, 2352637}, {134, 2406104}, {135, 2460375}, {136, 2515456}, {137, 2571353}, {138, 2628072}, {139, 2685619}, {140, 2744000}, {141, 2803221}, {142, 2863288}, {143, 2924207}, {144, 2985984}, {145, 3048625}, {146, 3112136}, {147, 3176523}, {148, 3241792}, {149, 3307949}, {150, 3375000}, {151, 3442951}, {152, 3511808}, {153, 3581577}, {154, 3652264}, {155, 3723875}, {156, 3796416}, {157, 3869893}, {158, 3944312}, {159, 4019679}, {160, 4096000}, {161, 4173281}, {162, 4251528}, {163, 4330747}, {164, 4410944}, {165, 4492125}, {166, 4574296}, {167, 4657463}, {168, 4741632}, {169, 4826809}, {170, 4913000}, {171, 5000211}, {172, 5088448}, {173, 5177717}, {174, 5268024}, {175, 5359375}, {176, 5451776}, {177, 5545233}, {178, 5639752}, {179, 5735339}, {180, 5832000}, {181, 5929741}, {182, 6028568}, {183, 6128487}, {184, 6229504}, {185, 6331625}, {186, 6434856}, {187, 6539203}, {188, 6644672}, {189, 6751269}, {190, 6859000}, {191, 6967871}, {192, 7077888}, {193, 7189057}, {194, 7301384}, {195, 7414875}, {196, 7529536}, {197, 7645373}, {198, 7762392}, {199, 7880599}, {200, 8000000}}, {2017, 9, 16, 17, 57, 19.234923`8.036665436084373}}[<||>]"
app = None

class RoombaNavigate():
    position = (0,0)    #in units of scaling
    theta = 0           #radians from x-axis
    prev_data = ''
    seconds_per_degree = 0.024  #found experimentally
    seconds_per_dist_unit = 0.5   #tuned for best experience
    def __init__(self):
        print 'start'

    def start(self):
        while True:
            print('loop start')
            try:
                file_handler = urllib.urlopen(MAGIC_URL)
                data = file_handler.readline()
            except IOError:
                print 'Connection Error: could not connect'
                data = TEST_DATA
                continue
            if data != self.prev_data:
                print('plot start')
                self.prev_data = data
                points = self.download_points(data)
                self.plot_xy(points)
                self.move_to_origin()
                print('plot stop')
            time.sleep(2)


    def download_points(self, data):
        wolfram_string = data[:-6]
        end_str = wolfram_string.rfind('}}', -2)
        points_string = wolfram_string[3:end_str + 1]
        points_array = points_string.split('}, {')
        request_time = points_array.pop()
        points_array[-1] = points_array[-1][:-1]    #Chop off the last brace
        points = []
        maxy = float('-inf')
        for point in points_array[:20]:
            next_point = map(int, point.split(', '))
            points.append(next_point)
            if (next_point[1] > maxy):
                maxy = next_point[1]
        for i in range(len(points)):
            points[i][1] *= SCALING_FACTOR / float(maxy)
        print points
        return points

    def move_to_origin(self):
        print 'idk'

    def plot_xy(self, points):
        self.move_to_origin()
        lastx, lasty = 0, 0
        for x, y in points:
            self.move(lastx, lasty, x, y)
            lastx, lasty = x, y

    def move(self, lastx, lasty, x, y):
        new_theta = math.atan2(y, x)
        print new_theta
        diff_theta = new_theta - self.theta
        dist = math.sqrt((x - lastx) ** 2 + (y - lasty) ** 2)
        self.theta = new_theta
        self.rotate(diff_theta)
        self.travel(dist)

    def rotate(self, angle):
        global app

        degrees = math.degrees(angle)
        print 'rotate ' + str(degrees) + ' degrees'
        if degrees > 0:
            print 'time: ' + str(degrees * self.seconds_per_degree)
            app.sendCommandASCII('137 0 80 0 1')
            time.sleep(degrees * self.seconds_per_degree)
            app.stop()
        else:
            print 'time: ' + str(-degrees * self.seconds_per_degree)
            app.sendCommandASCII('137 0 80 255 255')
            time.sleep(-degrees * self.seconds_per_degree)
            app.stop()

    def travel(self, dist):
        global app

        app.sendCommandASCII('145 0 100 0 100')
        time.sleep(dist * self.seconds_per_dist_unit)
        app.stop()

if __name__ == "__main__":
    roomba = RoombaNavigate()
    app = create2_cli.TetheredDriveApp()
    app.sendCommandASCII('131')
    roomba.start()
