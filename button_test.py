import gpiod

button_dict = {
    4: "Power",
    17: "info",
    27: "Home",
    22: "Vol_don",
    23: "Vol_up"
}
# LED_PIN = 17

chip = gpiod.Chip('gpiochip4')
# led_line = chip.get_line(LED_PIN)
button_lines = [chip.get_line(pin_num) for pin_num in range(5, 30)]
# led_line.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)
for line in button_lines:
    line.request(consumer="Button", type=gpiod.LINE_REQ_DIR_IN)

current_state = None

while True:
    for idx, line in enumerate(button_lines):
        button_state = line.get_value()
        if button_state == 1:
            print(f"{list(button_dict.values())[idx]} Pressed")
