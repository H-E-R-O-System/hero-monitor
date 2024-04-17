import gpiod

# Define Raspberry Pi button pins
button_dict = {
    4: "Power",     # Pin number 7
    17: "Home",     # Pin number 11
    27: "Vol Down",     # Pin number 13
    22: "Info",  # Pin number 15
    23: "Vol Up"    # Pin number 16
}

# LED_PIN = 17

chip = gpiod.Chip('gpiochip4')
# led_line = chip.get_line(LED_PIN)
button_lines = [(chip.get_line(pin_num), button_dict[pin_num]) for pin_num in button_dict.keys()]
# led_line.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)

for (line, name) in button_lines:
    line.request(consumer="Button", type=gpiod.LINE_REQ_DIR_IN)

current_state = None


class Buttons:
    def __init__(self):

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

        self.states = {
                "Power": 0,  # to track the current state (on/off)
                "Home": 0,  # to track the current state (on/off)
                "Vol Up": 0,  # to track the current state (on/off)
                "Vol Down": 0,  # to track the current state (on/off)
                "Info": 0,  # to track the current state (on/off)
        }

    def check_pressed(self):
        for idx, (line, name) in enumerate(self.button_lines):
            button_state = line.get_value()

            if button_state and not self.states[name]:
                print(f"{name} Pressed")

            self.states[name] = button_state


while True:
    for idx, (line, name) in enumerate(button_lines):
        button_state = line.get_value()
        if button_state == 1:
            print(f"{name} Pressed")
