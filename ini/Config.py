import configparser
import contextlib
import os
from varialble_tools import *


class Empty:
    pass


def get_value(value):
    with contextlib.suppress(NameError, SyntaxError):
        eval_value = eval(value)
        if type(eval_value) in [int, float, list, tuple, dict]:
            return eval_value
    return value


def get_config_value(section, option):
    config = Config()
    return config.get_value(section, option)


def set_config_value(section, option, value):
    config = Config()
    return config.set_value(section, option, value)


class Config:
    def __init__(self, config_filename='config.ini', debug=False):
        self.debug = debug
        self.filename = config_filename
        if not os.path.exists(self.filename):
            self.init_config()
        self.config = configparser.ConfigParser()
        self.config.optionxform = lambda option: option
        self.read_value()

    def init_config(self):
        config = configparser.ConfigParser()
        config.optionxform = lambda option: option
        config.add_section(STR_PASSWORD)
        config[STR_PASSWORD][STR_PASSWORD] = 'bujeon'
        config.add_section(STR_SERIAL)
        config[STR_SERIAL][STR_COMPORT] = ''
        config.add_section(STR_FILES)
        config[STR_FILES][STR_CONFIG_FILE] = ''
        config[STR_FILES][STR_RESULT_FILE] = ''
        config[STR_FILES][STR_RESULT_NUM] = '0'
        config.add_section(STR_COUNT)
        config[STR_COUNT][STR_COUNT_TOTAL] = '0'
        config[STR_COUNT][STR_COUNT_OK] = '0'
        config[STR_COUNT][STR_COUNT_NG] = '0'
        config.add_section(STR_ERROR_COUNT)
        config[STR_ERROR_COUNT][STR_ERROR_COUNT_CON] = '0'
        config[STR_ERROR_COUNT][STR_ERROR_COUNT_POGO] = '0'
        config[STR_ERROR_COUNT][STR_ERROR_COUNT_LED] = '0'
        config[STR_ERROR_COUNT][STR_ERROR_COUNT_HALL] = '0'
        config[STR_ERROR_COUNT][STR_ERROR_COUNT_VBATID] = '0'
        config[STR_ERROR_COUNT][STR_ERROR_COUNT_BATTERY] = '0'
        config[STR_ERROR_COUNT][STR_ERROR_COUNT_PROX] = '0'
        config[STR_ERROR_COUNT][STR_ERROR_COUNT_MIC] = '0'

        with open(self.filename, 'w') as configfile:
            config.write(configfile)

    def read_value(self):
        self.config.read(self.filename)

        for section in self.config.sections():
            if not hasattr(self, section):
                setattr(self, section, Empty())
            current_section = getattr(self, section)

            for option in self.config[section]:
                value = self.config.get(section, option)
                setattr(current_section, option, get_value(value))

    def get_value(self, section, option):
        self.config.read(self.filename)
        with contextlib.suppress(KeyError):
            if type(return_value := get_value(self.config[section][option])) is int:
                return_value = str(return_value)
            return return_value

    def set_value(self, section, option, value):
        self.config.read(self.filename)
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config[section][option] = str(value)

        if not hasattr(self, section):
            setattr(self, section, Empty())
        current_section = getattr(self, section)
        setattr(current_section, option, value)
        self.save()

    def save(self):
        with open(self.filename, 'w') as configfile:
            self.config.write(configfile)
