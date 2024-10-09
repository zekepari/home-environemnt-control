import Adafruit_DHT
from gpiozero import DistanceSensor, LED
from time import sleep

sensor = DistanceSensor(echo=24, trigger=18)
green_led = LED(17)
yellow_led = LED(27)

DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4

MOVEMENT_THRESHOLD = 0.1

TEMP_CATEGORIES = {
    'cold': lambda t: t < 18,
    'moderate': lambda t: 18 <= t <= 24,
    'hot': lambda t: t > 24
}

HUMIDITY_CATEGORIES = {
    'low': lambda h: h < 30,
    'moderate': lambda h: 30 <= h <= 60,
    'high': lambda h: h > 60
}

def categorize_temperature(temp):
    for category, condition in TEMP_CATEGORIES.items():
        if condition(temp):
            return category
    return 'unknown'

def categorize_humidity(humidity):
    for category, condition in HUMIDITY_CATEGORIES.items():
        if condition(humidity):
            return category
    return 'unknown'

if __name__ == '__main__':
    try:
        while True:
            dist = sensor.distance
            print(f"Measured Distance = {dist * 100:.1f} cm")
            
            if dist < MOVEMENT_THRESHOLD:
                green_led.on()
                yellow_led.off()
            else:
                yellow_led.on()
                green_led.off()

            humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)

            if humidity is not None and temperature is not None:
                temp_category = categorize_temperature(temperature)
                humidity_category = categorize_humidity(humidity)

                print(f"Temperature: {temperature:.1f}°C, Category: {temp_category}")
                print(f"Humidity: {humidity:.1f}%, Category: {humidity_category}")

                # Alert based on categories
                if temp_category == 'hot':
                    print("Warning: The room is too hot!")
                elif temp_category == 'cold':
                    print("Warning: The room is too cold!")

                if humidity_category == 'high':
                    print("Warning: The humidity is too high!")
                elif humidity_category == 'low':
                    print("Warning: The humidity is too low!")
            else:
                print("Failed to retrieve data from the humidity sensor.")

            sleep(1)

    except KeyboardInterrupt:
        print("Measurement stopped by User")
        green_led.off()
        yellow_led.off()
