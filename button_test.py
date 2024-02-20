# from gpiozero import Button
# from signal import pause
# def say_hello():
#     print("Hello!")
# def say_goodbye():
#     print("Goodbye!")
#
#
# print("start")
#
# buttons = [Button(id) for id in range(10)]
# for button in buttons:
#     button.when_pressed = say_hello
#     button.when_released = say_goodbye
#
# pause()

import sys
import RPi.GPIO as GPIO
from time import sleep

import gpiod

# , 3: "Power", 5: "info", 7: "Home", 8: "Vol_don", 10: "Vol_up"
button_dict = {2: "Hi", 3: "Power", 5: "info", 7: "Home", 8: "Vol_don", 4: "Vol_up"}
# LED_PIN = 17

chip = gpiod.Chip('gpiochip4')
# led_line = chip.get_line(LED_PIN)
button_lines = [chip.get_line(pin_num) for pin_num in button_dict.keys()]
# led_line.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)
for line in button_lines:
    line.request(consumer="Button", type=gpiod.LINE_REQ_DIR_IN)

while True:
    for idx, line in enumerate(button_lines):
        button_state = line.get_value()
        print(button_state)
        if button_state == 1:
            print(f"{list(button_dict.values())[idx]} Pressed")