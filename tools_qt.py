import sys
import time
import traceback

from PySide2.QtCore import Slot, QTimer
from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QCheckBox, QTextEdit, \
    QMessageBox, QPushButton

from component.components import Button, GroupLabel, modify_sequence_visible
from config import TWSConfigView, TWSConfigPassword
from ini.Config import get_config_value, set_config_value
from logger import logger
from result import TWSResultView
from tws_serial import TWSSerial, get_serial_available_list
from variables import *
from varialble_tools import *


class TWSChecker(QApplication):
    def __init__(self):
        super(TWSChecker, self).__init__()
        self.serial = TWSSerial()
        self.ui = TWSCheckerView(self.serial)
        self.ui.event_connector()

        self.ui.setWindowTitle(MAIN_WINDOW_TITLE)


class TWSCheckerView(QWidget):

    def __init__(self, serial):
        super(TWSCheckerView, self).__init__()
        self.serial = serial
        self.config = TWSConfigView(serial)
        self.config_password = TWSConfigPassword()
        self.result_view = TWSResultView(serial)
        self.setMinimumWidth(WINDOW_WIDTH)
        self.setMinimumHeight(WINDOW_HEIGHT)
        self.setLayout(layout := QVBoxLayout())
        layout.addLayout(serial_layout := QHBoxLayout())
        layout.addLayout(config_layout := QHBoxLayout())
        layout.addLayout(main_layout := QHBoxLayout())
        layout.addLayout(bottom_layout := QVBoxLayout())

        layout.setStretchFactor(serial_layout, 1)
        layout.setStretchFactor(config_layout, 1)
        layout.setStretchFactor(main_layout, 7)
        layout.setStretchFactor(bottom_layout, 1)

        serial_layout.addWidget(serial_combobox := QComboBox())
        serial_layout.addWidget(serial_reload_button := QPushButton(STR_RELOAD))
        serial_layout.addWidget(serial_connect_button := Button(STR_CONNECT))
        serial_layout.addWidget(exit_button := QPushButton(STR_EXIT))
        serial_layout.setStretchFactor(serial_combobox, 7)
        serial_layout.setStretchFactor(serial_reload_button, 1)
        serial_layout.setStretchFactor(serial_connect_button, 1)
        serial_layout.setStretchFactor(exit_button, 1)

        config_layout.addWidget(reset_button := QPushButton(STR_RESET))
        config_layout.addWidget(buzzer_off_button := QPushButton(STR_BUZZER_OFF))
        config_layout.addWidget(fail_skip_checkbox := QCheckBox(STR_FAIL_SKIP))
        config_layout.addWidget(config_button := QPushButton(STR_CONFIG))
        config_layout.addWidget(result_button := QPushButton(STR_RESULT))

        main_layout.addLayout(step_sequence_layout := QVBoxLayout())
        main_layout.addLayout(result_layout := QVBoxLayout())
        main_layout.setStretchFactor(step_sequence_layout, 3)
        main_layout.setStretchFactor(result_layout, 7)

        step_sequences = {step: Button(f"{index + 1}.{step}", expanding=True) for index, step in
                          enumerate(STEP_SEQUENCES_MAIN)}
        for step in step_sequences.values():
            step_sequence_layout.addWidget(step)

        result_layout.addWidget(config_data_files := GroupLabel("Config/Data files"))
        config_data_files.set_font_size(20)
        result_layout.addWidget(pass_fail := GroupLabel())
        result_layout.addWidget(console_log := QTextEdit())
        result_layout.setStretchFactor(config_data_files, 1)
        result_layout.setStretchFactor(pass_fail, 2)
        result_layout.setStretchFactor(console_log, 7)

        bottom_layout.addWidget(stop_button := Button(STR_STOP))

        self.serial_combobox = serial_combobox
        self.buttons = {
            STR_RELOAD: serial_reload_button,
            STR_CONNECT: serial_connect_button,
            STR_EXIT: exit_button,
            STR_RESET: reset_button,
            STR_BUZZER_OFF: buzzer_off_button,
            STR_CONFIG: config_button,
            STR_RESULT: result_button,
            STR_STOP: stop_button
        }

        self.fail_skip_checkbox = fail_skip_checkbox

        self.step_sequences = step_sequences
        self.config_data_files = config_data_files
        self.pass_fail = pass_fail
        self.console_log = console_log
        self.console_log.setDisabled(True)

        self.init_variable()

        self.reload_button_clicked()
        self.serial_combobox.setCurrentText(get_config_value(STR_SERIAL, STR_COMPORT))
        self.refresh_filenames()

        # Timer
        self.version_timer = QTimer()

        self.show()

    def init_variable(self):
        self.buttons_action = {
            STR_RELOAD: self.reload_button_clicked,
            STR_CONNECT: self.connect_button_clicked,
            STR_EXIT: self.exit_button_clicked,
            STR_RESET: self.reset_button_clicked,
            STR_BUZZER_OFF: self.buzzer_button_clicked,
            STR_CONFIG: self.config_button_clicked,
            STR_RESULT: self.result_button_clicked,
            STR_STOP: self.stop_button_clicked
        }
        self.step_list = []
        self.step_name = ''
        self.config_first_time = True
        self.start_time = 0
        self.is_version_get = False

    def reload_button_clicked(self):
        self.serial_combobox.clear()
        self.serial_combobox.addItems(get_serial_available_list())

    def connect_button_clicked(self):
        self.serial.connect_signal.emit(self.serial_combobox.currentText())
        set_config_value(STR_SERIAL, STR_COMPORT, self.serial_combobox.currentText())

    def exit_button_clicked(self):
        self.close()

    def reset_button_clicked(self):
        send_data = [CMD_TEST_END, TEST_STOP]
        self.serial.serial_write_data_signal.emit(send_data)

    def buzzer_button_clicked(self):
        send_data = [CMD_BUZZ_OFF, ]
        self.serial.serial_write_data_signal.emit(send_data)

    def sub_window_status(self, window):
        if window.isMinimized():
            window.showNormal()
        elif window.isVisible():
            window.close()
            return
        self.view_left_main_view(window)

    def config_button_clicked(self):
        if self.config.isVisible():
            self.sub_window_status(self.config)
        else:
            self.config_password.show()

    def result_button_clicked(self):
        self.sub_window_status(self.result_view)

    def view_left_main_view(self, view):
        x, y, width, height = self.frameGeometry().getRect()
        view.move(x + width, y)
        view.show()

    def stop_button_clicked(self):
        send_data = [CMD_TEST_END, TEST_STOP]
        self.serial.serial_write_data_signal.emit(send_data)

    def event_connector(self):
        # button event connect
        for button_name, button in self.buttons.items():
            button.clicked.connect(self.button_clicked)

        # serial event connect
        self.serial.connection_state_signal.connect(self.serial_state)
        self.serial.serial_read_data_signal.connect(self.read_serial_data)

        # config event connect
        self.result_view.file_name_change_signal.connect(self.refresh_filenames)
        self.result_view.result_send_signal.connect(self.received_pass_fail)
        self.config.checkbox_checked_signal.connect(self.modify_sequence)
        self.config.checkbox_checked_signal.connect(self.result_view.checkbox_checked_signal.emit)
        self.config.file_name_change_signal.connect(self.refresh_filenames)
        self.config.config_data_send_signal.connect(self.serial.serial_write_data_signal.emit)
        self.config_password.password_ok_signal.connect(self.config_password.close)
        self.config_password.password_ok_signal.connect(lambda: self.sub_window_status(self.config))

        # timer connect
        self.version_timer.timeout.connect(self.cmd_version)

    def button_clicked(self):
        button_name = self.sender().text()
        logger.debug(f"{button_name} clicked!!")
        self.buttons_action[button_name]()

    @Slot(list)
    def read_serial_data(self, datas):
        logger.debug(datas)

        cmd, *data = datas
        if cmd == CMD_CONFIG_SET:
            self.config.config_received_signal.emit(data[0])
        if cmd == CMD_ZIG_DOWN:
            self.cmd_zig_down()
        if cmd == CMD_SOFTWARE_RESET:
            self.zig_down_reset()
        if cmd == CMD_TEST_END:
            self.console_log.append(TEXT_TEXT_STOP)
            QMessageBox.warning(self, "Machine Stop", "The test was aborted by the Machine")
        if cmd == CMD_RESULT_DATA:
            self.cmd_result_data(data)
        if cmd == CMD_CONNECTION_VERSION:
            version = f"{data[0] / 100: .2f}"
            self.setWindowTitle(f"{MAIN_WINDOW_TITLE} / FW v{version}")

    def cmd_zig_down(self):
        self.start_time = time.time()
        self.result_view.result_value_clear_signal.emit()
        self.zig_down_reset()
        self.console_log.append(TEXT_JIG_DOWN)
        self.start_step()
        self.result_view.clean_result_signal.emit()

    def cmd_result_data(self, data):
        step, step_size, *result = data
        try:
            ordered_step = self.step_list.pop(0)[2:]
            if step == STEP_SEQUENCES.index(ordered_step) + 1:
                to_config_data = [step] + list(result)
                self.result_view.result_received_signal.emit(to_config_data)
            else:
                raise IndexError
        except IndexError as e:
            QMessageBox.critical(self, TEXT_CRITICAL_MESSAGE, "Result is not expected!!!")

    def cmd_version(self):
        self.version_timer.stop()
        send_data = [CMD_CONNECTION_VERSION]
        self.serial.serial_write_data_signal.emit(send_data)

    def make_step_list(self):
        self.step_list = self.config.get_config_checked_list()

    def start_step(self):
        self.make_step_list()
        self.send_step_packet()

    def send_step_packet(self):
        try:
            self.step_name = self.step_list[0][2:]
            self.step_sequences[self.step_name].background_color = COLOR_SKY_LIGHT_BLUE
            self.console_log.append(f"{self.step_name} START\n")
        except IndexError as e:
            self.step_name = len(STEP_SEQUENCES)
            self.console_log.append(TEXT_TEST_DONE)
            self.console_log.append(f"TEST TIME : {time.time() - self.start_time: .2f}")
            self.check_result = self.result_view.get_pass_fail()
            if self.check_result == STR_PASS:
                send_data = [CMD_TEST_END, TEST_STOP]
            else:
                send_data = [CMD_TEST_END, TEST_FAIL]

            self.result_view.make_result_file_signal.emit(STEP_SEQUENCES)
            self.result_view.count_signal.emit(self.config.get_config_checked_list())
        else:
            step = STEP_SEQUENCES.index(self.step_name) + 1
            send_data = [CMD_TEST_START, self.config.get_right_check(), step]
            if step > 5:
                self.step_sequences[STR_CTEST].background_color = COLOR_GREEN
        self.serial.serial_write_data_signal.emit(send_data)
        # self.step_on_view()

    def zig_down_reset(self):
        self.check_result = ''
        self.console_log.clear()
        self.sequence_color_reset()

    def sequence_color_reset(self):
        for button in self.step_sequences.values():
            button.background_color = '#E1E1E1'

    @Slot(list)
    def received_pass_fail(self, result):
        if result:
            self.console_log.append(f"{self.step_name} END\n")
            self.step_sequences[self.step_name].background_color = COLOR_GREEN
            self.send_step_packet()
        elif self.fail_skip_checkbox.checkState():
            self.console_log.append(f"{self.step_name} FAIL but SKIP!!\n")
            self.step_sequences[self.step_name].background_color = COLOR_RED
            self.check_result = STR_FAIL
            self.send_step_packet()
        else:
            self.step_sequences[self.step_name].background_color = COLOR_RED
            self.fail_work()

    def modify_sequence(self, states):
        modify_sequence_visible(self.step_sequences, states)

    def refresh_filenames(self):
        config_file = get_config_value(STR_FILES, STR_CONFIG_FILE).split('/')[-1]
        result_file = get_config_value(STR_FILES, STR_RESULT_FILE).split('/')[-1]
        self.config_data_files.setText(
            f"{config_file}\n"
            f"{result_file}"
        )

    def fail_work(self):
        self.check_result = STR_FAIL
        self.console_log.append(f"{self.step_name} {STR_FAIL}\n")
        send_data = [CMD_TEST_END, TEST_FAIL]
        self.serial.serial_write_data_signal.emit(send_data)
        self.step_sequences[self.step_name].background_color = 'red'
        self.result_view.count_signal.emit(self.config.get_config_checked_list())

    @Slot(bool)
    def serial_state(self, state):
        self.buttons[STR_CONNECT].background_color = COLOR_SKY_LIGHT_BLUE if state else COLOR_RED
        self.serial_combobox.setDisabled(state)
        self.buttons[STR_RELOAD].setDisabled(state)
        if state:
            self.is_version_get = True
            self.version_timer.start(2000)
        else:
            QMessageBox.warning(self, 'Connection State', 'Disconnected with Machine!!')

    def closeEvent(self, event):
        self.serial.serial.close()
        self.config_password.close()
        self.config.close()
        self.result_view.close()

    @property
    def check_result(self):
        return self._check_result

    @check_result.setter
    def check_result(self, value):
        self._check_result = value
        self.pass_fail.setText(value)
        if value == STR_PASS:
            self.pass_fail.set_text_color(COLOR_SKY_LIGHT_BLUE)
        if value == STR_FAIL:
            self.pass_fail.set_text_color(COLOR_RED)


if __name__ == "__main__":
    try:
        logger.info(f"Start {MAIN_WINDOW_TITLE}")
        app = TWSChecker()
        sys.exit(app.exec_())
    except Exception as e:
        logger.error(e)
        logger.error(traceback.format_exc())
