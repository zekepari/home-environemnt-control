# app.py

from flask import Flask, render_template, request, redirect, url_for
from actuators import toggle_light_state
from sensors import read_temperature_humidity, detect_presence

app = Flask(__name__)

light_state = False

@app.route('/')
def index():
    temperature, humidity = read_temperature_humidity()
    presence = detect_presence()
    return render_template(
        'index.html',
        temperature=temperature,
        humidity=humidity,
        presence=presence,
        light_state=light_state
    )

@app.route('/toggle_light', methods=['POST'])
def toggle_light():
    global light_state
    light_state = not light_state
    toggle_light_state(light_state)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
