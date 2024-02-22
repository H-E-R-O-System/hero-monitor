import gpiod

button_dict = {
    4: "Power",     # Pin number 7
    17: "info",     # Pin number 11
    27: "Home",     # Pin number 13
    22: "Vol_don",  # Pin number 15
    23: "Vol_up"    # Pin number 16
}
# LED_PIN = 17

chip = gpiod.Chip('gpiochip4')
# led_line = chip.get_line(LED_PIN)
button_lines = [(chip.get_line(pin_num), button_dict[pin_num]) for pin_num in button_dict.keys()]
# led_line.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)
for (line, name) in button_lines:
    line.request(consumer="Button", type=gpiod.LINE_REQ_DIR_IN)

current_state = None

while True:
    for idx, (line, name) in enumerate(button_lines):
        button_state = line.get_value()
        if button_state == 1:
            print(f"{name} Pressed")
