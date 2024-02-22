#!/usr/bin/python3

"""
Use two 28BYJ-48 stepper motors to rotate and lift the scanner

1. lift the scanner up by 45°
2. rotate the scanner by 2.815°
3. take a picture
4. keep rotating the scanner by 2.815° and taking pictures until the scanner has rotated 360°
5. lower the scanner by 45°
6. rotate the scanner by 360° in the opposite direction
"""
import RPi.GPIO as GPIO
import time

# rotation motor
in1 = 17
in2 = 18
in3 = 27
in4 = 22

# lifting motor
in5 = 26
in6 = 19
in7 = 13
in8 = 6

# careful lowering this, at some point you run into the mechanical limitation of how quick your motor can move
step_sleep = 0.002

one_step_rotation = int(4096/128)
step_count_rotation_motor = 4096  # 5.625*(1/64) per step, 4096 steps is 360°
step_count_lifting_motor = 512  # 45°

direction = False  # True for clockwise, False for counter-clockwise

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

rotation_motor_pins = [in1, in2, in3, in4]
lifting_motor_pins = [in5, in6, in7, in8]
motor_pins = [in1, in2, in3, in4, in5, in6, in7, in8]


def setup_pins(motor_pins):
    # setting up
    GPIO.setmode(GPIO.BCM)
    for pin in motor_pins:
        GPIO.setup(pin, GPIO.OUT)

    # initializing
    for pin in motor_pins:
        GPIO.output(pin, GPIO.LOW)


setup_pins(motor_pins)


def cleanup():
    for pin in motor_pins:
        GPIO.output(pin, GPIO.LOW)
    GPIO.cleanup()


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

time.sleep(1)

# lifting the scanner up by 45°
move_motor(step_count_lifting_motor, direction, step_sleep, lifting_motor_pins)
for i in range(128):
    move_motor(one_step_rotation, direction, step_sleep, rotation_motor_pins)
    # take a picture
    print(f"taking a picture - {i+1}/128")

# reversing direction
direction = not direction

# lowering the scanner by 45°
move_motor(step_count_lifting_motor, direction, step_sleep, lifting_motor_pins)
# rotating the scanner by 360° in the opposite direction
move_motor(step_count_rotation_motor, direction, step_sleep, rotation_motor_pins)

print("done")

cleanup()
exit(0)
