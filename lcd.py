from RPi import GPIO
import thread
import threading
from time import sleep


class HD44780:
    lock = threading.Lock()

    def __init__(self, lcd_e_pin, lcd_rs_pin, lcd_db_pins):
        self.lcd_e_pin = lcd_e_pin
        self.lcd_rs_pin = lcd_rs_pin
        self.lcd_db_pins = lcd_db_pins

    def init_gpio(self):
        GPIO.setup(self.lcd_e_pin, GPIO.OUT)
        GPIO.setup(self.lcd_rs_pin, GPIO.OUT)
        for pin in self.lcd_db_pins:
            GPIO.setup(pin, GPIO.OUT)

        self.clear()

    def clear(self):
        self.cmd(0x2C, False)  # 0010 1100    Function set       1     DL     N     F     *     *
        self.cmd(0x0C, False)  # 0000 1100    Display on/off     1     D     C     B
        self.cmd(0x01, False)  # 0000 0001    Clear Display

    # Internal
    def set_position(self, row, col):
        row_offsets = [0x00, 0x40, 0x14, 0x54]
        command = 0x80 | (col + row_offsets[row])
        self.cmd(command, False)

    # Internal
    def message(self, text):
        for char in text:
            self.cmd(ord(char), True)

    def message_at(self, row, col, text, length):
        displayed_text = text[:length]
        displayed_text = displayed_text.ljust(length, ' ')
        self.message_at_static(row, col, displayed_text)

    def message_at_static(self, row, col, text):
        with self.lock:
            self.set_position(row, col)
            self.message(text)

    def cmd(self, bits, char_mode):
        sleep(0.001)
        bits = bin(bits)[2:].zfill(8)

        GPIO.output(self.lcd_rs_pin, char_mode)

        for pin in self.lcd_db_pins:
            GPIO.output(pin, GPIO.LOW)

        for i in range(4):
            if bits[i] == "1":
                GPIO.output(self.lcd_db_pins[::-1][i], GPIO.HIGH)

        GPIO.output(self.lcd_e_pin, GPIO.HIGH)
        GPIO.output(self.lcd_e_pin, GPIO.LOW)

        for pin in self.lcd_db_pins:
            GPIO.output(pin, GPIO.LOW)

        for i in range(4, 8):
            if bits[i] == "1":
                GPIO.output(self.lcd_db_pins[::-1][i - 4], GPIO.HIGH)

        GPIO.output(self.lcd_e_pin, GPIO.HIGH)
        GPIO.output(self.lcd_e_pin, GPIO.LOW)

    def scrolling_message(self, text, x, y, size):
        thread.start_new_thread(scroll_text, (self, text, x, y, size))


# BETA
def scroll_text(lcd, text, x, y, size):
    text = text.strip()

    # displayedText = text.ljust(size)
    # lcd.messageAt(x, y, displayedText)
    # sleep(1)

    original_text = text
    text = text[:max(size, len(text))]
    while True:
        displayed_text = text.ljust(size)
        lcd.message_at(x, y, displayed_text)

        if text == original_text:
            sleep(2)
        else:
            sleep(.25)

        if len(text) >= 1:
            text = text[1:]
        else:
            text = original_text
