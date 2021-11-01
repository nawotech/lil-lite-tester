from serial import Serial
import json


class LilLite():
    def __init__(self, serial_port: str):
        self.serial_port = serial_port
    
    def connect(self):
        self.ser = Serial(self.serial_port, 115200, timeout=0.5)

    def write_command(self, command: str):
        self.ser.write(command.encode('utf-8'))

    def get_new_reading(self):
        self.write_command("R")
        this_line = self.ser.readline()
        self.vals = json.loads(this_line)

    def clear_all_leds(self):
        for i in range(0, 6):
            self.set_led_color(i, 0, 0, 0)

    def set_led_color(self, led_num: int, r: int, g: int, b: int):
        command = "L {} {} {} {}".format(led_num, r, g, b)
        self.write_command(command)
        self.write_command(command)

    def get_vbat_v(self):
        self.get_new_reading()
        return self.vals["vbat_v"]

    def get_vbus(self):
        self.get_new_reading()
        return self.vals["vbus"]

    def get_button_pressed(self):
        self.get_new_reading()
        return self.vals["button_pressed"]

    def get_charge_stat(self):
        self.get_new_reading()
        return self.vals["charge_stat"]

    def get_charge_i_mA(self):
        self.get_new_reading()
        return self.vals["charge_i_mA"]

    def get_light_sensor_V(self):
        self.get_new_reading()
        return self.vals["light_sensor_V"]

    def sleep(self):
        self.write_command("S")

    def set_switched_rail(self, on: bool):
        command = "E {}".format(on)
        self.write_command(command)
        self.write_command(command)

    def get_accel(self):
        self.get_new_reading()
        x = self.vals["accel_x"]
        y = self.vals["accel_y"]
        z = self.vals["accel_z"]
        return x, y, z

    def get_accel_int(self):
        self.get_new_reading()
        return self.vals["accel_int"]

    def set_accel_self_test(self, enabled: bool):
        if enabled:
            self.write_command("T 1")
        else:
            self.write_command("T 0")

    def set_accel_int_inactive_level(self, level: bool):
        if level:
            self.write_command("P 0")
        else:
            self.write_command("P 1")