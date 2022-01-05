from power_controller import PowerController
from lil_lite import LilLite
from time import sleep
from flash_lil_lite import flash_test_firmware, flash_firmware

Pwr = PowerController("/dev/tty.usbserial-0148A89B")

"""
print("power off")
Pwr.set_vbus_enable(0)
Pwr.set_vbat(0.0)
while Pwr.get_vbus_v() > 1.0:
    print(".")
    sleep(0.5)
print(Pwr.get_vbus_v())
"""
print("Enable VBUS")
Pwr.set_vbat(3.7)
Pwr.set_vbus_enable(0)
while Pwr.get_vbat_v() < 3:
    print(".")
    sleep(0.5)
print(Pwr.get_vbat_v())
 
while True:
    print(Pwr.get_vbat_mA())
    sleep(3)
"""
print("Reset lite into bootloader")
Pwr.reset_into_bootloader()

print("flash firmware")

"""
print("reset lite")
Pwr.reset()
"""
print("flash app")
flash_firmware("/dev/tty.usbmodem01")
"""