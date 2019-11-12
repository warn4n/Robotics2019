from rplidar import RPLidar, RPLidarException
import time
import threading
import sys
import os
import signal
import RPi.GPIO as GPIO
import example_motor


PORT_NAME = '/dev/ttyUSB0'
global proxyBool

class Lidar(threading.Thread):
    QualityIdx = 0
    angleIdx = 1
    distanceIdx = 2
    rpLidar = RPLidar(PORT_NAME)
    ml = None
    mr = None



    def run(self):
        global proxyBool
        proxyBool = False
        while not proxyBool:
            time.sleep(.1)
            data = self.readScans(50)
            self.setForwardProxy(data)



        self.ml.brake()
        self.ml.off()

        print("kill CMD")
        GPIO.cleanup()
        os.killpg(0, signal.SIGTERM)





    def setForwardProxy(self,dataScan):
        global proxyBool
        dataList = []
        for data in dataScan:  # reading is a full 360 scan
            dataList.append(data)
            for reading in data:

                print(reading)

                if (reading[self.distanceIdx] > 5 and reading[self.distanceIdx]) < 500 and ((reading[self.angleIdx] > 120) or (reading[self.angleIdx] < 260) ): #proxy Trig
                    proxyBool = True






    def readScans(self,scansToCollect):
        #print("this is a test")
        #self.rpLidar.clear_input()
        data = []
        #print("new loop")
        forwardProximity = False
        numOFScans = 0

        try:
            for scan in self.rpLidar.iter_scans():
                # print(scan)
                data.append(scan)
                numOFScans = numOFScans + 1
                if numOFScans == scansToCollect:
                    return data
            self.rpLidar.stop()
        except RPLidarException:
            print("read error")
            pass