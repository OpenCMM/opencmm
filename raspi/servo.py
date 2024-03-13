#!/usr/bin/python
"""
Test two servo motors
"""
import RPi.GPIO as GPIO
import time

# Set GPIO mode (BCM or BOARD)
GPIO.setmode(GPIO.BCM)

# move camera
servo0 = 3
# move laser1
servo1 = 4

servo_pins = [servo0, servo1]

# Set the PWM frequency (Hz)
frequency = 50

# Setup GPIO pin for servo motor
for servo_pin in servo_pins:
    GPIO.setup(servo_pin, GPIO.OUT)

# Create PWM instance
servo0_pwm = GPIO.PWM(servo0, frequency)
servo1_pwm = GPIO.PWM(servo1, frequency)

servo0_initial_duty_cycle = 2.5
servo1_initial_duty_cycle = 12.5

# Start PWM with the duty cycle that corresponds to 0 degrees
servo0_pwm.start(servo0_initial_duty_cycle)
servo1_pwm.start(servo1_initial_duty_cycle)

try:
    # move servo0 to 180 degrees
    servo0_pwm.ChangeDutyCycle(12.5)
    # move servo1 to 140 degrees counter-clockwise
    servo1_pwm.ChangeDutyCycle(5.0)

    while True:
        time.sleep(100)

except KeyboardInterrupt:
    print("KeyboardInterrupt")
    # move to 0 degrees
    servo0_pwm.ChangeDutyCycle(servo0_initial_duty_cycle)
    servo1_pwm.ChangeDutyCycle(servo1_initial_duty_cycle)

    time.sleep(1)

    # Clean up GPIO on Ctrl+C
    servo0_pwm.stop()
    servo1_pwm.stop()
    GPIO.cleanup()
