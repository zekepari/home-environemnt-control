import adafruit_dht
from gpiozero import DistanceSensor, LED
from board import D4
from time import sleep

dht_sensor = adafruit_dht.DHT22(D4)
distance_sensor = DistanceSensor(echo=24, trigger=18)

green_led = LED(17)
yellow_led = LED(27)

MOVEMENT_THRESHOLD = 0.1

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

if __name__ == '__main__':
    try:
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
            
            except RuntimeError as error:
                print(f"Error reading from DHT sensor: {error}")

            sleep(1)

    except KeyboardInterrupt:
        print("Measurement stopped by User")
        green_led.off()
        yellow_led.off()
