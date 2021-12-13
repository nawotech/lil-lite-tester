import openhtf as htf
from openhtf.core import base_plugs
from openhtf.util import conf
from lil_lite import LilLite
import flash_lil_lite
from time import sleep

conf.declare(
    'lil_lite_serial_port',
    default_value='/dev/cu.usbmodem01',
    description='lil lite serial port string')


class LilLitePlug(base_plugs.BasePlug):

    @conf.inject_positional_args
    def __init__(self, lil_lite_serial_port):
        self.lite = LilLite(lil_lite_serial_port)

    def connect(self):
        self.lite.connect()

    def get_vbat_v(self):
        return self.lite.get_vbat_v()

    def flash_test_app(self):
        flash_lil_lite.flash_test_firmware(self.lite.serial_port)
        sleep(2)  # wait for light to restart

    def flash_app(self):
        flash_lil_lite.flash_firmware(self.lite.serial_port)
        sleep(2)

    def clear_all_leds(self):
        self.lite.clear_all_leds()

    def set_led_color(self, led_num: int, r: int, g: int, b: int):
        self.lite.set_led_color(led_num, r, g, b)

    def get_vbat_v(self):
        return self.lite.get_vbat_v()

    def get_vbus(self):
        return self.lite.get_vbus()

    def get_button_pressed(self):
        return self.lite.get_button_pressed()

    def get_charge_stat(self):
        return self.lite.get_charge_stat()

    def get_charge_i_mA(self):
        return self.lite.get_charge_i_mA()

    def get_light_sensor_V(self):
        return self.lite.get_light_sensor_V()

    def sleep(self):
        self.lite.sleep()

    def set_switched_rail(self, on: bool):
        self.lite.set_switched_rail(on)

    def get_accel(self):
        return self.lite.get_accel()

    def get_accel_int(self):
        return self.lite.get_accel_int()

    def set_accel_self_test(self, enabled: bool):
        self.lite.set_accel_self_test(enabled)

    def set_accel_int_inactive_level(self, level: bool):
        self.lite.set_accel_int_inactive_level(level)
