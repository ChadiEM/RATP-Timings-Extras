import RPi.GPIO as GPIO
import Adafruit_DHT


# Assume GPIO already set up

class DHT:
    def __init__(self, dht_pin, dht_type):
        self.dht_pin = dht_pin
        self.dht_type = dht_type

    def init_gpio(self):
        GPIO.setup(self.dht_pin, GPIO.OUT)

    def get_temp_humidity(self):
        hum, temp = Adafruit_DHT.read(self.dht_type, self.dht_pin)
        return hum, temp
