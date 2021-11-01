from power_controller import PowerController
from lil_lite import LilLite
from time import sleep
import pytest


@pytest.fixture(scope="session")  # only open serial port once for all tests
def power_controller():
    return PowerController("/dev/cu.usbserial-0148A89B")


@pytest.fixture
def battery_voltage():
    return 3.8


@pytest.fixture
def lite():
    return LilLite("/dev/cu.usbmodem01")


def clear_leds(lite: LilLite):
    for i in range(0, 6):
        lite.set_led_color(i, 0, 0, 0)


def set_and_check_battery(power_controller: PowerController, battery_voltage: float):
    power_controller.set_vbat(battery_voltage)
    # wait until VBAT is within target
    t = 0
    vmin = battery_voltage - 0.1
    vmax = battery_voltage + 0.1
    if battery_voltage == 0:
        vmax = 1.0
    while 1:
        vbat_v = power_controller.get_vbat_v()
        if(vbat_v >= vmin and vbat_v <= vmax):
            return
        assert(t < 20)  # if it takes > 2 sec, throw error
        sleep(0.1)
        t = t+1


def set_and_check_vbus(power_controller: PowerController, vbus_on: bool):
    power_controller.set_vbus_enable(vbus_on)
    if vbus_on:
        vmin = 4.25
        vmax = 5.2
    else:
        vmin = 0
        vmax = 1
    # wait until VBUS is within target
    t = 0
    while 1:
        vbus_v = power_controller.get_vbus_v()
        if(vbus_v >= vmin and vbus_v <= vmax):
            return
        assert(t < 20)  # if it takes > 2 sec, throw error
        sleep(0.1)
        t = t+1


@pytest.fixture
def battery_power_setup(power_controller, battery_voltage):
    set_and_check_vbus(power_controller, 0)
    set_and_check_battery(power_controller, battery_voltage)

@pytest.fixture
def vbus_power_setup(power_controller, battery_voltage):
    set_and_check_battery(power_controller, battery_voltage)
    set_and_check_vbus(power_controller, 1)


def test_battery_power_supply(power_controller, battery_voltage):
    # turn off power to light
    set_and_check_vbus(power_controller, 0)
    set_and_check_battery(power_controller, 0)

    # turn on power to light
    set_and_check_battery(power_controller, battery_voltage)
    sleep(2)

def test_button(battery_power_setup, power_controller: PowerController, lite: LilLite):
    power_controller.set_servo_position(90)
    
    # check button is not pressed
    button_pressed = lite.get_button_pressed()
    assert (not button_pressed)
    
    # press button and check it responds
    power_controller.set_servo_position(172)
    sleep(2)
    button_pressed = lite.get_button_pressed()
    assert (button_pressed)

    # unpress and confirm no longer pressed
    power_controller.set_servo_position(90)
    sleep(2)
    button_pressed = lite.get_button_pressed()
    assert (not button_pressed)

def test_battery_monitor(battery_power_setup, power_controller, lite):
    vbat_v_real = power_controller.get_vbat_v()
    vbat_v_lite = lite.get_vbat_v()
    assert(vbat_v_lite >= vbat_v_real -
           0.05 and vbat_v_lite <= vbat_v_real + 0.05)


def test_on_current_battery(battery_power_setup, power_controller, lite):
    lite.set_switched_rail(0)
    vbat_mA = power_controller.get_vbat_mA()
    assert(vbat_mA >= 25 and vbat_mA <= 35)


def test_switched_rail(battery_power_setup, power_controller, lite):
    lite.set_switched_rail(1)
    lite.set_led_color(0, 255, 255, 255)
    sleep(0.5)
    vbat_mA = power_controller.get_vbat_mA()
    assert(vbat_mA >= 50)
    lite.set_switched_rail(0)
    sleep(1)
    vbat_mA = power_controller.get_vbat_mA()
    assert(vbat_mA >= 25 and vbat_mA <= 35)


def test_leds(battery_power_setup, power_controller, lite):
    lite.set_switched_rail(1)
    sleep_time = 0.01
    sleep(sleep_time)
    for i in range(0, 6):
        # red
        lite.set_led_color(i, 255, 0, 0)
        sleep(sleep_time)
        r, g, b = power_controller.get_rgb()
        assert(r > 160 and g < 75 and b < 75)

        # green
        lite.set_led_color(i, 0, 255, 0)
        sleep(sleep_time)
        r, g, b = power_controller.get_rgb()
        assert(r < 50 and g > 140 and b < 100)

        # blue
        lite.set_led_color(i, 0, 0, 255)
        sleep(sleep_time)
        r, g, b = power_controller.get_rgb()
        assert(r < 50 and g < 100 and b > 140)

        # blank
        lite.set_led_color(i, 0, 0, 0)
        sleep(sleep_time)
        r, g, b = power_controller.get_rgb()
        assert(r < 25 and g < 25 and b < 25)


def test_light_sensor(battery_power_setup, lite):
    clear_leds(lite)

    lite.set_led_color(0, 255, 255, 255)
    sleep(0.05)
    v_sens = lite.get_light_sensor_V()
    assert(v_sens > 0.4 and v_sens < 0.6)

    lite.set_led_color(0, 0, 0, 0)
    sleep(0.05)
    v_sens = lite.get_light_sensor_V()
    assert(v_sens < 0.1)


def test_accel_int_pin(battery_power_setup, lite: LilLite):
    lite.set_accel_int_inactive_level(1)
    level = lite.get_accel_int()
    assert(level == 1)

    lite.set_accel_int_inactive_level(0)
    level = lite.get_accel_int()
    assert(level == 0)


def test_accel_sensor(battery_power_setup, lite: LilLite):
    # first save current axis readings
    lite.set_accel_self_test(0)
    x, y, z = lite.get_accel()

    # then enable self test, which adds 0.5G to each axis
    lite.set_accel_self_test(1)
    tx, ty, tz = lite.get_accel()

    assert(tx > x + 0.45)
    assert(ty > y + 0.45)
    assert(tz > z + 0.45)

    # lastly disable self test and make sure values are close to original
    lite.set_accel_self_test(0)
    fx, fy, fz = lite.get_accel()

    assert(fx > x - 0.05 and fx < x + 0.05)
    assert(fy > y - 0.05 and fy < y + 0.05)
    assert(fz > z - 0.05 and fz < z + 0.05)


def test_vbus_monitor(battery_power_setup, power_controller: PowerController, lite: LilLite):
    vbus = lite.get_vbus()
    assert(vbus == 0)

    set_and_check_vbus(power_controller, 1)
    vbus = lite.get_vbus()
    assert(vbus == 1)


def test_charger_current(vbus_power_setup, power_controller: PowerController, lite: LilLite):
    vbus_mA = power_controller.get_vbus_mA()
    vbat_mA = power_controller.get_vbat_mA()
    assert(vbus_mA > 90)
    assert(vbat_mA < -90 and vbat_mA > -130)


def test_charger_stat_pin(vbus_power_setup, power_controller: PowerController, lite: LilLite):
    charge_stat = lite.get_charge_stat()
    assert(charge_stat == 0)

    # now disconnect VBUS to stop charging and make sure stat goes high
    set_and_check_vbus(power_controller, 0)
    charge_stat = lite.get_charge_stat()
    assert(charge_stat == 1)
    

def test_charger_imon_pin(vbus_power_setup, power_controller: PowerController, lite: LilLite):
    charge_i_mA = lite.get_charge_i_mA()
    assert(charge_i_mA > 90 and charge_i_mA < 110)

    # now disconnect VBUS to stop charging and make charge monitor changes
    set_and_check_vbus(power_controller, 0)
    charge_i_mA = lite.get_charge_i_mA()
    assert(charge_i_mA < 5)


def test_power_input_select(battery_power_setup, power_controller: PowerController, lite: LilLite):
    # first from battery power, turn on 3 LEDs ~ 120mA total draw
    lite.set_switched_rail(1)
    lite.set_led_color(0, 255, 255, 255)
    lite.set_led_color(1, 255, 255, 255)
    lite.set_led_color(2, 0, 0, 0)
    vbus_mA = power_controller.get_vbus_mA()
    vbat_mA = power_controller.get_vbat_mA()
    assert(vbus_mA < 2)
    assert(vbat_mA > 110 and vbat_mA < 130)

    # now enable vbus, make sure current on vbus is correct
    set_and_check_vbus(power_controller, 1)
    vbus_mA = power_controller.get_vbus_mA()
    vbat_mA = power_controller.get_vbat_mA()
    assert(vbat_mA < -90) # battery charging
    assert(vbus_mA > 210 and vbat_mA < 240)
    clear_leds(lite)


def test_sleep(battery_power_setup, power_controller, lite):
    vbat_mA = power_controller.get_vbat_mA()
    assert(vbat_mA > 20)
    lite.sleep()
    sleep(2)
    vbat_mA = power_controller.get_vbat_mA()
    assert(vbat_mA < 0.2)