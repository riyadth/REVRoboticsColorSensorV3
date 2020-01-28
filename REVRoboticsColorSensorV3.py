# Program to read data from REV Robotics Color Sensor V3
import board
import busio
import time
import adafruit_dotstar

class RevColorSensorV3:
    """A class to interface with the REV Robotics Color Sensor V3"""
    ID=82
    i2c=None
    reg = {
        "control": 0x00,
        "proxLED": 0x01,
        "proxPulses": 0x02,
        "proxRate": 0x03,
        "colorRate": 0x04,
        "colorGain": 0x05,
        "partID": 0x06,
        "status": 0x07,
        "proxData": 0x08,
        "dataInfrared": 0x0a,
        "dataGreen": 0x0d,
        "dataBlue": 0x10,
        "dataRed": 0x13
    }
    gain = {
        "1x": 0,
        "3x": 1,
        "6x": 2,
        "9x": 3,
        "18x": 4
    }
    pulse_freq = {
        "60kHz": 0x18,
        "70kHz": 0x40,
        "80kHz": 0x28,
        "90kHz": 0x30,
        "100kHz": 0x38
    }
    led_current = {
        "Pulse2mA": 0,
        "Pulse5mA": 1,
        "Pulse10mA": 2,
        "Pulse25mA": 3,
        "Pulse50mA": 4,
        "Pulse75mA": 5,
        "Pulse100mA": 6,
        "Pulse125mA": 7
    }
    prox_res = {
        "8bit": 0x00,
        "9bit": 0x08,
        "10bit": 0x10,
        "11bit": 0x18
    }
    prox_rate = {
        "6ms": 1,
        "12ms": 2,
        "25ms": 3,
        "50ms": 4,
        "100ms": 5,
        "200ms": 6,
        "400ms": 7
    }
    color_res = {
        "20bit": 0x00,
        "19bit": 0x08,
        "18bit": 0x10,
        "17bit": 0x18,
        "16bit": 0x20,
        "13bit": 0x28
    }
    color_rate = {
        "25ms": 1,
        "50ms": 2,
        "100ms": 3,
        "200ms": 4,
        "500ms": 5,
        "1000ms": 6,
        "2000ms": 7
    }
    default_pulse_freq = "60kHz"
    default_led_current = "Pulse100mA"
    default_pulses = 32
    default_prox_res = "11bit"
    default_prox_rate = "50ms"
    default_color_res = "18bit"
    default_color_rate = "50ms"
    default_gain = "3x"

    def __init__(self):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        # Turn on RGB mode, enable light sensor, and enable proximity sensor
        self.write_regs(self.reg["control"], [ 0x07 ]);
        # Set default parameters
        self.config_prox_LED(self.default_pulse_freq, self.default_led_current, self.default_pulses)
        self.config_prox_sensor(self.default_prox_res, self.default_prox_rate)
        self.config_color_sensor(self.default_color_res, self.default_color_rate)
        self.set_gain(self.default_gain)

    def read_regs(self, offset, num_regs):
        address=[offset]
        while (self.i2c.try_lock()):
            pass
        try:
            self.i2c.writeto(self.ID, bytes(address), stop=False)
            result=bytearray(num_regs)
            self.i2c.readfrom_into(self.ID, result)
        finally:
            self.i2c.unlock()
        return tuple(result)

    def write_regs(self, address, data):
        buffer=[address]
        buffer += data
        while (self.i2c.try_lock()):
            pass
        try:
            self.i2c.writeto(self.ID, bytes(buffer), stop=True)
        finally:
            self.i2c.unlock()

    def read_20_bit_reg(self, address):
        raw = self.read_regs(address, 3)
        return (((raw[2] << 16) | (raw[1] << 8) | raw[0]) & 0xfffff)

    def read_11_bit_reg(self, address):
        raw = self.read_regs(address, 2)
        return (((raw[1] << 8) | raw[0]) & 0x7ff)

    def get_color(self):
        red = self.read_20_bit_reg(self.reg["dataRed"])
        green = self.read_20_bit_reg(self.reg["dataGreen"])
        blue = self.read_20_bit_reg(self.reg["dataBlue"])
        return (red,green,blue)

    def get_prox(self):
        return self.read_11_bit_reg(self.reg["proxData"])

    def set_gain(self, gain):
        self.write_regs(self.reg["lightGain"], [gain])

    def get_status(self):
        return tuple(self.read_regs(self.reg["status"], 1))

    def get_control(self):
        return tuple(self.read_regs(self.reg["control"], 1))

    def enable(self):
        control = self.read_regs(self.reg["control"], 1)
        new_control = control[0] | 0x02
        self.write_regs(self.reg["control"], [new_control])

    def config_prox_LED(self, pulse_freq, led_current, default_pulses):
        self.write_regs(self.reg["proxLED"], [ self.pulse_freq[pulse_freq] | self.led_current[led_current] ])
        self.write_regs(self.reg["proxPulses"], [ default_pulses ])

    def config_prox_sensor(self, prox_res, prox_rate):
        self.write_regs(self.reg["proxRate"], [ self.prox_res[prox_res] | self.prox_rate[prox_rate] ])

    def config_color_sensor(self, color_res, color_rate):
        self.write_regs(self.reg["colorRate"], [ self.color_res[color_res] | self.color_rate[color_rate] ])

    def set_gain(self, gain):
        self.write_regs(self.reg["colorGain"], [ self.gain[gain] ])


led = adafruit_dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1)
led.brightness = 1.0
sensor=RevColorSensorV3()

# print(sensor.read_rgb())

while True:
    (red,green,blue) = sensor.get_color()
    while (red > 255) or (green > 255) or (blue > 255):
        red = red >> 1
        green = green >> 1
        blue = blue >> 1
    led[0] = ( red, green, blue )
    print(sensor.get_prox())
    time.sleep(1.0)
