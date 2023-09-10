WINDOW_WIDTH = 450
WINDOW_HEIGHT = 640
WINDOW_RESULT_WIDTH_ADD = 75

WINDOW_STATUS_WIDTH = 300
WINDOW_STATUS_HEIGHT = 450

VERSION = 1.12

MAIN_WINDOW_TITLE = f"TWSTester SW v{VERSION}"
SIDE = 0

RESULT_COLUMN_COUNT = 5

STR_CONFIG = "CONFIG"

STR_RELOAD = "RELOAD"
STR_CONNECT = "CONNECT"
STR_EXIT = "EXIT"
STR_RESET = "RESET"
STR_BUZZER_OFF = "BUZZER OFF"
STR_FAIL_SKIP = "FAIL SKIP"
STR_CONFIG = "CONFIG"
STR_RESULT = "RESULT"

STR_LEFT = "LEFT"
STR_RIGHT = "RIGHT"

STR_CONN_OS = "CONN OS"
STR_POGO_OS = "POGO OS"
STR_LED = "LED"
STR_HALL_SENSOR = "HALL SENSOR"
STR_VBAT_ID = "VBAT ID"
STR_CTEST = "C TEST"
STR_BATTERY = "BATTERY"
STR_PROX = "PROX"
STR_MIC = "MIC"

STR_POS = "POS"
STR_NEG = "NEG"
STR_REF_VOLTAGE = "REF Voltage"

STR_J1_PIN = "J1 Pin"
STR_J2_PIN = "J2 Pin"
STR_POGO_PIN = "POGO Pin"
STR_GND_PIN = "GND Pin"

STR_LED_PIN = "LED Pin"

STR_18V_PIN = "1.8V Pin"
STR_I2C_SCL_PIN = "I2C SCL Pin"
STR_I2C_SDA_PIN = "I2C SDA Pin"

STR_MIC_18V_PIN = "MIC 1.8V Pin"

STR_BAT_ID_PIN = "BAT ID Pin"
STR_VBATT_PIN = "VBATT Pin"

STR_33V_PIN = "3.3V Pin"

STR_DESCRIPTION = "Description"
STR_MIN = "MIN"
STR_VALUE = "VALUE"
STR_MAX = "MAX"
STR_RESULT = "RESULT"

STR_PASS = "PASS"
STR_FAIL = "FAIL"

STR_PASSWORD = 'PASSWORD'
STR_SERIAL = 'SERIAL'
STR_COMPORT = "COMPORT"
STR_FILES = "FILES"
STR_RESULT_FILE = "RESULT FILE"
STR_CONFIG_FILE = "CONFIG FILE"
STR_RESULT_NUM = "RESULT NUM"
STR_COUNT = "COUNT"
STR_COUNT_TOTAL = "TOTAL"
STR_COUNT_OK = "OK"
STR_COUNT_NG = "NG"
STR_ERROR_COUNT = "ERROR_COUNT"
STR_ERROR_COUNT_CON = STR_CONN_OS
STR_ERROR_COUNT_POGO = STR_POGO_OS
STR_ERROR_COUNT_LED = STR_LED
STR_ERROR_COUNT_HALL = STR_HALL_SENSOR
STR_ERROR_COUNT_VBATID = STR_VBAT_ID
STR_ERROR_COUNT_BATTERY = STR_BATTERY
STR_ERROR_COUNT_PROX = STR_PROX
STR_ERROR_COUNT_MIC = STR_MIC

STR_NA = 'N/A'

RESULT_COLUMN_NAMES = (
    STR_DESCRIPTION,
    STR_MIN,
    STR_VALUE,
    STR_MAX,
    STR_RESULT
)

DEFAULT_TABLE_COLUMN = (
    STR_DESCRIPTION,
    STR_MIN,
    STR_VALUE,
    STR_MAX,
    STR_RESULT
)
INDEX_COLUMN_DESCRIPTION = 0
INDEX_COLUMN_MIN = 1
INDEX_COLUMN_VALUE = 2
INDEX_COLUMN_MAX = 3
INDEX_COLUMN_RESULT = 4

STEP_SEQUENCES = (
    STR_CONN_OS,
    STR_POGO_OS,
    STR_LED,
    STR_HALL_SENSOR,
    STR_VBAT_ID,
    STR_BATTERY,
    STR_PROX,
    STR_MIC,
)

STEP_SEQUENCES_MAIN = (
    STR_CONN_OS,
    STR_POGO_OS,
    STR_LED,
    STR_HALL_SENSOR,
    STR_VBAT_ID,
    STR_CTEST,
    STR_BATTERY,
    STR_PROX,
    STR_MIC,
)

STEP_SEQUENCES_COUNT = {
    STR_CONN_OS: 48,
    STR_POGO_OS: 3,
    STR_LED: 5,
    STR_HALL_SENSOR: 15,
    STR_VBAT_ID: 1,
    STR_BATTERY: 1,
    STR_PROX: 11,
    STR_MIC: 1,
}

REF1 = (
    "",
    "REF 1V 1KΩ",
    "REF 1V 10KΩ",
    "REF 1V 100KΩ",
    "REF 1V 1MΩ",
    "REF 1V 10MΩ",
    "P 3.3V",
    "AMP 1.8V",
    "AMP 3.3V",
)

PIN_NUM_LIST = [str(num) if num else "" for num in range(49)]

STR_STOP = "STOP"

STR_LOAD = "LOAD"
STR_SAVE = "SAVE"
STR_STATUS = "STATUS"
STR_SET = "SET"

STR_CHECK_ALL = "CHECK ALL"

COLOR_SKY_LIGHT_BLUE = 'lightskyblue'
COLOR_GREEN = 'green'
COLOR_RED = 'red'

TEXT_JIG_DOWN = "JIG Down detected!!\n"
TEXT_TEST_DONE = "All Test Done!!\n"
TEXT_TEXT_STOP = "Stop Test by Machine!!\n"

TEXT_CRITICAL_MESSAGE = "Error Message"
TEXT_ERROR_SEQUENCE = ""

RESULT_PASS_FAIL_HEADER = [
    'P/F',
    'OS',
    'POGO',
    'LED',
    'HALL',
    'VBAT_ID',
    'BATTERY',
    'PROX',
    'MIC'
]

STATUS_COUNT_LABEL = [
    STR_COUNT_TOTAL,
    STR_COUNT_OK,
    STR_COUNT_NG,
] + list(STEP_SEQUENCES)


def xor_calc(s):
    b = 0
    for l in s.split(' '):
        b ^= int(l, 16)
    return hex(b)
