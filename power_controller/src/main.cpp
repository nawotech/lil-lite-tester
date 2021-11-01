#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_INA219.h>
#include <Adafruit_TCS34725.h>
#include <ArduinoJson.h>
#include <ESP32Servo.h>
#include <Timer.h>

#define PIN_SDA 32
#define PIN_SCL 33
#define PIN_VBUS_EN 22
#define PIN_DAC_VBAT 26
#define PIN_SERVO 2

Adafruit_INA219 Vbat;
Adafruit_INA219 Vbus(0x41);
Adafruit_TCS34725 Color = Adafruit_TCS34725(TCS34725_INTEGRATIONTIME_2_4MS, TCS34725_GAIN_4X);
Servo ButtonServo;
Timer TmrAutosend;

bool autosend = false;

void set_vbat(float v)
{
    // given float Vout, calculate correct value to set DAC
    // Vout has 2X amp
    float vdac = v / 2.0;
    // DAC outputs 3.3V at 255 counts, calculate counts needed
    uint8_t set_counts = vdac / 3.3 * 255;
    dacWrite(PIN_DAC_VBAT, set_counts); // DAC1, pin GPIO17
}

void set_vbus_enable(bool on)
{
    digitalWrite(PIN_VBUS_EN, on);
}

void setup()
{
    pinMode(PIN_VBUS_EN, OUTPUT);
    pinMode(PIN_SERVO, OUTPUT);
    Wire.setPins(PIN_SDA, PIN_SCL);
    Serial.begin(115200);
    Vbat.begin();
    Vbus.begin();
    Vbat.setCalibration_16V_400mA();
    Vbus.setCalibration_16V_400mA();
    Color.begin();
    set_vbat(3.7);
    delay(3000);
    set_vbus_enable(1);
    Color.setInterrupt(1); // turn off white LED
    ESP32PWM::allocateTimer(0);
	ESP32PWM::allocateTimer(1);
	ESP32PWM::allocateTimer(2);
	ESP32PWM::allocateTimer(3);
    ButtonServo.setPeriodHertz(50);
    ButtonServo.attach(PIN_SERVO, 600, 2500);
    ButtonServo.write(90);
}

int servopos = 90;

void move_servo(bool forward)
{
    if(forward)
    {
        servopos++;
    }
    else
    {
        servopos = servopos - 1;
    }
    if(servopos > 180)
    {
        servopos = 180;
    }
    if(servopos < 0)
    {
        servopos = 0;
    }
    ButtonServo.write(servopos);
    Serial.println(servopos);
}

void send_all_readings()
{
    StaticJsonDocument<200> Readings;

    Readings["vbus_v"] = Vbus.getBusVoltage_V();
    Readings["vbus_mA"] = Vbus.getCurrent_mA();
    Readings["vbat_v"] = Vbat.getBusVoltage_V();
    Readings["vbat_mA"] = Vbat.getCurrent_mA();

    float r, g, b;
    Color.getRGB(&r, &g, &b);
    Readings["color_r"] = r;
    Readings["color_g"] = g;
    Readings["color_b"] = b;

    serializeJson(Readings, Serial);
    Serial.println();
}

void accel_self_test()
{
    return;
}

void loop()
{
    if (Serial.available() > 0)
    {
        char byte = Serial.read();
        if (byte == 'R')
        {
            send_all_readings();
        }
        else if (byte == 'E')
        {
            int val = Serial.parseInt();
            if (val == 1)
            {
                set_vbus_enable(1);
                // Serial.println("VBUS enabled");
            }
            else if (val == 0)
            {
                set_vbus_enable(0);
                // Serial.println("VBUS disabled");
            }
        }
        else if (byte == 'V')
        {
            float val = Serial.parseFloat();
            if (val >= 0.0 && val <= 4.4)
            {
                set_vbat(val);
                // Serial.println("VBAT set to ");
                // Serial.print(val);
                // Serial.print("V");
            }
        }
        else if (byte == 'I')
        {
            move_servo(true);
        }
        else if (byte == 'O')
        {
            move_servo(false);
        }
        else if (byte == 'S')
        {
            int val = Serial.parseInt();
            ButtonServo.write(val);
        }
        else if (byte == 'A')
        {
            autosend = true;
        }
    }

    if (autosend)
    {
        if (TmrAutosend.time_passed(10))
        {
            send_all_readings();
        }
    }
}