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

MOVEMENT_THRESHOLD = 0.1

sensor_data = {
    "distance": None,
    "temperature": None,
    "humidity": None,
    "temp_category": None,
    "humidity_category": None,
    "warnings": []
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

def update_sensor_data():
    global sensor_data
    while True:
        dist = distance_sensor.distance
        print(f"Measured Distance = {dist * 100:.1f} cm")

        if dist < MOVEMENT_THRESHOLD:
            green_led.on()
            yellow_led.off()
        else:
            yellow_led.on()
            green_led.off()

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

            sensor_data = {
                "distance": dist * 100,  # convert to cm
                "temperature": temperature,
                "humidity": humidity,
                "temp_category": temp_category,
                "humidity_category": humidity_category,
                "warnings": warnings
            }

            print(f"Temperature: {temperature:.1f}°C, Category: {temp_category}")
            print(f"Humidity: {humidity:.1f}%, Category: {humidity_category}")
            print(f"Warnings: {warnings}")

        except RuntimeError as error:
            print(f"Error reading from DHT sensor: {error}")

        sleep(1)

sensor_thread = threading.Thread(target=update_sensor_data)
sensor_thread.daemon = True
sensor_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def data():
    return jsonify(sensor_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
