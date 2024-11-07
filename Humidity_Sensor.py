import RPi.GPIO as GPIO
from RPLCD.gpio import CharLCD
import Adafruit_DHT
import time

# Pin configuration
DHT_PIN = 4                # DHT11 sensor GPIO pin
DHT_SENSOR = Adafruit_DHT.DHT11
HUMIDITY_THRESHOLD = 70    # Threshold for high humidity

# 7-segment display pin configuration
SEGMENT_PINS = {
    'A': 21, 'B': 20, 'C': 16, 'D': 12, 'E': 7, 'F': 8, 'G': 25
}

# LCD configuration (using 4-bit mode)
lcd = CharLCD(
    pin_rs=26, pin_rw=None, pin_e=19,
    pins_data=[13, 6, 5, 11],
    numbering_mode=GPIO.BCM,
    cols=16, rows=2
)

# Setup GPIO pins
GPIO.setmode(GPIO.BCM)
for pin in SEGMENT_PINS.values():
    GPIO.setup(pin, GPIO.OUT)

def display_humidity_on_lcd(humidity):
    """Displays humidity on the 16x2 LCD."""
    lcd.clear()
    lcd.write_string("Humidity: {}%".format(humidity))

def display_alert_on_7_segment(high_humidity):
    """Displays 'H' on the 7-segment display for high humidity alert."""
    if high_humidity:
        # Set segments to form the letter "H"
        GPIO.output(SEGMENT_PINS['A'], GPIO.LOW)
        GPIO.output(SEGMENT_PINS['B'], GPIO.HIGH)
        GPIO.output(SEGMENT_PINS['C'], GPIO.HIGH)
        GPIO.output(SEGMENT_PINS['D'], GPIO.LOW)
        GPIO.output(SEGMENT_PINS['E'], GPIO.HIGH)
        GPIO.output(SEGMENT_PINS['F'], GPIO.HIGH)
        GPIO.output(SEGMENT_PINS['G'], GPIO.HIGH)
    else:
        # Turn off all segments when humidity is normal
        for pin in SEGMENT_PINS.values():
            GPIO.output(pin, GPIO.LOW)

try:
    while True:
        # Read humidity from DHT11 sensor
        humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
        
        if humidity is not None:
            display_humidity_on_lcd(humidity)

            # Check if humidity exceeds the threshold
            if humidity > HUMIDITY_THRESHOLD:
                display_alert_on_7_segment(high_humidity=True)
            else:
                display_alert_on_7_segment(high_humidity=False)
        else:
            lcd.clear()
            lcd.write_string("Sensor Error")
        
        # Wait before the next reading
        time.sleep(2)

except KeyboardInterrupt:
    # Cleanup on exit
    lcd.clear()
    display_alert_on_7_segment(high_humidity=False)
    GPIO.cleanup()
