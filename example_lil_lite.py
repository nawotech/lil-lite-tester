from lil_lite import LilLite
from time import sleep

Lite = LilLite("/dev/cu.usbmodem01")

sleep(2)
Lite.set_led_color(3, 255, 0, 0)
sleep(2)
Lite.set_led_color(3, 0, 255, 0)
sleep(2)
Lite.set_led_color(3, 0, 0, 255)
