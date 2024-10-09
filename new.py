import adafruit_dht
from gpiozero import DistanceSensor, LED
from board import D4
from time import sleep

dht_sensor = adafruit_dht.DHT22(D4)
distance_sensor = DistanceSensor(echo=24, trigger=18)

green_led = LED(17)
yellow_led = LED(27)

MOVEMENT_THRESHOLD = 0.1
MAX_RETRIES = 5

def categorize_temperature(temp):
    if temp is None:
        return 'invalid'
    elif temp < 18:
        return 'cold'
    elif 18 <= temp <= 24:
        return 'moderate'
    else:
        return 'hot'

def categorize_humidity(humidity):
    if humidity is None:
        return 'invalid'
    elif humidity < 30:
        return 'low'
    elif 30 <= humidity <= 60:
        return 'moderate'
    else:
        return 'high'

def read_dht_sensor():
    for attempt in range(MAX_RETRIES):
        try:
            temperature = dht_sensor.temperature
            humidity = dht_sensor.humidity
            if temperature is not None and humidity is not None:
                return temperature, humidity
            else:
                print(f"Attempt {attempt + 1} failed, retrying...")
                sleep(2)  # Wait for 2 seconds before retrying
        except RuntimeError as error:
            print(f"Error reading DHT sensor (Attempt {attempt + 1}): {error}")
            sleep(2)  # Wait for 2 seconds before retrying
    return None, None  # Return None if all attempts fail


if __name__ == '__main__':
    try:
        sleep(2)  # Allow some time for the sensor to stabilize
        while True:
            dist = distance_sensor.distance
            print(f"Measured Distance = {dist * 100:.1f} cm")
            
            if dist < MOVEMENT_THRESHOLD:
                green_led.on()
                yellow_led.off()
            else:
                yellow_led.on()
                green_led.off()

            temperature, humidity = read_dht_sensor()

            if temperature is not None and humidity is not None:
                temp_category = categorize_temperature(temperature)
                humidity_category = categorize_humidity(humidity)

                print(f"Temperature: {temperature:.1f}°C, Category: {temp_category}")
                print(f"Humidity: {humidity:.1f}%, Category: {humidity_category}")

                if temp_category == 'hot':
                    print("Warning: The room is too hot!")
                elif temp_category == 'cold':
                    print("Warning: The room is too cold!")

                if humidity_category == 'high':
                    print("Warning: The humidity is too high!")
                elif humidity_category == 'low':
                    print("Warning: The humidity is too low!")
            else:
                print("Failed to get a valid reading from the DHT sensor after retries.")

            sleep(1)

    except KeyboardInterrupt:
        print("Measurement stopped by User")
        green_led.off()
        yellow_led.off()