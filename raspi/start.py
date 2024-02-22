#!/usr/bin/python3

"""
Use two 28BYJ-48 stepper motors to rotate and lift the scanner
Take pictures with raspberry pi high quality camera

1. lift the scanner up by 45°
2. rotate the scanner by 2.815°
3. take a picture and send it to the server over websockets
4. keep rotating the scanner by 2.815° and taking pictures until the scanner has rotated 360°
5. lower the scanner by 45°
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

# lifting motor
in5 = 26
in6 = 19
in7 = 13
in8 = 6

# careful lowering this, at some point you run into the mechanical limitation of how quick your motor can move
step_sleep = 0.002

one_step_rotation = int(4096 / 128)
step_count_rotation_motor = 4096  # 5.625*(1/64) per step, 4096 steps is 360°
step_count_lifting_motor = 512  # 45°


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


def take_picture(picam2) -> bytes:
    data = io.BytesIO()
    picam2.capture_file(data, format="jpeg")
    image_data = data.getvalue()
    return image_data


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


async def main():
    # establish the websockets connection
    uri = "ws://192.168.72.219:8765"
    async with websockets.connect(uri) as websocket:
        direction = False  # True for clockwise, False for counter-clockwise
        setup_pins(motor_pins)
        picam2 = Picamera2()
        is_full = False
        if is_full:
            picam2.configure(picam2.create_still_configuration())
        else:
            picam2.configure(picam2.create_preview_configuration())
        picam2.start()
        print("camera started")

        time.sleep(1)

        # lifting the scanner up by 45°
        move_motor(step_count_lifting_motor, direction, step_sleep, lifting_motor_pins)
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

        # reversing direction
        direction = not direction

        # lowering the scanner by 45°
        move_motor(step_count_lifting_motor, direction, step_sleep, lifting_motor_pins)
        # rotating the scanner by 360° in the opposite direction
        move_motor(
            step_count_rotation_motor, direction, step_sleep, rotation_motor_pins
        )

        print("done")

        picam2.stop()
        cleanup()
        exit(0)


asyncio.run(main())
