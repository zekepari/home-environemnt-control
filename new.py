from gpiozero import DistanceSensor
from time import sleep

sensor = DistanceSensor(echo=24, trigger=18, max_distance=4)

if __name__ == '__main__':
    try:
        while True:
            dist = sensor.distance * 100
            print(f"Measured Distance = {dist:.1f} cm")
            sleep(1)

    except KeyboardInterrupt:
        print("Measurement stopped by User")
