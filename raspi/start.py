#!/usr/bin/python3

"""
Use one 28BYJ-48 stepper motors to rotate and two servo motors to extend/close the scanner
Take pictures with raspberry pi high quality camera

1. extend the scanner using two servo motors
2. rotate the scanner by 2.815°
3. take a picture and send it to the server over websockets
4. keep rotating the scanner by 2.815° and taking pictures until the scanner has rotated 360°
5. close the scanner using two servo motors
6. rotate the scanner by 360° in the opposite direction
"""
import RPi.GPIO as GPIO
from picamera2 import Picamera2
import websockets
import asyncio
import time
import io

# rotation motor
in1 = 17
in2 = 18
in3 = 27
in4 = 22


# servo motors
# move camera
servo0 = 3
# move laser1
servo1 = 4
# Set the PWM frequency (Hz)
frequency = 50

# careful lowering this, at some point you run into the mechanical limitation of how quick your motor can move
step_sleep = 0.002

one_step_rotation = int(4096 / 128)
step_count_rotation_motor = 4096  # 5.625*(1/64) per step, 4096 steps is 360°


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


def setup_pins(motor_pins):
    # setting up
    GPIO.setmode(GPIO.BCM)
    for pin in motor_pins:
        GPIO.setup(pin, GPIO.OUT)


    # Setup GPIO pin for servo motor
    GPIO.setup(servo0, GPIO.OUT)
    GPIO.setup(servo1, GPIO.OUT)

    # initializing
    for pin in motor_pins:
        GPIO.output(pin, GPIO.LOW)

def extend_scanner(servo0_pwm, servo1_pwm):
    # move servo0 to 180 degrees
    servo0_pwm.ChangeDutyCycle(12.5)
    # move servo1 to 140 degrees counter-clockwise
    servo1_pwm.ChangeDutyCycle(5.0)

def close_scanner(servo0_pwm, servo1_pwm):
    # move to 0 degrees
    servo0_pwm.ChangeDutyCycle(2.5)
    servo1_pwm.ChangeDutyCycle(12.5)

    time.sleep(1)

    # Clean up GPIO on Ctrl+C
    servo0_pwm.stop()
    servo1_pwm.stop()


def take_picture(picam2) -> bytes:
    data = io.BytesIO()
    picam2.capture_file(data, format="jpeg")
    image_data = data.getvalue()
    return image_data


def cleanup():
    for pin in rotation_motor_pins:
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


async def main():
    # establish the websockets connection
    uri = "ws://ubuntu-main.local:8765"
    async with websockets.connect(uri) as websocket:
        direction = False  # True for clockwise, False for counter-clockwise
        setup_pins(rotation_motor_pins)
        picam2 = Picamera2()
        is_full = True
        if is_full:
            picam2.configure(picam2.create_still_configuration())
        else:
            picam2.configure(picam2.create_preview_configuration())
        picam2.start()
        print("camera started")

        time.sleep(1)

        # Create PWM instance
        servo0_pwm = GPIO.PWM(servo0, frequency)
        servo1_pwm = GPIO.PWM(servo1, frequency)

        # Start PWM with the duty cycle that corresponds to 0 degrees
        servo0_pwm.start(2.5)
        servo1_pwm.start(12.5)

        extend_scanner(servo0_pwm, servo1_pwm)

        for i in range(3):
            # for i in range(128):
            move_motor(one_step_rotation, direction, step_sleep, rotation_motor_pins)
            # take a picture
            print(f"taking a picture - {i+1}/128")
            image_data = take_picture(picam2)
            chunk_size = 1024  # Set the desired chunk size

            # Calculate the total number of chunks
            total_chunks = (len(image_data) + chunk_size - 1) // chunk_size
            await websocket.send(f"sending {total_chunks} chunks of data - {i+1}/128")

            # Send data in smaller chunks
            for i in range(total_chunks):
                start = i * chunk_size
                end = (i + 1) * chunk_size
                chunk = image_data[start:end]
                await websocket.send(chunk)
            await websocket.send("end")

        # reversing direction
        direction = not direction

        # move the scanner to the starting position
        close_scanner(servo0_pwm, servo1_pwm)
        # rotating the scanner by 360° in the opposite direction
        move_motor(
            step_count_rotation_motor, direction, step_sleep, rotation_motor_pins
        )

        print("done")

        picam2.stop()
        cleanup()
        exit(0)


asyncio.run(main())
