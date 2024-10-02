# sensors.py

import time
import board
import adafruit_dht
from gpiozero import DistanceSensor

# DHT22 setup using adafruit-circuitpython-dht
dhtDevice = adafruit_dht.DHT22(board.D4)

# Ultrasonic sensor setup using gpiozero's DistanceSensor
ultrasonic_sensor = DistanceSensor(echo=24, trigger=23, max_distance=4)

def read_temperature_humidity():
    try:
        temperature = dhtDevice.temperature
        humidity = dhtDevice.humidity

        if humidity is None or temperature is None:
            print("Failed to retrieve data from humidity sensor")
            time.sleep(2)
            return read_temperature_humidity()
        return temperature, humidity
    except RuntimeError as error:
        # Reading doesn't always work; retry after a short delay
        print(f"DHT Reading error: {error.args[0]}")
        time.sleep(2)
        return read_temperature_humidity()
    except Exception as error:
        dhtDevice.exit()
        raise error

def detect_presence():
    distance = ultrasonic_sensor.distance * 100  # Convert to centimeters
    # Define presence detection threshold
    if distance < 100:  # Adjust this value as needed
        return True
    else:
        return False
