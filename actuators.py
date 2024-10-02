# actuators.py

from gpiozero import LED, Button, OutputDevice

# LED setup
presence_led = LED(17)

# Push button setup
button = Button(27, pull_up=True)

# Light relay or LED setup (connected to GPIO 22)
light_relay = OutputDevice(22, active_high=True, initial_value=False)

def control_presence_led(presence):
    if presence:
        presence_led.on()
    else:
        presence_led.off()

def read_button_state():
    return button.is_pressed

def toggle_light_state(state):
    if state:
        light_relay.on()
    else:
        light_relay.off()
