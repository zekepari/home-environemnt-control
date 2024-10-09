from gpiozero import DistanceSensor
from time import sleep

# Set up the DistanceSensor using GPIO pins
sensor = DistanceSensor(echo=24, trigger=18)

if __name__ == '__main__':
    try:
        while True:
            dist = sensor.distance * 100  # Convert distance to cm
            print(f"Measured Distance = {dist:.1f} cm")
            sleep(1)

    except KeyboardInterrupt:
        print("Measurement stopped by User")
