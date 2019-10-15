# docs: https://rplidar.readthedocs.io/en/latest/
from rplidar import RPLidar
import time
import threading 
import sys

lidar = RPLidar('/dev/ttyUSB0')
stop_flag = False

def close_lidar(): 
    stop_flag = True
    lidar.stop()
    lidar.stop_motor()
    lidar.disconnect()
    sys.exit(0)

info = lidar.get_info()
print(info)

health = lidar.get_health()
print(health)

time.sleep(2) #set 2 seconds to get full speed

timer = threading.Timer(3.0, close_lidar) #set timer for 3 seconds
timer.start() 

for measurment in enumerate(lidar.iter_measurments()): #print measurements
    print("quality: ",measurment[1][1],"angle: ", measurment[1][2], "distance: ",measurment[1][3] )
