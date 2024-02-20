import RPi.GPIO as GPIO
from time import sleep

button_dict = {2: "Power", 3: "info", 4: "Home", 14: "Vol_don", 50: "Vol_up"}

GPIO.setmode(GPIO.BCM)

for pin in button_dict.keys():
    GPIO.setup(pin, GPIO.IN)

running = True
while running:
    for button_id in button_dict.keys():
        if GPIO.input(button_id) == 0:
            print(f"Button pressed: {button_dict[button_id]}")
            sleep(0.25)


GPIO.cleanup()