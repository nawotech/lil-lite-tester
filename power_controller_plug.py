import openhtf as htf
from openhtf.core import base_plugs
from openhtf.util import conf
from power_controller import PowerController

conf.declare(
    'power_controller_serial_port',
    default_value='/dev/cu.usbserial-0148A89B',
    description='power controller serial port string')


class PowerControllerPlug(base_plugs.BasePlug):

    @conf.inject_positional_args
    def __init__(self, power_controller_serial_port):
        self.pwr_cntrl = PowerController(power_controller_serial_port)

    def set_vbat(self, vbat: float):
        self.pwr_cntrl.set_vbat(vbat)

    def get_vbat_v(self):
        return self.pwr_cntrl.get_vbat_v()

    def set_vbus_enable(self, on: bool):
        self.pwr_cntrl.set_vbus_enable(on)

    def get_vbus_v(self):
        return self.pwr_cntrl.get_vbus_v()

    def get_vbat_mA(self):
        return self.pwr_cntrl.get_vbat_mA()

    def get_vbus_mA(self):
        return self.pwr_cntrl.get_vbus_mA()

    def get_rgb(self):
        return self.pwr_cntrl.get_rgb()

    def set_servo_position(self, degrees: int):
        self.pwr_cntrl.set_servo_position(degrees)

    def reset(self):
        self.pwr_cntrl.reset()

    def reset_into_bootloader(self):
        self.pwr_cntrl.reset_into_bootloader
