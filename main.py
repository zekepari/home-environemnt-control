from flask import Flask, render_template, request
from gpiozero import LED

app = Flask(__name__)
leds = [LED(17), LED(16), LED(6)]

def fetch_states():
    return [bool(led.is_lit) for led in leds]

@app.route('/')
def index():
    for led in leds:
        led.on()

    return render_template('index.html', led_states=fetch_states())

@app.route('led/<int:ledNum>')
def led_control(ledNum):
    state = request.args.get('state')
    led = leds[ledNum - 1]

    if state == 'on':
        led.on()
    elif state == 'off':
        led.off()

    print(fetch_states())
    return render_template('index.html', led_states=fetch_states())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=50000)