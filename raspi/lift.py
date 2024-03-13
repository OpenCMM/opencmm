#!/usr/bin/python3
import RPi.GPIO as GPIO
import time
import sys

# lifting motor
in1 = 26
in2 = 19
in3 = 13
in4 = 6

# careful lowering this, at some point you run into the mechanical limitation of how quick your motor can move
step_sleep = 0.004

full_step_rotation = 4096  # 5.625*(1/64) per step, 4096 steps is 360°
one_step_rotation = int(4096 / 128)

# defining stepper motor sequence (found in documentation http://www.4tronix.co.uk/arduino/Stepper-Motors.php)
step_sequence = [
    [1, 0, 0, 1],
    [1, 0, 0, 0],
    [1, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 0],
    [0, 0, 1, 1],
    [0, 0, 0, 1],
]

motor_pins = [in1, in2, in3, in4]


def setup_pins(motor_pins):
    # setting up
    GPIO.setmode(GPIO.BCM)
    for pin in motor_pins:
        GPIO.setup(pin, GPIO.OUT)

    # initializing
    for pin in motor_pins:
        GPIO.output(pin, GPIO.LOW)

def cleanup():
    for pin in motor_pins:
        GPIO.output(pin, GPIO.LOW)
    GPIO.cleanup()

def angle_to_step_count(angle):
    return int(full_step_rotation/360*angle)


def move_motor(step_count, direction, step_sleep, motor_pins):
    motor_step_counter = 0
    try:
        for i in range(step_count):
            for pin in range(0, len(motor_pins)):
                GPIO.output(motor_pins[pin], step_sequence[motor_step_counter][pin])
            if direction is True:
                motor_step_counter = (motor_step_counter - 1) % 8
            elif direction is False:
                motor_step_counter = (motor_step_counter + 1) % 8
            else:  # defensive programming
                print("uh oh... direction should *always* be either True or False")
                cleanup()
                exit(1)
            time.sleep(step_sleep)
    except KeyboardInterrupt:
        cleanup()
        exit(1)


def main(angle):
        direction = angle > 0  # True for clockwise, False for counter-clockwise
        setup_pins(motor_pins)

        step_count_rotation_motor = angle_to_step_count(angle)
        move_motor(abs(step_count_rotation_motor), direction, step_sleep, motor_pins)
        cleanup()
        exit(0)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python lift.py <angle>")
        sys.exit(1)
    angle = int(sys.argv[1])
    main(angle)