# main.py

import time
from sensors import read_temperature_humidity, detect_presence
from actuators import control_presence_led, read_button_state, toggle_light_state
from cloud import log_data_to_cloud
from alerts import send_email_alert

# Threshold settings
TEMP_THRESHOLD_HIGH = 30  # Degrees Celsius
TEMP_THRESHOLD_LOW = 15
HUMIDITY_THRESHOLD_HIGH = 70  # Percentage
HUMIDITY_THRESHOLD_LOW = 30

# Initial device states
light_state = False

def main():
    global light_state
    while True:
        # Read sensor data
        temperature, humidity = read_temperature_humidity()
        presence = detect_presence()
        button_pressed = read_button_state()

        # Control LEDs based on presence
        control_presence_led(presence)

        # Toggle light if button is pressed
        if button_pressed:
            light_state = not light_state
            toggle_light_state(light_state)
            print(f"Light state toggled to: {'ON' if light_state else 'OFF'}")
            time.sleep(0.2)  # Debounce delay

        # Check environmental thresholds and send alerts
        if temperature > TEMP_THRESHOLD_HIGH or temperature < TEMP_THRESHOLD_LOW:
            send_email_alert(
                subject="Temperature Alert",
                message=f"Temperature is out of range: {temperature:.2f}°C"
            )

        if humidity > HUMIDITY_THRESHOLD_HIGH or humidity < HUMIDITY_THRESHOLD_LOW:
            send_email_alert(
                subject="Humidity Alert",
                message=f"Humidity is out of range: {humidity:.2f}%"
            )

        # Log data to the cloud
        log_data_to_cloud(
            temperature=temperature,
            humidity=humidity,
            presence=presence,
            light_state=light_state
        )

        # Wait before the next iteration
        time.sleep(5)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Program terminated by user.")
