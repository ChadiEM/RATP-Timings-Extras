# RATP timings + Extras

## Hardware Requirements
- Raspberry PI
- 20x4 LCD (16x2 LCD may also work, but code needs to be adapted accordingly)
- DHT22 Temperature / Humidity sensor
- Cables, resistors, etc..
- Push button to change the timing "channel" (you can do without, requires code adaptation)
- Optional: Buzzer to buzz on some particular events

## Software Requirements
- Python 2
- Adafruit_DHT Python module

## Circuit
I will not go into the details of the circuitry. You can find plenty of tutorials for connecting the 20x4 LCD, DHT22, and push button to your Raspberry PI.
You will need to take note of the LCD, DHT, and button pins:
- LCD RS PIN (1)
- LCD E PIN (1)
- LCD DB PINS (4)
- DHT PIN (1)
- BUTTON PIN (1)

## Running
- Modify the pins in `app.py`.
- Run `python app.py` as root.

## Example output
![Example Output](http://i.imgur.com/CuCOhof.jpg)