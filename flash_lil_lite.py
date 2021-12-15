from time import sleep
import esptool
import serial


def flash(serial_port: str, app_path: str):
    command = [
        "--chip", "esp32s2",
        "--port", serial_port,
        "--baud", "460800",
        "--before", "default_reset",
        "--after", "hard_reset",
        "write_flash",
        "-z",
        "--flash_mode", "dio",
        "--flash_freq", "40m",
        "--flash_size", "detect",
        "0x1000", "firmware_files/bootloader_dio_40m.bin",
        "0x8000", "firmware_files/partitions.bin",
        "0xe000", "firmware_files/boot_app0.bin",
        "0x10000", app_path,
    ]
    try:
        esptool.main(command)
    except SystemExit:
        pass
        return
    except (serial.serialutil.SerialException):
        pass
        sleep(1)
        esptool.main(command)


def flash_test_firmware(lite_port):
    flash(lite_port, "firmware_files/test_firmware.bin")


def flash_firmware(lite_port):
    flash(lite_port, "firmware_files/firmware.bin")
