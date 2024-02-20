from gpiozero import Button
from signal import pause
def say_hello():
    print("Hello!")
def say_goodbye():
    print("Goodbye!")


print("start")
button = Button(3)
button.when_pressed = say_hello
button.when_released = say_goodbye
pause()

# import sys
# import RPi.GPIO as GPIO
# from time import sleep
#
# button_dict = {3: "Power", 5: "info", 7: "Home", 8: "Vol_don", 10: "Vol_up"}
#
# GPIO.setmode(GPIO.BCM)
#
# for pin in button_dict.keys():
#     GPIO.setup(pin, GPIO.IN)
#
# running = True
# while running:
#     for button_id in button_dict.keys():
#         if GPIO.input(button_id) == 0:
#             print(f"Button pressed: {button_dict[button_id]}")
#             sleep(0.25)


# GPIO.cleanup()