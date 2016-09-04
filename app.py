#!/usr/bin/python
import time
import logging

from ratp_with_extras import RATPWithExtras

# Parameters
REFRESH_TIME = 5

# Pins
LCD_RS_PIN = 9
LCD_E_PIN = 10
LCD_DB_PINS = [7, 8, 25, 11]
BUTTON_PIN = 24
DHT_PIN = 4

BUZZER_PIN = 2

logging.basicConfig(filename="ratp.log", level=logging.ERROR)

if __name__ == '__main__':
    ratp_with_extras = RATPWithExtras(LCD_RS_PIN, LCD_E_PIN, LCD_DB_PINS, BUTTON_PIN, DHT_PIN)

    try:
        ratp_with_extras.init_gpio()

        ratp_with_extras.set_destinations()

        while True:
            ratp_with_extras.update_destinations_temperature()
            time.sleep(REFRESH_TIME)

    except Exception:
        logging.exception("An exception has occurred!")

    finally:
        # Ensure a clean exit
        ratp_with_extras.clean()
