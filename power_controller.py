from serial import Serial
import json
from time import sleep


class PowerController():
    def __init__(self, serial_port: str):
        # open serial port for load and set receieve timeout to 0.5 sec
        self.ser = Serial(serial_port, 115200, timeout=0.5)
        self.vals = 0

    def write_command(self, command: str):
        self.ser.write(command.encode('utf-8'))

    def get_new_reading(self):
        self.write_command("R")
        this_line = self.ser.readline()
        self.vals = json.loads(this_line)

    def get_vbat_v(self):
        self.get_new_reading()
        return self.vals["vbat_v"]

    def set_vbat(self, v: float):
        command = "V {}".format(v)
        self.write_command(command)
        # wait until VBAT reaches target value
        max_wait_sec = 2
        min_v = v - 0.1
        max_v = v + 0.1
        n = 0
        while 1:
            v_read = self.get_vbat_v()
            if v_read > min_v and v_read < max_v:
                return
            if n > max_wait_sec * 10:
                return
            sleep(0.1)
            n = n + 1

    def get_vbus_v(self):
        self.get_new_reading()
        return self.vals["vbus_v"]

    def set_vbus_enable(self, on: bool):
        if on:
            self.write_command("E 1")
            min_v = 4.25
            max_v = 5.2
        else:
            self.write_command("E 0")
            min_v = 0.0
            max_v = 1.0
        # wait until VBUS reaches target value

    def get_vbat_mA(self):
        self.get_new_reading()
        return self.vals["vbat_mA"]

    def get_vbus_mA(self):
        self.get_new_reading()
        return self.vals["vbus_mA"]

    def get_rgb(self):
        self.get_new_reading()
        r = self.vals["color_r"]
        g = self.vals["color_g"]
        b = self.vals["color_b"]
        return r, g, b

    def set_servo_position(self, degrees: int):
        command = "S {}".format(degrees)
        self.write_command(command)

    def reset(self):
        self.write_command("Y")

    def reset_into_bootloader(self):
        self.write_command("B")
