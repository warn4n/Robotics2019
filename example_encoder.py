#motors have 2240 ticks per revolution

import time
import RPi.GPIO as GPIO
from threading import Thread
import math

class Encoder(Thread):
	GPIO.setmode(GPIO.BCM)

	leftDistance = 0
	rightDistance = 0


	leftTime = time.time()
	rightTime = time.time()

	rightCount = 0
	lastRightCount = 0
	lastLeftCount = 0
	leftCount = 0

	ticksInRev = 2240
	wheelRadiusCm = 4

	def run(self):
		pin_A_left = 17
		pin_B_left = 18
		pin_A_right = 20
		pin_B_right = 21

		GPIO.setup(pin_A_left, GPIO.IN)
		GPIO.setup(pin_B_left, GPIO.IN)
		GPIO.setup(pin_A_right, GPIO.IN)
		GPIO.setup(pin_B_right, GPIO.IN)

		outcome = [0, -1, 1, 0, -1, 0, 0, 1, 1, 0, 0, -1, 0, -1, 1, 0]

		last_AB_left = 0b00
		last_AB_right = 0b00
		counter_left = 0
		counter_right = 0

		while True:
			A_left = GPIO.input(pin_A_left)
			B_left = GPIO.input(pin_B_left)

			A_right = GPIO.input(pin_A_right)
			B_right = GPIO.input(pin_B_right)

			current_AB_left = (A_left << 1) | B_left
			current_AB_right = (A_right << 1) | B_right



			if (current_AB_left != last_AB_left):
				position_left = (last_AB_left << 2) | current_AB_left
				counter_left += outcome[position_left]
				last_AB_left = current_AB_left
				self.leftCount = counter_left

				# left motor is backwards
				#print("Left wheel counter: ", -self.counter_left)

			if (current_AB_right != last_AB_right):
				position_right = (last_AB_right << 2) | current_AB_right
				counter_right += outcome[position_right]
				last_AB_right = current_AB_right
				self.rightCount = counter_right
				#print("Right wheel counter: ", self.counter_right)


	def getRightTicks(self):
		diff = self.rightCount - self.lastRightCount
		self.lastRightCount = self.rightCount
		return diff

	def getLeftTicks(self):
		diff = self.leftCount - self.lastLeftCount
		self.lastLeftCount = self.leftCount
		return diff

	def getPhiDotRight(self):
		timeDelta = time.time() - self.rightTime
		self.rightTime = time.time()
		rotations = (self.wheelRadiusCm*self.getRightTicks()/self.ticksInRev)
		self.rightDistance += rotations*2*math.pi
		return rotations/timeDelta

	def getPhiDotLeft(self):
		timeDelta = time.time() - self.leftTime
		self.leftTime = time.time()
		rotations = self.wheelRadiusCm*self.getLeftTicks()/self.ticksInRev
		self.leftDistance += rotations * 2 * math.pi
		return rotations/timeDelta



