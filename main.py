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

previous_distance = None

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
    global sensor_data, previous_distance
    while True:
        dist = distance_sensor.distance
        
        if previous_distance is not None:
            distance_change = abs(dist - previous_distance)
            
            if distance_change > MOVEMENT_THRESHOLD:
                green_led.on()  # Movement detected
                yellow_led.off()
            else:
                yellow_led.on()  # No significant movement
                green_led.off()
        
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

            sensor_data = {
                "distance": dist * 100,  # convert to cm
                "temperature": temperature,
                "humidity": humidity,
                "temp_category": temp_category,
                "humidity_category": humidity_category,
                "warnings": warnings
            }

        except RuntimeError as error:
            print(f"Error reading from DHT sensor: {error}")

