import example_encoder
import time
import example_motor

if __name__ == "__main__":
    encoder = example_encoder.Encoder()
    encoder.start()
    motors = example_motor.Motor()
    #while True:
    for x in range(50):
        time.sleep(.05)
        measuredPhiDotLeft = encoder.getPhiDotLeft()
        measuredPhiDotRight = encoder.getPhiDotRight()
        motors.PID(1,measuredPhiDotLeft,1.5,motors.setPhiDotDesiredLeft)
        motors.PID(1,measuredPhiDotRight, 1.5, motors.setPhiDotDesiredRight)

        print("Phi Dot Right is: "+str(measuredPhiDotRight))
        print("Phi Dot Left is: " + str(measuredPhiDotLeft))

    motors.brake()
    motors.off()
