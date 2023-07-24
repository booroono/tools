import struct

from PySide2.QtCore import Slot, Signal
from PySide2.QtGui import Qt
from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QCheckBox, \
    QFileDialog, QHeaderView, QComboBox, QTableWidgetItem, QMessageBox, QRadioButton, QGridLayout, QLineEdit, QLabel

from component.components import CheckButton, change_color_selected_button
from ini.Config import set_config_value, get_config_value
from logger import logger
from variables import CMD_CONFIG_SET
from varialble_tools import *


class TWSConfigView(QWidget):
    config_received_signal = Signal(int)
    config_data_send_signal = Signal(list)
    file_name_change_signal = Signal()
    checkbox_checked_signal = Signal(dict)

    def __init__(self, serial):
        super(TWSConfigView, self).__init__()
        self.serial = serial
        self.setWindowTitle(STR_CONFIG)

        self.setMinimumWidth(WINDOW_WIDTH)
        self.setMinimumHeight(WINDOW_HEIGHT)
        self.setLayout(layout := QVBoxLayout())
        layout.addLayout(load_save_layout := QHBoxLayout())
        layout.addLayout(main_layout := QHBoxLayout())
        layout.addLayout(set_layout := QHBoxLayout())
        layout.setStretchFactor(load_save_layout, 1)
        layout.setStretchFactor(main_layout, 8)
        layout.setStretchFactor(set_layout, 1)

        load_save_layout.addWidget(left_radio := QRadioButton(STR_LEFT))
        load_save_layout.addWidget(right_radio := QRadioButton(STR_RIGHT))
        load_save_layout.addWidget(load_button := QPushButton(STR_LOAD))
        load_save_layout.addWidget(save_button := QPushButton(STR_SAVE))
        load_save_layout.addWidget(password_button := QPushButton(STR_PASSWORD))

        main_layout.addLayout(steps_layout := QVBoxLayout())
        main_layout.addLayout(config_layout := QHBoxLayout())
        main_layout.setStretchFactor(steps_layout, 3)
        main_layout.setStretchFactor(config_layout, 7)

        steps_layout.addWidget(check_all := QCheckBox(STR_CHECK_ALL))
        steps = [CheckButton(f"{index + 1}.{step}") for index, step in enumerate(STEP_SEQUENCES)]
        for step in steps:
            step.state_changed_signal.connect(self.checkbox_checked_signal.emit)
            steps_layout.addLayout(step)
        step_pages = {step: self.make_table_widget(step) for step in STEP_SEQUENCES}
        for table in step_pages.values():
            config_layout.addWidget(table)
        step_pages[STR_CONN_OS].setVisible(True)

        set_layout.addWidget(set_button := QPushButton(STR_SET))

        check_all.stateChanged.connect(self.check_all)

        self.left_radio = left_radio
        self.right_radio = right_radio

        # button
        load_button.clicked.connect(self.button_clicked)
        save_button.clicked.connect(self.button_clicked)
        set_button.clicked.connect(self.button_clicked)
        password_button.clicked.connect(self.button_clicked)

        self.steps = steps
        self.step_pages = step_pages

        self.set_config_list = []

        self.password_changed_widget = TWSConfigChangePassword()

        self.connect_event()
        check_all.setChecked(True)

        change_color_selected_button([step.button for step in self.steps], self.steps[0].button)

        if file := get_config_value(STR_FILES, STR_CONFIG_FILE):
            self.load_file(file)

    def connect_event(self):
        for step in self.steps:
            step.button.clicked.connect(self.step_clicked)

        self.config_received_signal.connect(self.received_config)
        self.password_changed_widget.password_changed.connect(self.password_changed_widget.close)

    def check_all(self, state):
        for step in self.steps:
            step.checkbox.setChecked(state)

    def button_clicked(self):
        button_name = self.sender().text()
        self.serial.timer_stop_signal.emit()
        if button_name == STR_SET:
            if self.make_config_set_list():
                self.send_config_data_to_serial()
            else:
                raise InterruptedError
        if button_name == STR_LOAD:
            if fname := QFileDialog.getOpenFileName(self, 'Open file', './', 'Data Files(*.txt)')[0]:
                self.load_file(fname)
                set_config_value(STR_FILES, STR_CONFIG_FILE, fname)
                self.file_name_change_signal.emit()
        if button_name == STR_SAVE:
            if fname := QFileDialog.getSaveFileName(self, 'Save file', './', 'Data Files(*.txt)')[0]:
                self.save_file(fname)
        if button_name == STR_PASSWORD:
            self.password_changed_widget.show()

        self.serial.reset_time_signal.emit()

    def make_config_set_list(self):
        self.set_config_list.clear()
        self.set_config_list = self.get_config_checked_list()
        return self.set_config_list

    def get_config_checked_list(self):
        return [
            step.button.text()
            for step in self.steps
            if step.checkbox.checkState() == Qt.Checked
        ]

    def get_right_check(self):
        return int(self.right_radio.isChecked())

    def send_config_data_to_serial(self):
        try:
            step_name = self.set_config_list.pop(0)[2:]
        except IndexError as e:
            logger.debug('step done!!!')
            QMessageBox.information(self, "Config Result", "Config Set is Okay!!!")
            return
        step = STEP_SEQUENCES.index(step_name) + 1
        table = self.step_pages[step_name]
        table_data = self.get_table_values(table)
        datas = []
        for row in table_data:
            datas.extend([int(value) if type(value) == str else value for value in row])

        if datas:
            datas.insert(0, step)
            datas.insert(0, CMD_CONFIG_SET)
            self.config_data_send_signal.emit(datas)
        else:
            self.send_config_data_to_serial()

    def step_clicked(self):
        logger.debug(f"{self.sender().text()} button clicked!!!")
        for steps_page in self.step_pages.values():
            steps_page.setVisible(False)

        self.step_pages[self.sender().text()[2:]].setVisible(True)

        change_color_selected_button(
            [step.button for step in self.steps],
            self.sender()
        )

    def load_file(self, file_name):
        with open(file_name, 'r') as f:
            lines = f.readlines()
        lines = [line.replace('\n', '') for line in lines]
        step_start_nums = [index for index, line in enumerate(lines) if ':' in line]

        steps = []
        for index, step_num in enumerate(step_start_nums):
            if index == len(step_start_nums) - 1:
                steps.append(lines[step_num + 1:])
                continue
            steps.append(lines[step_num + 1:step_start_nums[index + 1]])

        for step_num, step in enumerate(steps):
            self.fill_table_widget_from_load_file(step_num, step)

    def fill_table_widget_from_load_file(self, step_num, datas):
        table = self.get_table_widget_from_step_num(step_num)
        self.clear_table(table)
        values = []
        for data in datas:
            value = list(map(int, data.split(' ')))
            values.append(value)
        self.set_table_values(table, values)

    def clear_table(self, table):
        column_count, row_count = table.columnCount(), table.rowCount()
        for row in range(row_count):
            for column in range(column_count):
                item = table.cellWidget(row, column)
                if type(item) == QTableWidget:
                    item.setCurrentIndex(0)
                else:
                    table.takeItem(row, column)

    def get_table_widget_from_step_num(self, step_num):
        return self.step_pages[STEP_SEQUENCES[step_num]]

    def save_file(self, file_name):
        line_datas = []
        for step_name, step_table in self.step_pages.items():
            step_num = STEP_SEQUENCES.index(step_name) + 1
            line_datas.append(f"{step_num}:\n")
            table_values = self.get_table_values(step_table)
            line_datas.extend(' '.join(value) + '\n' for value in table_values if value)
        with open(file_name, 'w') as f:
            f.writelines(line_datas)


    @staticmethod
    def get_table_row_datas(table, row):
        values = []
        for column in range(table.columnCount()):
            if item := table.cellWidget(row, column):
                if value := item.currentIndex():
                    values.append(str(value))
                else:
                    values.clear()
                    break
            elif item := table.item(row, column):
                values.append(item.text())
            else:
                values.clear()
                break
        return values

    def get_table_values(self, table):
        values = []
        for row in range(table.rowCount()):
            if row := (self.get_table_row_datas(table, row)):
                values.append(row)
        return values

    @staticmethod
    def set_table_values(table, values):
        for row, row_value in enumerate(values):
            for column, column_value in enumerate(row_value):
                if item := table.cellWidget(row, column):
                    item.setCurrentIndex(column_value)
                else:
                    table.setItem(row, column, QTableWidgetItem(str(column_value)))

    @Slot(int)
    def received_config(self, result):
        if result:
            self.send_config_data_to_serial()
        else:
            raise NotImplemented

    def make_table_widget(self, step):
        widget = QTableWidget()
        if step == STR_CONN_OS:
            self.set_table_column_row_count(widget, 3, 48)
            widget.setHorizontalHeaderLabels([STR_POS, STR_NEG, STR_REF_VOLTAGE])
            for index in range(48):
                self.add_combobox_pin_num(index, 2, widget)
                ref_voltage_combo_box = QComboBox()
                ref_voltage_combo_box.addItems(REF1)
                widget.setCellWidget(index, 2, ref_voltage_combo_box)
        if step == STR_POGO_OS:
            self.set_table_column_row_count(widget, 4, 1)
            widget.setHorizontalHeaderLabels([STR_J1_PIN, STR_J2_PIN, STR_POGO_PIN, STR_GND_PIN])
            self.add_combobox_pin_num(0, 4, widget)
        if step == STR_LED:
            self.set_table_column_row_count(widget, 2, 1)
            widget.setHorizontalHeaderLabels([STR_LED_PIN, STR_GND_PIN])
            self.add_combobox_pin_num(0, 2, widget)
        if step == STR_HALL_SENSOR:
            self.set_table_column_row_count(widget, 4, 1)
            widget.setHorizontalHeaderLabels([STR_18V_PIN, STR_I2C_SCL_PIN, STR_I2C_SDA_PIN, STR_GND_PIN])
            self.add_combobox_pin_num(0, 4, widget)
        if step == STR_VBAT_ID:
            self.set_table_column_row_count(widget, 3, 1)
            widget.setHorizontalHeaderLabels([STR_18V_PIN, STR_BAT_ID_PIN, STR_GND_PIN])
            self.add_combobox_pin_num(0, 3, widget)
        if step == STR_BATTERY:
            self.set_table_column_row_count(widget, 2, 1)
            widget.setHorizontalHeaderLabels([STR_VBATT_PIN, STR_GND_PIN])
            self.add_combobox_pin_num(0, 2, widget)
        if step == STR_PROX:
            self.set_table_column_row_count(widget, 5, 1)
            widget.setHorizontalHeaderLabels([STR_33V_PIN, STR_18V_PIN, STR_I2C_SCL_PIN, STR_I2C_SDA_PIN, STR_GND_PIN])
            self.add_combobox_pin_num(0, 5, widget)
        if step == STR_MIC:
            self.set_table_column_row_count(widget, 2, 1)
            widget.setHorizontalHeaderLabels([STR_MIC_18V_PIN, STR_GND_PIN])
            self.add_combobox_pin_num(0, 2, widget)
        widget.setVisible(False)
        return widget

    def add_combobox_pin_num(self, index, num, widget):
        for num in range(num):
            combo_box = QComboBox()
            combo_box.addItems(PIN_NUM_LIST)
            widget.setCellWidget(index, num, combo_box)

    def set_table_column_row_count(self, widget, column, row):
        widget.setColumnCount(column)
        widget.setRowCount(row)
        header = widget.horizontalHeader()

        for index in range(column):
            header.setSectionResizeMode(index, QHeaderView.ResizeToContents)

        return widget

    def closeEvent(self, e):
        self.password_changed_widget.close()


class TWSConfigPassword(QWidget):
    password_ok_signal = Signal()

    def __init__(self):
        super(TWSConfigPassword, self).__init__()
        self.setWindowTitle("Enter Password")
        self.setLayout(layout := QHBoxLayout())
        layout.addWidget(input_password := QLineEdit())
        layout.addWidget(password_enter := QPushButton("Enter"))
        input_password.setEchoMode(QLineEdit.Password)
        input_password.setMinimumWidth(200)

        input_password.returnPressed.connect(self.clicked_enter)
        password_enter.clicked.connect(self.clicked_enter)

        self.input_password = input_password

    def clicked_enter(self):
        if self.input_password.text() == get_config_value(STR_PASSWORD, STR_PASSWORD):
            self.password_ok_signal.emit()
        else:
            QMessageBox.warning(self, "Error", "Password is not Correct!!")
        self.input_password.clear()


class TWSConfigChangePassword(QWidget):
    password_changed = Signal()

    def __init__(self):
        super(TWSConfigChangePassword, self).__init__()
        self.setWindowTitle("Change Password")
        self.setLayout(layout := QGridLayout())
        layout.addWidget(QLabel("New Password"), 0, 0)
        layout.addWidget(new_password := QLineEdit(), 0, 1)
        layout.addWidget(QLabel("Confirm Password"), 1, 0)
        layout.addWidget(confirm_password := QLineEdit(), 1, 1)
        layout.addWidget(enter_button := QPushButton("Enter"), 2, 1)
        new_password.setEchoMode(QLineEdit.Password)
        confirm_password.setEchoMode(QLineEdit.Password)

        new_password.returnPressed.connect(confirm_password.setFocus)
        confirm_password.returnPressed.connect(self.clicked_enter)
        enter_button.clicked.connect(self.clicked_enter)

        self.new_password = new_password
        self.confirm_password = confirm_password

    def clicked_enter(self):
        if self.new_password.text() == self.confirm_password.text():
            set_config_value(STR_PASSWORD, STR_PASSWORD, self.new_password.text())
            QMessageBox.information(self, "Password", "Password is Changed!!")
            self.password_changed.emit()
        else:
            QMessageBox.warning(self, "Error", "Password is not matched!!")
        self.clear_line_edits()

    def clear_line_edits(self):
        self.new_password.clear()
        self.confirm_password.clear()
