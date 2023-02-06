VOLTAGE = 'mV'
RESISTANCE = 'Ω'
DIGITAL = 'digital'

ZERO_BYTE = b'\x00'
CONNECTION_OFF = 0xFF

SOT = b'\x10'
UI = b'\x01'
MCU = b'\x02'
EOT = b'\x20' * 3

CMD_CONFIG_SET = b'\x90'
CMD_ZIG_DOWN = b'\x91'
CMD_TEST_START = b'\x92'
CMD_TEST_END = b'\x93'
CMD_RESULT_DATA = b'\x94'
CMD_CONTACT_CONTROL = b'\x80'
CMD_REF_VOLTAGE_CONTROL1 = b'\x81'
CMD_REF_VOLTAGE_CONTROL2 = b'\x82'
CMD_ETC_CONTROL = b'\x83'
CMD_AD_READ = b'\x84'
CMD_SOL_VALVE_CONTROL = b'\x85'
CMD_ALL_OFF = b'\x86'
CMD_CONNECTION_VERSION = b'\x70'
CMD_SIDE_SET = b'\x71'

REF1 = {
    "REF 1V 1KΩ": 0,
    "REF 1V 10KΩ": 1,
    "REF 1V 100KΩ": 2,
    "REF 1V 1MΩ": 3,
    "AMP 1.8V": 4,
    "REF 2V": 5,
    "AMP 3.3V": 6,
    "TP1": 7
}

REF2 = {
    "AMP 1.8V": 0,
    "AMP 3.3V": 1,
    "P1.8V": 2,
    "P3.3V": 3
}

ETC = {
    "ETC AD": 0,
    "TP2-TP3": 1,
    "I2C": 2,
    "FREQ": 3
}

AD_READ = {
    'mux_ad8': 0,
    'etc_ad': 1,
    'ref_1.0v': 3,
    'ref_2.0v': 4,
    '1.8v_cc': 5,
    '3.3v_cc': 6,
    'ad_cds': 7
}

AD_READ_TEXT = {
    'mux_ad8': 'MUX AD8',
    'etc_ad': 'ETC AD',
    'ref_1.0v': 'REF 1.0V',
    'ref_2.0v': 'REF 2.0V',
    '1.8v_cc': '1.8V CC',
    '3.3v_cc': '3.3V CC',
    'ad_cds': 'AD CDS'
}

AD_READ_TYPE = {
    'mux_ad8': VOLTAGE,
    'etc_ad': DIGITAL,
    'ref_1.0v': VOLTAGE,
    'ref_2.0v': VOLTAGE,
    '1.8v_cc': VOLTAGE,
    '3.3v_cc': VOLTAGE,
    'ad_cds': VOLTAGE
}

SOL_VALUE = {f"-sol{num}-": 10 + num - 1 for num in range(1, 9)}
