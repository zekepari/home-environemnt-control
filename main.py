from gpiozero import Button, LED
from flask import Flask, render_template, jsonify
import adafruit_dht
from gpiozero import DistanceSensor, LED
from board import D4
from time import sleep

app = Flask(__name__)

# Initialize sensors
dht_sensor = adafruit_dht.DHT11(D4)
distance_sensor = DistanceSensor(echo=24, trigger=18)

# Initialize LEDs
green_led = LED(17)
yellow_led = LED(27)
white_led = LED(22)  # New white LED for room light

# Initialize button
button = Button(23)  # Button to control the white LED

MOVEMENT_THRESHOLD = 0.1  # Threshold for detecting movement
NO_MOVEMENT_LIMIT = 5  # Number of readings to assume no movement (for entry/exit logic)

# State tracking
movement_detected = 0  # Count of consecutive detections with no significant change
in_room = False  # Assume nobody is in the room initially
previous_distance = None  # To store the previous distance value
movement_after_no_movement = False  # To track if we detect movement after no movement period

# Function to categorize temperature
def categorize_temperature(temp):
    if temp < 18:
        return 'cold'
    elif 18 <= temp <= 24:
        return 'moderate'
    else:
        return 'hot'

# Function to categorize humidity
def categorize_humidity(humidity):
    if humidity < 30:
        return 'low'
    elif 30 <= humidity <= 60:
        return 'moderate'
    else:
        return 'high'

# Function to toggle the white LED
def toggle_white_led():
    if white_led.is_lit:
        white_led.off()
    else:
        white_led.on()

# Set up button to control the white LED
button.when_pressed = toggle_white_led

# Function to retrieve sensor data dynamically
def get_sensor_data():
    global previous_distance, movement_detected, in_room, movement_after_no_movement
    try:
        # Read distance sensor data
        dist = distance_sensor.distance
        distance_change = None
        if previous_distance is not None:
            distance_change = abs(dist - previous_distance)

        if distance_change is not None and distance_change > MOVEMENT_THRESHOLD:
            green_led.on()  # Movement detected
            yellow_led.off()

            if not in_room:
                # First movement, assume entry into the room
                in_room = True
                print("Someone has entered the room.")
            elif movement_detected >= NO_MOVEMENT_LIMIT:
                # Movement after no movement period, assume exit
                in_room = False
                movement_after_no_movement = False
                print("Someone has left the room.")

            # Reset movement detection counter since there is movement
            movement_detected = 0

        else:
            yellow_led.on()  # No significant movement
            green_led.off()

            movement_detected += 1
            if movement_detected >= NO_MOVEMENT_LIMIT and in_room:
                # We are in a state where no movement was detected for 5 cycles
                # Set the flag to track if we see movement again (assume they are leaving)
                movement_after_no_movement = True

        previous_distance = dist  # Update the previous distance with the current one

        # Read DHT sensor data
        temperature = dht_sensor.temperature
        humidity = dht_sensor.humidity

        temp_category = categorize_temperature(temperature)
        humidity_category = categorize_humidity(humidity)

        warnings = []

        if temp_category == 'hot':
            warnings.append("Warning: The room is too hot!")
        elif temp_category == 'cold':
            warnings.append("Warning: The room is too cold!")

        if humidity_category == 'high':
            warnings.append("Warning: The humidity is too high!")
        elif humidity_category == 'low':
            warnings.append("Warning: The humidity is too low!")

        # Return the latest sensor data
        sensor_data = {
            "distance": dist * 100,  # convert to cm
            "temperature": temperature,
            "humidity": humidity,
            "temp_category": temp_category,
            "humidity_category": humidity_category,
            "warnings": warnings,
            "in_room": in_room,
            "white_led_status": white_led.is_lit
        }

        return sensor_data

    except RuntimeError as error:
        print(f"Error reading from sensors: {error}")
        return {}

# Flask routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def data():
    sensor_data = get_sensor_data()  # Fetch the latest sensor data dynamically
    return jsonify(sensor_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
