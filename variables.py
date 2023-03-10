import struct

VOLTAGE = 'mV'
RESISTANCE = 'Ω'
DIGITAL = 'digital'

CONNECTION_OFF = 0xFF

SOT = 16
UI = 1
MCU = 2
EOT = struct.pack('3B', 32, 32, 32)

CMD_CONFIG_SET = 144
CMD_ZIG_DOWN = 145
CMD_TEST_START = 146
CMD_TEST_END = 147
CMD_RESULT_DATA = 148
CMD_SOFTWARE_RESET = 149
CMD_CONTACT_CONTROL = 128
CMD_REF_VOLTAGE_CONTROL1 = 129
CMD_REF_VOLTAGE_CONTROL2 = 130
CMD_ETC_CONTROL = 131
CMD_AD_READ = 132
CMD_SOL_VALVE_CONTROL = 133
CMD_ALL_OFF = 134
CMD_CONNECTION_VERSION = 112
CMD_SIDE_SET = 113
CMD_BUZZ_OFF = 114

TEST_STOP = 1
TEST_FAIL = 3

ZERO_BYTE_SEND_CMD = (
    CMD_ALL_OFF,
    CMD_CONNECTION_VERSION,
    CMD_BUZZ_OFF
)

ONE_BYTE_SEND_CMD = (
    CMD_TEST_START,
    CMD_TEST_END,
    CMD_REF_VOLTAGE_CONTROL1,
    CMD_REF_VOLTAGE_CONTROL2,
    CMD_ETC_CONTROL,
    CMD_AD_READ,
    CMD_SIDE_SET
)

RESULT_CONNECTOR_OPEN_SHORT = 1
RESULT_POGO_OPEN_SHORT = 2
RESULT_LED = 3
RESULT_HALL_SENSOR = 4
RESULT_VBAT_ID = 5
RESULT_BATTERY = 6
RESULT_PROX_TEST = 7
RESULT_MIC_TEST = 8

CONFIG_CONNECTOR_OPEN_SHORT = 1
CONFIG_POGO_OPEN_SHORT = 2
CONFIG_LED = 3
CONFIG_HALL_SENSOR = 4
CONFIG_VBAT_ID = 5
CONFIG_BATTERY = 6
CONFIG_PROX_TEST = 7

REF1 = {
    "REF R 1KΩ": 0,
    "REF R 10KΩ": 1,
    "REF R 100KΩ": 2,
    "REF R 1MΩ": 3,
    "REF R 10MΩ": 4,
    "P 3.3V": 5,
    "AMP 1.8V": 6,
    "AMP 3.3V": 7
}

REF2 = {
    "AMP 1.8V": 0,
    "AMP 3.3V": 1,
    "P1.8V": 2,
    "P3.3V": 3
}

ETC = {
    "ETC AD": 0,
    "TP4-TP2": 1,
    "TP5-TP3": 2,
    "I2C": 3
}

AD_READ = {
    'mux_ad8': 0,
    'mux_ad4': 1,
    'etc_ad': 2,
    '1.8v_cc': 3,
    '3.3v_cc': 4,
    'ad_cds1': 5,
    'ad_cds2': 6,
    'ad_cds3': 7
}

AD_READ_TEXT = {
    'mux_ad8': 'MUX AD8',
    'mux_ad4': 'MUX AD4',
    'etc_ad': 'ETC AD',
    '1.8v_cc': '1.8V CC',
    '3.3v_cc': '3.3V CC',
    'ad_cds1': 'AD CDS1',
    'ad_cds2': 'AD CDS2',
    'ad_cds3': 'AD CDS3'
}

AD_READ_TYPE = {
    'mux_ad8': VOLTAGE,
    'mux_ad4': VOLTAGE,
    'etc_ad': DIGITAL,
    '1.8v_cc': VOLTAGE,
    '3.3v_cc': VOLTAGE,
    'ad_cds1': VOLTAGE,
    'ad_cds2': VOLTAGE,
    'ad_cds3': VOLTAGE
}

SOL_VALUE = {f"-sol{num}-": 10 + num - 1 for num in range(1, 9)}
