from gpiozero import Button, LED
from flask import Flask, render_template, jsonify
import adafruit_dht
from gpiozero import DistanceSensor, LED
from board import D4
from time import sleep
import threading

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

# Initialize sensor data
sensor_data = {
    "distance": None,
    "temperature": None,
    "humidity": None,
    "temp_category": None,
    "humidity_category": None,
    "warnings": [],
    "in_room": False,  # Track if someone is in the room
    "white_led_status": False  # Track white LED status
}

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
        sensor_data['white_led_status'] = False
    else:
        white_led.on()
        sensor_data['white_led_status'] = True

# Set up button to control the white LED
button.when_pressed = toggle_white_led

# Function to update sensor data
def update_sensor_data():
    global sensor_data, previous_distance, movement_detected, in_room
    while True:
        dist = distance_sensor.distance
        
        if previous_distance is not None:
            distance_change = abs(dist - previous_distance)
            
            if distance_change > MOVEMENT_THRESHOLD:
                green_led.on()  # Movement detected
                yellow_led.off()
                movement_detected = 0  # Reset no movement count

                # Room entry logic
                if not in_room:
                    sensor_data["in_room"] = True
                    in_room = True  # Person has entered the room
                    print("Someone has entered the room.")
                else:
                    print("Movement inside the room detected.")
            
            else:
                yellow_led.on()  # No significant movement
                green_led.off()
                movement_detected += 1

                # After 5 consecutive detections of no movement, we assume leaving
                if movement_detected >= NO_MOVEMENT_LIMIT:
                    if in_room:
                        sensor_data["in_room"] = False
                        in_room = False  # Person has left the room
                        print("Someone has left the room.")
                    else:
                        print("No movement, but no one is in the room.")

        previous_distance = dist  # Update the previous distance with the current one

        try:
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

            sensor_data.update({
                "distance": dist * 100,  # convert to cm
                "temperature": temperature,
                "humidity": humidity,
                "temp_category": temp_category,
                "humidity_category": humidity_category,
                "warnings": warnings
            })

        except RuntimeError as error:
            print(f"Error reading from DHT sensor: {error}")

        sleep(2/5)

# Start the sensor data update thread
sensor_thread = threading.Thread(target=update_sensor_data)
sensor_thread.daemon = True
sensor_thread.start()

# Flask routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def data():
    return jsonify(sensor_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
