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

button_dict = {2: "Hi", 3: "Power", 5: "info", 7: "Home", 8: "Vol_don", 10: "Vol_up"}

import gpiod
# LED_PIN = 17
BUTTON_PIN = 3
chip = gpiod.Chip('gpiochip4')
# led_line = chip.get_line(LED_PIN)
button_line = chip.get_line(BUTTON_PIN)
# led_line.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)
# button_line.request(consumer="Button", type=gpiod.LINE_REQ_DIR_IN)

while True:
   button_state = button_line.get_value()
   if button_state == 1:
       print("Pressed")
   # else:
   #     led_line.set_value(0)

# button_line.release()
