import re
from time import strftime

import RPi.GPIO as GPIO
import Adafruit_DHT

import time_converter
from dht import DHT
from lcd import HD44780

import urllib
import json

# Length
LEN_CLOCK = 5
LEN_TEMP = 6
LEN_HUMIDITY = 5
LEN_SEPARATOR = 1
LEN_TIME = 3
LEN_DESTINATION_NUMBER = 3
LEN_DESTINATION = 8
LEN_SPACE = 1
LEN_FULLLINE = 20

METADATA_LINE = 0
INTERMEDIATE_LINE = 1
BUS_LINE_1 = 2
BUS_LINE_2 = 3

BUS_TIMES = {
    "22O": "https://api-ratp.pierre-grimaud.fr/v3/schedules/bus/22/ranelagh/A?_format=json",
    "52O": "https://api-ratp.pierre-grimaud.fr/v3/schedules/bus/52/ranelagh/A?_format=json",
    "M9M": "https://api-ratp.pierre-grimaud.fr/v3/schedules/metros/9/ranelagh/A?_format=json",
    "M9P": "https://api-ratp.pierre-grimaud.fr/v3/schedules/metros/9/ranelagh/R?_format=json",
    "32A": "https://api-ratp.pierre-grimaud.fr/v3/schedules/bus/32/porte_de_passy/A?_format=json",
    "32E": "https://api-ratp.pierre-grimaud.fr/v3/schedules/bus/32/la_muette_boulainvilliers/R?_format=json"
}

TRANSPORTS_TO_SHOW = [["22O", "52O"], ["M9M", "M9P"], ["32A", "32E"]]


def get_page(url):
    try:
        f = urllib.urlopen(url)
        output = f.read()
        json_output = json.loads(output)
        schedules = json_output['result']['schedules']
        return [
            schedules[0]['destination'].encode('utf-8'), schedules[0]['message'].encode('utf-8'),
            schedules[1]['destination'].encode('utf-8'), schedules[1]['message'].encode('utf-8')
        ]
    except:
        return connect_issue()


def unavailable():
    return ["NAV", "NAV", "NAV", "NAV"]


def connect_issue():
    return ["UNC", "UNC", "UNC", "UNC"]


class RATPWithExtras:
    def __init__(self, lcd_rs_pin, lcd_e_pin, lcd_db_pins, button_pin, dht_pin):
        # LCD
        self.lcd_rs_pin = lcd_rs_pin
        self.lcd_e_pin = lcd_e_pin
        self.lcd_db_pins = lcd_db_pins

        # Button
        self.button_pin = button_pin

        # DHT
        self.dht_type = Adafruit_DHT.DHT22
        self.dht_pin = dht_pin

        self.dht = DHT(self.dht_pin, self.dht_type)
        self.lcd = HD44780(self.lcd_e_pin, self.lcd_rs_pin, self.lcd_db_pins)
        self.cur_transport = 0
        self.transports = TRANSPORTS_TO_SHOW[self.cur_transport]

    def set_temp_if_there(self, temp, col, sign, length):
        temp_string = str(temp)
        if temp_string != "None":
            temp_string = str(round(temp, 1))
            self.lcd.message_at(METADATA_LINE, col, temp_string + sign, length)

    def set_humidity(self, temp, col, sign, length):
        temp_string = str(temp)
        if temp_string != "None":
            temp_string = str(round(temp, 1))
            self.lcd.message_at(METADATA_LINE, col, temp_string + sign, length)

    def set_trans(self, time, row):
        timings = time_converter.get_timings(time)

        if isinstance(timings, time_converter.RegularTimings):
            self.lcd.message_at(row, 4, timings.first_destination, LEN_DESTINATION)
            self.lcd.message_at(row, 12, " ", LEN_SPACE)
            self.lcd.message_at(row, 13, timings.first_timing, LEN_TIME)
            self.lcd.message_at(row, 16, "/", LEN_SEPARATOR)
            self.lcd.message_at(row, 17, timings.second_timing, LEN_TIME)
        elif isinstance(timings, time_converter.TimingIssue):
            self.lcd.message_at(row, 4, timings.message,
                                LEN_DESTINATION + LEN_SPACE + LEN_TIME + LEN_SEPARATOR + LEN_TIME)

    def update_destinations_temperature(self):
        next_first = get_page(BUS_TIMES[self.transports[0]])
        self.set_trans(next_first, BUS_LINE_1)

        next_second = get_page(BUS_TIMES[self.transports[1]])
        self.set_trans(next_second, BUS_LINE_2)

        self.lcd.message_at(METADATA_LINE, 0, strftime("%H:%M"), LEN_CLOCK)

        humidity, temp = self.dht.get_temp_humidity()

        temp_string = str(temp)
        if temp_string != "None":
            temp_string = str(round(temp, 1))
            self.lcd.message_at(METADATA_LINE, 7, temp_string + chr(223) + "C", LEN_TEMP)

        humidity_string = str(humidity)
        if humidity_string != "None":
            humidity_string = str(round(humidity, 1))
            self.lcd.message_at(METADATA_LINE, 15, humidity_string + "%", LEN_HUMIDITY)

    def init_gpio(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.button_pin, GPIO.IN)
        GPIO.add_event_detect(self.button_pin, GPIO.FALLING, callback=self.cycle)

        self.dht.init_gpio()
        self.lcd.init_gpio()

    # noinspection PyUnusedLocal
    def cycle(self, channel):
        self.cur_transport = (self.cur_transport + 1) % len(TRANSPORTS_TO_SHOW)
        self.transports = TRANSPORTS_TO_SHOW[self.cur_transport]
        self.set_destinations()
        self.update_destinations_temperature()

    def set_destinations(self):
        self.lcd.message_at(BUS_LINE_1, 0, self.transports[0][:-1], LEN_DESTINATION_NUMBER)
        self.lcd.message_at(BUS_LINE_2, 0, self.transports[1][:-1], LEN_DESTINATION_NUMBER)

        self.lcd.message_at(INTERMEDIATE_LINE, 0, "--------------------", LEN_FULLLINE)

    def clean(self):
        self.lcd.clear()
        GPIO.remove_event_detect(self.button_pin)
        GPIO.cleanup()
