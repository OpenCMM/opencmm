#!/usr/bin/python
import RPi.GPIO as GPIO
import time

# Set GPIO mode (BCM or BOARD)
GPIO.setmode(GPIO.BCM)

servo_pins = [3, 4]

# Set the PWM frequency (Hz)
frequency = 50

# Setup GPIO pin for servo motor
for servo_pin in servo_pins:
    GPIO.setup(servo_pin, GPIO.OUT)

# Create PWM instance
pwms = []
for servo_pin in servo_pins:
    pwm = GPIO.PWM(servo_pin, frequency)
    pwms.append(pwm)
    # Start PWM with 0% duty cycle (neutral position)
    pwm.start(0)

try:
    while True:
        for pwm in pwms:
            # Move servo to 0 degrees (counter-clockwise)
            pwm.ChangeDutyCycle(2.5)
            time.sleep(1)

            pwm.ChangeDutyCycle(5.0)
            time.sleep(1)
            
            # Move servo to 90 degrees (center position)
            # pwm.ChangeDutyCycle(7.5)
            # time.sleep(1)
            
            # Move servo to 180 degrees (clockwise)
            # pwm.ChangeDutyCycle(12.5)
            # time.sleep(1)

except KeyboardInterrupt:
    # Clean up GPIO on Ctrl+C
    pwm.stop()
    GPIO.cleanup()
