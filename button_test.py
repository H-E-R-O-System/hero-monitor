import pygame as pg
# import gpiod

# Define Raspberry Pi button pins
# button_dict = {
#     4: "Power",     # Pin number 7
#     17: "Home",     # Pin number 11
#     27: "Vol Down",     # Pin number 13
#     22: "Info",  # Pin number 15
#     23: "Vol Up"    # Pin number 16
# }

# LED_PIN = 17

# chip = gpiod.Chip('gpiochip4')
# # led_line = chip.get_line(LED_PIN)
# button_lines = [(chip.get_line(pin_num), button_dict[pin_num]) for pin_num in button_dict.keys()]
# # led_line.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)
#
# for (line, name) in button_lines:
#     line.request(consumer="Button", type=gpiod.LINE_REQ_DIR_IN)
#
# current_state = None


class Buttons:
    def __init__(self, pi=True):
        self.pi = pi
        if self.pi:
            gpiod = __import__('gpiod')

            # Define Raspberry Pi button pins
            self.button_dict = {
                4: "Power",  # Pin number 7
                17: "Home",  # Pin number 11
                23: "Vol Up",  # Pin number 16
                27: "Vol Down",  # Pin number 13
                22: "Info",  # Pin number 15
            }
            # LED_PIN = 17

            chip = gpiod.Chip('gpiochip4')
            # led_line = chip.get_line(LED_PIN)
            self.button_lines = [(chip.get_line(pin_num), self.button_dict[pin_num]) for pin_num in self.button_dict.keys()]
            # led_line.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)
            for (line, name) in self.button_lines:
                line.request(consumer="Button", type=gpiod.LINE_REQ_DIR_IN)
        else:

            self.button_dict = {
                pg.K_1: "Power",  # Pin number 7
                pg.K_2: "Home",  # Pin number 11
                pg.K_3: "Vol Up",  # Pin number 16
                pg.K_4: "Vol Down",  # Pin number 13
                pg.K_5: "Info",  # Pin number 15
            }

        self.states = {
                "Power": 0,  # to track the current state (on/off)
                "Home": 0,  # to track the current state (on/off)
                "Vol Up": 0,  # to track the current state (on/off)
                "Vol Down": 0,  # to track the current state (on/off)
                "Info": 0,  # to track the current state (on/off)
        }

    def check_pressed(self):
        if self.pi:
            for idx, (line, name) in enumerate(self.button_lines):
                button_state = line.get_value()

                self.states[name] = button_state

                if button_state and not self.states[name]:
                    print(f"{name} Pressed")
                    return name

        else:
            pressed = pg.key.get_pressed()
            for val, name in self.button_dict.items():

                if pressed[val] and not self.states[name]:
                    self.states[name] = pressed[val]
                    return name

                self.states[name] = pressed[val]

        return None


pg.init()
pg.event.pump()

pi = False
buttons = Buttons(pi)
while True:
    if pi:
        buttons.check_pressed()
    else:
        pg.event.pump()

        selected = buttons.check_pressed()
        if selected:
            print(f"{selected} pressed")
