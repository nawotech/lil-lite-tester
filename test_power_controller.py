from power_controller import PowerController
from time import sleep


def set_and_check_power(PwrCnt, vbat: float, vbus: bool):
    PwrCnt.set_vbus_enable(vbus)
    PwrCnt.set_vbat(vbat)
    sleep(0.5)

    PwrCnt.get_new_reading()
    vbat = PwrCnt.get_vbat_v()
    vbus = PwrCnt.get_vbus_v()
    vbat_min = vbat - 0.1
    vbat_max = vbat + 0.1

    if vbus:
        vbus_min = 4.3
        vbus_max = 5.2
    else:
        vbus_min = 0.0
        vbus_max = 0.5

    assert(vbat >= vbat_min and vbat <= vbat_max)
    assert(vbus >= vbus_min and vbus <= vbus_max)


def test_power_vbat():
    PwrControl = PowerController("/dev/cu.usbserial-14220")
    sleep(1)

    # remove power to reset light
    set_and_check_power(PwrControl, 0, 0)

    sleep(1)

    # apply battery to light
    set_and_check_power(PwrControl, 3.7, 0)

    sleep(1)


def test_power_vbus():
    PwrControl = PowerController("/dev/cu.usbserial-14220")
    sleep(1)

    # apply battery to light
    set_and_check_power(PwrControl, 3.7, 0)

    sleep(1)

    # apply vbus to light
    set_and_check_power(PwrControl, 3.7, 1)

    sleep(1)
