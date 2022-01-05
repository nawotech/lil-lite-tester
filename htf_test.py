import yaml
import openhtf as htf
from time import sleep

from openhtf.output.callbacks import console_summary
from openhtf.output.callbacks import json_factory
from openhtf.output.callbacks import mfg_inspector
from openhtf.output.proto import mfg_event_converter
from openhtf.util import conf

from openhtf.output.servers import station_server
from openhtf.output.web_gui import web_launcher
from openhtf.plugs import user_input

from power_controller_plug import PowerControllerPlug
from lil_lite_plug import LilLitePlug

from flash_lil_lite import flash_test_firmware


@htf.plug(lite=LilLitePlug)
def setup_lite(test, lite: LilLitePlug):
    lite.connect()
    lite.clear_all_leds()


@htf.plug(pwr_cntrl=PowerControllerPlug)
@htf.measures(htf.Measurement('vbat_voltage').with_units('V').in_range(minimum=3.6, maximum=3.75))
@htf.measures(htf.Measurement('vbus_voltage').with_units('V').in_range(minimum=0.0, maximum=1.0))
def setup_battery_power(test, pwr_cntrl: PowerControllerPlug):
    pwr_cntrl.set_vbat(3.7)
    pwr_cntrl.set_vbus_enable(0)
    test.measurements.vbat_voltage = pwr_cntrl.get_vbat_v()
    test.measurements.vbus_voltage = pwr_cntrl.get_vbus_v()


@htf.plug(pwr_cntrl=PowerControllerPlug)
@htf.measures(htf.Measurement('vbat_voltage').with_units('V').in_range(minimum=3.6, maximum=3.75))
@htf.measures(htf.Measurement('vbus_voltage').with_units('V').in_range(minimum=4.2, maximum=5.2))
def setup_usb_power(test, pwr_cntrl: PowerControllerPlug):
    pwr_cntrl.set_vbat(3.7)
    pwr_cntrl.set_vbus_enable(1)
    test.measurements.vbat_voltage = pwr_cntrl.get_vbat_v()
    test.measurements.vbus_voltage = pwr_cntrl.get_vbus_v()


@htf.plug(lite=LilLitePlug)
@htf.plug(pwr_cntrl=PowerControllerPlug)
def flash_test_firmware(test, lite: LilLitePlug, pwr_cntrl: PowerControllerPlug):
    pwr_cntrl.reset_into_bootloader()
    sleep(3)
    lite.flash_test_app()
    pwr_cntrl.reset()


@htf.plug(lite=LilLitePlug)
@htf.measures(htf.Measurement('monitor_vbat_voltage').with_units('V').in_range(minimum=3.6, maximum=3.75))
def battery_monitor(test, lite: LilLitePlug):
    lite.set_switched_rail(1)
    sleep(0.1)
    test.measurements.monitor_vbat_voltage = lite.get_vbat_v()


@htf.plug(lite=LilLitePlug)
@htf.plug(pwr_cntrl=PowerControllerPlug)
@htf.measures(htf.Measurement('button_not_pressed').equals(0))
@htf.measures(htf.Measurement('button_pressed').equals(1))
@htf.measures(htf.Measurement('button_not_pressed_end').equals(0))
def button(test, lite: LilLitePlug, pwr_cntrl: PowerControllerPlug):
    pwr_cntrl.set_servo_position(90)
    test.measurements.button_not_pressed = lite.get_button_pressed()
    pwr_cntrl.set_servo_position(172)
    sleep(2)
    test.measurements.button_pressed = lite.get_button_pressed()
    pwr_cntrl.set_servo_position(90)
    sleep(2)
    test.measurements.button_not_pressed_end = lite.get_button_pressed()


@htf.plug(lite=LilLitePlug)
@htf.plug(pwr_cntrl=PowerControllerPlug)
@htf.measures(
    htf.Measurement('vbat_current_rail_on').with_units(
        'mA').in_range(minimum=50, maximum=100),
    htf.Measurement('vbat_current_rail_off').with_units(
        'mA').in_range(minimum=25, maximum=35)
)
def switched_rail(test, lite: LilLitePlug, pwr_cntrl: PowerControllerPlug):
    lite.set_switched_rail(1)
    sleep(0.2)
    lite.set_led_color(0, 255, 255, 255)
    sleep(0.2)
    test.measurements.vbat_current_rail_on = pwr_cntrl.get_vbat_mA()
    lite.set_switched_rail(0)
    sleep(0.2)
    test.measurements.vbat_current_rail_off = pwr_cntrl.get_vbat_mA()


@htf.plug(lite=LilLitePlug)
@htf.plug(pwr_cntrl=PowerControllerPlug)
# define limits for color sensor with each color LED on
@htf.measures(
    *(htf.Measurement('led_{}_red_read_red'.format(n)).in_range(minimum=160)
      for n in range(0, 6)),
    *(htf.Measurement('led_{}_red_read_green'.format(n)).in_range(maximum=75)
      for n in range(0, 6)),
    *(htf.Measurement('led_{}_red_read_blue'.format(n)).in_range(maximum=75)
      for n in range(0, 6)),
    *(htf.Measurement('led_{}_green_read_red'.format(n)).in_range(maximum=50)
      for n in range(0, 6)),
    *(htf.Measurement('led_{}_green_read_green'.format(n)).in_range(minimum=140)
      for n in range(0, 6)),
    *(htf.Measurement('led_{}_green_read_blue'.format(n)).in_range(maximum=100)
      for n in range(0, 6)),
    *(htf.Measurement('led_{}_blue_read_red'.format(n)).in_range(maximum=50)
      for n in range(0, 6)),
    *(htf.Measurement('led_{}_blue_read_green'.format(n)).in_range(maximum=100)
      for n in range(0, 6)),
    *(htf.Measurement('led_{}_blue_read_blue'.format(n)).in_range(minimum=140)
      for n in range(0, 6)),
    *(htf.Measurement('led_{}_blank_read_red'.format(n)).in_range(maximum=25)
      for n in range(0, 6)),
    *(htf.Measurement('led_{}_blank_read_green'.format(n)).in_range(maximum=25)
      for n in range(0, 6)),
    *(htf.Measurement('led_{}_blank_read_blue'.format(n)).in_range(maximum=25)
      for n in range(0, 6)),
)
def led(test, lite: LilLitePlug, pwr_cntrl: PowerControllerPlug):
    lite.set_switched_rail(1)
    sleep(0.2)
    for n in range(0, 6):
        for color in ('red', 'green', 'blue', 'blank'):
            if color == 'red':
                lite.set_led_color(n, 255, 0, 0)
            elif color == 'green':
                lite.set_led_color(n, 0, 255, 0)
            elif color == 'blue':
                lite.set_led_color(n, 0, 0, 255)
            elif color == 'blank':
                lite.set_led_color(n, 0, 0, 0)
            sleep(0.01)
            r, g, b = pwr_cntrl.get_rgb()
            test.measurements['led_{}_{}_read_red'.format(n, color)] = r
            test.measurements['led_{}_{}_read_green'.format(n, color)] = g
            test.measurements['led_{}_{}_read_blue'.format(n, color)] = b


@htf.plug(lite=LilLitePlug)
@htf.measures(htf.Measurement('light_level_led_on').with_units('V').in_range(minimum=0.4, maximum=0.6))
@htf.measures(htf.Measurement('light_level_led_off').with_units('V').in_range(maximum=0.1))
def light_sensor(test, lite: LilLitePlug):
    lite.set_led_color(0, 255, 255, 255)
    sleep(0.05)
    test.measurements.light_level_led_on = lite.get_light_sensor_V()

    lite.set_led_color(0, 0, 0, 0)
    sleep(0.05)
    test.measurements.light_level_led_off = lite.get_light_sensor_V()


@htf.plug(lite=LilLitePlug)
@htf.plug(pwr_cntrl=PowerControllerPlug)
@htf.measures(
    htf.Measurement('accel_int_high').equals(1),
    htf.Measurement('accel_int_low').equals(0)
)
def accel_int_pin(test, lite: LilLitePlug, pwr_cntrl: PowerControllerPlug):
    lite.set_accel_int_inactive_level(1)
    test.measurements.accel_int_high = lite.get_accel_int()
    lite.set_accel_int_inactive_level(0)
    test.measurements.accel_int_low = lite.get_accel_int()


@htf.plug(lite=LilLitePlug)
@htf.plug(pwr_cntrl=PowerControllerPlug)
@htf.measures(
    *(htf.Measurement('accel_{}_change_self_test'.format(axis)
                      ).with_units('g').in_range(minimum=0.40, maximum=0.60) for axis in ['x', 'y', 'z']),
    *(htf.Measurement('accel_{}_change_no_self_test'.format(axis)).with_units('g').in_range(maximum=0.1) for axis in ['x', 'y', 'z'])
)
def accel_sensor(test, lite: LilLitePlug, pwr_cntrl: PowerControllerPlug):
    # first save current axis readings
    lite.set_accel_self_test(0)
    x, y, z = lite.get_accel()

    # then enable self test, which adds 0.5G to each axis
    lite.set_accel_self_test(1)
    tx, ty, tz = lite.get_accel()

    test.measurements.accel_x_change_self_test = tx - x
    test.measurements.accel_y_change_self_test = ty - y
    test.measurements.accel_z_change_self_test = tz - z

    # lastly disable self test and make sure values are close to original
    lite.set_accel_self_test(0)
    fx, fy, fz = lite.get_accel()

    test.measurements.accel_x_change_no_self_test = fx - x
    test.measurements.accel_y_change_no_self_test = fy - y
    test.measurements.accel_z_change_no_self_test = fz - z


@htf.plug(lite=LilLitePlug)
@htf.plug(pwr_cntrl=PowerControllerPlug)
@htf.measures(
    htf.Measurement('vbus_current').with_units(
        'mA').in_range(minimum=90, maximum=160),
    htf.Measurement('vbat_current').with_units(
        'mA').in_range(minimum=-130, maximum=-90)
)
def charger_current(test, pwr_cntrl: PowerControllerPlug, lite: LilLitePlug):
    lite.set_switched_rail(0)
    pwr_cntrl.set_vbus_enable(1)
    sleep(2)
    test.measurements.vbus_current = pwr_cntrl.get_vbus_mA()
    test.measurements.vbat_current = pwr_cntrl.get_vbat_mA()


@htf.plug(pwr_cntrl=PowerControllerPlug)
@htf.plug(lite=LilLitePlug)
@htf.measures(
    htf.Measurement('vbus_connected').equals(1),
    htf.Measurement('vbus_disconnected').equals(0)
)
def vbus_monitor(test, pwr_cntrl: PowerControllerPlug, lite: LilLitePlug):
    test.measurements.vbus_connected = lite.get_vbus()
    pwr_cntrl.set_vbus_enable(0)
    sleep(1)
    test.measurements.vbus_disconnected = lite.get_vbus()


@htf.plug(lite=LilLitePlug)
@htf.plug(pwr_cntrl=PowerControllerPlug)
@htf.measures(
    htf.Measurement('not_charging').equals(1),
    htf.Measurement('charging').equals(0)
)
def charger_stat_pin(test, lite: LilLitePlug, pwr_cntrl: PowerControllerPlug):
    pwr_cntrl.set_vbus_enable(0)
    test.measurements.not_charging = lite.get_charge_stat()
    pwr_cntrl.set_vbus_enable(1)
    sleep(1)
    test.measurements.charging = lite.get_charge_stat()


@htf.plug(lite=LilLitePlug)
@htf.plug(pwr_cntrl=PowerControllerPlug)
@htf.measures(
    htf.Measurement('monitor_charging').with_units(
        'mA').in_range(minimum=90, maximum=110),
    htf.Measurement('monitor_not_charging').with_units(
        'mA').in_range(maximum=5)
)
def charger_i_monitor(test, lite: LilLitePlug, pwr_cntrl: PowerControllerPlug):
    pwr_cntrl.set_vbus_enable(1)
    sleep(1)
    test.measurements.monitor_charging = lite.get_charge_i_mA()
    pwr_cntrl.set_vbus_enable(0)
    sleep(1)
    test.measurements.monitor_not_charging = lite.get_charge_i_mA()


@htf.plug(lite=LilLitePlug)
@htf.plug(pwr_cntrl=PowerControllerPlug)
@htf.measures(
    htf.Measurement('vbus_current_vbus_selected').with_units(
        'mA').in_range(minimum=190, maximum=260),
    htf.Measurement('vbat_current_vbus_selected').with_units(
        'mA').in_range(minimum=-130, maximum=-90),
    htf.Measurement('vbus_current_vbat_selected').with_units(
        'mA').in_range(maximum=2),
    htf.Measurement('vbat_current_vbat_selected').with_units(
        'mA').in_range(minimum=90, maximum=130)
)
def power_input_select(test, lite: LilLitePlug, pwr_cntrl: PowerControllerPlug):
    pwr_cntrl.set_vbus_enable(0)
    lite.set_switched_rail(1)
    sleep(1)
    lite.set_led_color(0, 255, 255, 255)
    lite.set_led_color(1, 255, 255, 255)
    sleep(0.5)

    test.measurements.vbus_current_vbat_selected = pwr_cntrl.get_vbus_mA()
    test.measurements.vbat_current_vbat_selected = pwr_cntrl.get_vbat_mA()

    pwr_cntrl.set_vbus_enable(1)
    sleep(1)
    test.measurements.vbus_current_vbus_selected = pwr_cntrl.get_vbus_mA()
    test.measurements.vbat_current_vbus_selected = pwr_cntrl.get_vbat_mA()
    lite.clear_all_leds()


@htf.plug(lite=LilLitePlug)
@htf.plug(pwr_cntrl=PowerControllerPlug)
@htf.measures(
    htf.Measurement('vbat_current_on').with_units('mA').in_range(minimum=20),
    htf.Measurement('vbat_current_wake').with_units(
        'mA').in_range(minimum=-130, maximum=-90),
    htf.Measurement('vbat_current_sleep').with_units(
        'mA').in_range(maximum=0.2)
)
def power_sleep(test, lite: LilLitePlug, pwr_cntrl: PowerControllerPlug):
    pwr_cntrl.set_vbus_enable(0)
    sleep(0.1)
    test.measurements.vbat_current_on = pwr_cntrl.get_vbat_mA()
    lite.sleep()
    sleep(2)
    test.measurements.vbat_current_sleep = pwr_cntrl.get_vbat_mA()
    pwr_cntrl.set_vbat(0.0)
    sleep(1)
    pwr_cntrl.set_vbus_enable(1)
    sleep(3)
    test.measurements.vbat_current_wake = pwr_cntrl.get_vbat_mA()


@htf.plug(lite=LilLitePlug)
def flash_app_firmware(test, lite: LilLitePlug):
    lite.flash_app()


if __name__ == '__main__':

    f = open('tester_config.yaml')
    config_dict = yaml.safe_load(f)
    conf.load_from_dict(config_dict)

    interface = mfg_inspector.MfgInspector()
    interface.set_converter(mfg_event_converter.mfg_event_from_test_record)

    with station_server.StationServer(history_path='./test_history') as server:

        while 1:
            test = htf.Test(
                setup_usb_power,
                flash_test_firmware,
                setup_lite,
                setup_battery_power,
                vbus_monitor,
                battery_monitor,
                button,
                switched_rail,
                led,
                accel_int_pin,
                accel_sensor,
                light_sensor,
                charger_current,
                vbus_monitor,
                charger_stat_pin,
                charger_i_monitor,
                power_input_select,
                power_sleep,
                flash_app_firmware)

            test.add_output_callbacks(console_summary.ConsoleSummary())
            test.add_output_callbacks(json_factory.OutputToJSON(
                './test_runs/{dut_id}.json', indent=2))
            test.add_output_callbacks(interface.save_to_disk(
                './test_history/mfg_event_{dut_id}_{start_time_millis}.pb'))

            test.add_output_callbacks(server.publish_final_state)

            test.execute(test_start=user_input.prompt_for_test_start())
