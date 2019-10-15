#motors have 2240 ticks per revolution

import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

pin_A_left = 17
pin_B_left = 18
pin_A_right = 20
pin_B_right = 21

GPIO.setup(pin_A_left, GPIO.IN)
GPIO.setup(pin_B_left, GPIO.IN)
GPIO.setup(pin_A_right, GPIO.IN)
GPIO.setup(pin_B_right, GPIO.IN)

outcome = [0,-1,1,0,-1,0,0,1,1,0,0,-1,0,-1,1,0]

last_AB_left = 0b00
counter_left = 0

def update_left_counter(channel): 
	
	global last_AB_left
	global counter_left
	
	A_left = GPIO.input(pin_A_left)
	B_left = GPIO.input(pin_B_left) 
	
	current_AB_left = (A_left<<1)|B_left	
	position_left = (last_AB_left<<2)|current_AB_left
	counter_left += outcome[position_left]
	last_AB_left = current_AB_left
	
	#left motor is backwards
	print("Left wheel counter: ", -counter_left)	
	 
GPIO.add_event_detect(pin_A_left, GPIO.BOTH, callback=update_left_counter, bouncetime=1)  
GPIO.add_event_detect(pin_B_left, GPIO.BOTH, callback=update_left_counter, bouncetime=1) 

while True:
	
	"""
	do nothing
	"""
