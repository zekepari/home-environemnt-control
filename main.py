from gpiozero import Button, LED
from flask import Flask, render_template, jsonify
import adafruit_dht
from gpiozero import DistanceSensor, LED
from board import D4
from time import sleep
import threading

app = Flask(__name__)

dht_sensor = adafruit_dht.DHT11(D4)
distance_sensor = DistanceSensor(echo=24, trigger=18)

green_led = LED(17)
yellow_led = LED(27)
white_led = LED(22)

button = Button(23)

MOVEMENT_THRESHOLD = 0.1
NO_MOVEMENT_LIMIT = 5

movement_detected = 0
in_room = False
previous_distance = None

sensor_data = {
    "distance": None,
    "temperature": None,
    "humidity": None,
    "temp_category": None,
    "humidity_category": None,
    "warnings": [],
    "in_room": False,
    "white_led_status": False
}

def categorize_temperature(temp):
    if temp < 18:
        return 'cold'
    elif 18 <= temp <= 24:
        return 'moderate'
    else:
        return 'hot'

def categorize_humidity(humidity):
    if humidity < 30:
        return 'low'
    elif 30 <= humidity <= 60:
        return 'moderate'
    else:
        return 'high'

def toggle_white_led():
    if white_led.is_lit:
        white_led.off()
        sensor_data['white_led_status'] = False
    else:
        white_led.on()
        sensor_data['white_led_status'] = True

button.when_pressed = toggle_white_led

def update_sensor_data():
    global sensor_data, previous_distance, movement_detected, in_room
    while True:
        dist = distance_sensor.distance
        
        if previous_distance is not None:
            distance_change = abs(dist - previous_distance)
            
            if distance_change > MOVEMENT_THRESHOLD:
                green_led.on()
                yellow_led.off()
                movement_detected = 0

                if not in_room:
                    sensor_data["in_room"] = True
                    in_room = True
            
            else:
                yellow_led.on()
                green_led.off()
                movement_detected += 1

                if movement_detected >= NO_MOVEMENT_LIMIT:
                    if in_room:
                        sensor_data["in_room"] = False
                        in_room = False

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
