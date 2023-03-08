import csv
import os.path
import time

from PySide2.QtCore import Signal, Slot
from PySide2.QtGui import QColor
from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QFileDialog, QHeaderView, \
    QTableWidgetItem, QGroupBox, QGridLayout, QLabel

from component.components import Button, change_color_selected_button
from ini.Config import set_config_value, get_config_value
from logger import logger
from varialble_tools import *


def limit_place_decimal(value):
    v = f"{value: .2f}"
    for _ in range(2):
        if v[-1] == '0':
            v = v[:-1]
    if v[-1] == '.':
        v = v[:-1]
    return v


class TWSResultView(QWidget):
    result_received_signal = Signal(list)
    result_send_signal = Signal(bool)
    result_value_clear_signal = Signal()

    make_result_file_signal = Signal(list)
    file_name_change_signal = Signal()
    count_signal = Signal(list)

    clean_result_signal = Signal()

    def __init__(self):
        super(TWSResultView, self).__init__()
        self.setWindowTitle(STR_RESULT)
        self.status_widget = TWSStatusView()

        self.setMinimumWidth(WINDOW_WIDTH + WINDOW_RESULT_WIDTH_ADD)
        self.setMinimumHeight(WINDOW_HEIGHT)
        self.setLayout(layout := QVBoxLayout())
        layout.addLayout(load_save_layout := QHBoxLayout())
        layout.addLayout(main_layout := QHBoxLayout())
        layout.setStretchFactor(load_save_layout, 1)
        layout.setStretchFactor(main_layout, 9)

        load_save_layout.addWidget(load_button := QPushButton(STR_LOAD))
        load_save_layout.addWidget(save_button := QPushButton(STR_SAVE))
        load_save_layout.addWidget(status_button := QPushButton(STR_STATUS))

        main_layout.addLayout(steps_layout := QVBoxLayout())
        main_layout.addLayout(config_layout := QHBoxLayout())
        main_layout.setStretchFactor(steps_layout, 2)
        main_layout.setStretchFactor(config_layout, 8)

        steps = [Button(step, expanding=True) for step in STEP_SEQUENCES]
        for step in steps:
            steps_layout.addWidget(step)
        step_pages = {step: self.make_table_widget(step) for step in STEP_SEQUENCES}
        for table in step_pages.values():
            config_layout.addWidget(table)
        step_pages[STR_CONN_OS].setVisible(True)

        self.load_button = load_button
        self.save_button = save_button
        self.status_button = status_button
        self.steps = steps
        self.step_pages = step_pages

        self.set_config_list = []

        self.connect_event()

        localtime = time.localtime()
        self.filename = f"./{localtime.tm_year}{localtime.tm_mon:02d}{localtime.tm_mday:02d}.csv"

        self.result_num = 0
        if os.path.exists(self.filename):
            self.result_num = int(get_config_value(STR_FILES, STR_RESULT_NUM))

        change_color_selected_button(self.steps, self.steps[0])

        if file := get_config_value(STR_FILES, STR_RESULT_FILE):
            self.load_file(file)

    @Slot(list)
    def process_result(self, values):
        step, *datas = values
        table = self.get_table_widget_from_step_num(step - 1)
        float_datas = self.preprocess_result_data(step - 1, datas)
        # self.visible_table(table)
        self.result_send_signal.emit(self.compare_min_max_value(table, float_datas))

    @Slot()
    def clear_value(self):
        for table in self.step_pages.values():
            for row in range(table.rowCount()):
                table.takeItem(row, INDEX_COLUMN_VALUE)
                table.takeItem(row, INDEX_COLUMN_RESULT)
        # self.visible_table(self.step_pages[STR_CONN_OS])

    def visible_table(self, table):
        for pages in self.step_pages.values():
            pages.setVisible(False)
        table.setVisible(True)

    @staticmethod
    def compare_min_max_value(table, datas):
        ok_flag = True
        row = table.rowCount()

        for index, data in enumerate(datas):
            try:
                min_value, max_value = float(table.item(index, INDEX_COLUMN_MIN).text()), \
                                       float(table.item(index, INDEX_COLUMN_MAX).text())

            except Exception as e:
                print(index, e)
                continue
            table.setItem(index, INDEX_COLUMN_VALUE, QTableWidgetItem(limit_place_decimal(data)))
            if min_value <= data <= max_value:
                table.setItem(index, INDEX_COLUMN_RESULT, item := QTableWidgetItem(STR_PASS))
                item.setForeground(QColor("blue"))
            else:
                ok_flag = False
                table.setItem(index, INDEX_COLUMN_RESULT, item := QTableWidgetItem(STR_FAIL))
                item.setForeground(QColor("red"))
        return ok_flag

    @staticmethod
    def preprocess_result_data(step, datas):
        return_datas = list(map(float, datas))
        step_name = STEP_SEQUENCES[step]
        if step_name == STR_LED:
            for index in range(4):
                return_datas[index] /= 1000
        if step_name == STR_HALL_SENSOR:
            return_datas[0] /= 1000
            return_datas[1] /= 10
            return_datas[7] /= 10
            return_datas[9] /= 10
            return_datas[11] /= 10
        if step_name in [STR_VBAT_ID, STR_BATTERY, STR_PROX]:
            return_datas[0] /= 1000
        if step_name == STR_PROX:
            return_datas[1] /= 1000
        return return_datas

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
            value = data.split('\t')
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
            line_datas.extend('\t'.join(value) + '\n' for value in table_values)
        with open(file_name, 'w') as f:
            f.writelines(line_datas)

    @staticmethod
    def get_table_row_datas(table, row):
        description, min_value, max_value = table.item(row, INDEX_COLUMN_DESCRIPTION), \
                                            table.item(row, INDEX_COLUMN_MIN), \
                                            table.item(row, INDEX_COLUMN_MAX)
        if description and min_value and max_value:
            return [description.text(), min_value.text(), max_value.text()]
        else:
            return []

    def get_table_values(self, table):
        values = []
        for row in range(table.rowCount()):
            if row := (self.get_table_row_datas(table, row)):
                values.append(row)
        return values

    @staticmethod
    def set_table_values(table, values):
        for row, row_value in enumerate(values):
            description, min_value, max_value = row_value
            table.setItem(row, 0, QTableWidgetItem(str(description)))
            table.setItem(row, 1, QTableWidgetItem(str(min_value)))
            table.setItem(row, 3, QTableWidgetItem(str(max_value)))

    def make_table_widget(self, step):
        widget = QTableWidget()
        self.set_table_column_row_count(widget, RESULT_COLUMN_COUNT, STEP_SEQUENCES_COUNT[step])
        widget.setHorizontalHeaderLabels(RESULT_COLUMN_NAMES)
        widget.setVisible(False)
        return widget

    def set_table_column_row_count(self, widget, column, row):
        widget.setColumnCount(column)
        widget.setRowCount(row)
        header = widget.horizontalHeader()

        for index in range(column):
            header.setSectionResizeMode(index, QHeaderView.ResizeToContents)

        return widget

    def connect_event(self):
        for step in self.steps:
            step.clicked.connect(self.step_clicked)

        # button
        self.load_button.clicked.connect(self.button_clicked)
        self.save_button.clicked.connect(self.button_clicked)
        self.status_button.clicked.connect(self.button_clicked)

        # event connect
        self.result_received_signal.connect(self.process_result)
        self.result_value_clear_signal.connect(self.clear_value)
        self.make_result_file_signal.connect(self.make_result_file)
        self.count_signal.connect(self.make_count)
        self.clean_result_signal.connect(self.clean_result)

    def button_clicked(self):
        button_name = self.sender().text()
        if button_name == STR_LOAD:
            if fname := QFileDialog.getOpenFileName(self, 'Open file', './', 'Data Files(*.dat)')[0]:
                self.load_file(fname)
                set_config_value(STR_FILES, STR_RESULT_FILE, fname)
                self.file_name_change_signal.emit()
        if button_name == STR_SAVE:
            if fname := QFileDialog.getSaveFileName(self, 'Save file', './', 'Data Files(*.dat)')[0]:
                self.save_file(fname)
        if button_name == STR_STATUS:
            if self.status_widget.isMinimized():
                self.status_widget.showNormal()
            elif self.status_widget.isVisible():
                self.status_widget.close()
            else:
                self.status_widget.show()

    def step_clicked(self):
        logger.debug(f"{self.sender().text()} button clicked!!!")
        for steps_page in self.step_pages.values():
            steps_page.setVisible(False)

        self.step_pages[self.sender().text()].setVisible(True)

        change_color_selected_button(
            self.steps,
            self.sender()
        )

    @staticmethod
    def get_column_item(table, column):
        items = []
        for row in range(table.rowCount()):
            if table.item(row, INDEX_COLUMN_DESCRIPTION):
                if item := table.item(row, column):
                    items.append(item.text())
                else:
                    items.append('')
        return items

    def clean_item(self, table):
        for row in range(table.rowCount()):
            table.setItem(row, INDEX_COLUMN_VALUE, QTableWidgetItem(''))
            table.setItem(row, INDEX_COLUMN_RESULT, QTableWidgetItem(''))

    def get_pass_fail(self):
        items = []
        for table in self.step_pages.values():
            items.extend(self.get_column_item(table, INDEX_COLUMN_RESULT))
        return next((STR_FAIL for item in items if item != STR_PASS), STR_PASS)
        # return next((item for item in items if item == STR_FAIL), STR_PASS)

    @Slot()
    def clean_result(self):
        for table in self.step_pages.values():
            self.clean_item(table)

    @Slot(list)
    def make_count(self, step_list):
        if len(step_list) == len(STEP_SEQUENCES):
            self.status_widget.total_pass_fail_signal.emit(self.get_pass_fail() == STR_PASS)
        self.status_widget.step_error_result_signal.emit(
            self.get_step_pass_fail_list()
        )

    @Slot(list)
    def make_result_file(self, step_list):
        descriptions = []
        min_values = []
        max_values = []
        values = []
        self.result_num += 1

        for table_name in step_list:
            descriptions.extend(self.get_column_item(self.step_pages[table_name], INDEX_COLUMN_DESCRIPTION))
            min_values.extend(self.get_column_item(self.step_pages[table_name], INDEX_COLUMN_MIN))
            max_values.extend(self.get_column_item(self.step_pages[table_name], INDEX_COLUMN_MAX))
            values.extend(self.get_column_item(self.step_pages[table_name], INDEX_COLUMN_VALUE))

        descriptions.extend(RESULT_PASS_FAIL_HEADER)
        min_values.extend([STR_NA] * len(RESULT_PASS_FAIL_HEADER))
        max_values.extend([STR_NA] * len(RESULT_PASS_FAIL_HEADER))
        values.extend(self.make_pass_fail_for_file())

        descriptions.insert(0, 'description')
        min_values.insert(0, 'MIN')
        max_values.insert(0, 'MAX')
        values.insert(0, self.result_num)

        self.result_file_write(
            step_list,
            descriptions,
            min_values,
            max_values,
            values
        )

    def make_pass_fail_for_file(self):
        pass_fails = [self.get_pass_fail()]
        pass_fails.extend(self.get_step_pass_fail_list(pos='O', nag='X'))
        # for index in range(len(RESULT_PASS_FAIL_HEADER)):
        #     if index:
        #         pass_fail = self.get_column_item(self.step_pages[STEP_SEQUENCES[index - 1]], INDEX_COLUMN_RESULT)
        #         if all(STR_PASS == item for item in pass_fail):
        #             pass_fails.append('O')
        #         else:
        #             pass_fails.append('X')
        #     else:
        #         pass_fails.append(self.get_pass_fail())
        return pass_fails

    def get_step_pass_fail_list(self, pos=True, nag=False):
        pass_fail_list = []
        for step in STEP_SEQUENCES:
            a = self.get_column_item(self.step_pages[step], INDEX_COLUMN_RESULT)
            if all(STR_PASS == item or item == '' for item in a):
                pass_fail_list.append(pos)
            else:
                pass_fail_list.append(nag)
        return pass_fail_list

    def result_file_write(
            self,
            step_list,
            descriptions,
            min_values,
            max_values,
            values
    ):
        if os.path.exists(self.filename):
            with open(self.filename, 'a', newline="") as f:
                wr = csv.writer(f)
                if len(step_list) != len(self.step_pages):
                    self.csv_write_row(wr, descriptions, min_values, max_values)
                wr.writerow(values)
        else:
            with open(self.filename, 'w', newline="") as f:
                wr = csv.writer(f)
                self.csv_write_row(wr, descriptions, min_values, max_values)
                wr.writerow(values)
        set_config_value(STR_FILES, STR_RESULT_NUM, self.result_num)

    @staticmethod
    def csv_write_row(wr, descriptions, min_values, max_values):
        wr.writerow(descriptions)
        wr.writerow(min_values)
        wr.writerow(max_values)

    def closeEvent(self, event):
        self.status_widget.close()


class TWSStatusView(QWidget):
    status_update_signal = Signal(list)
    total_pass_fail_signal = Signal(bool)
    step_error_result_signal = Signal(list)

    def __init__(self):
        super(TWSStatusView, self).__init__()
        self.setWindowTitle("STATUS")
        self.setMinimumWidth(WINDOW_STATUS_WIDTH)
        self.setMinimumHeight(WINDOW_STATUS_HEIGHT)

        # component
        self.total_label = QLabel(str(self.total))
        self.ok_label = QLabel(str(self.ok))
        self.ng_label = QLabel(str(self.ng))
        self.total_reset_button = QPushButton(STR_RESET)

        self.error_count_labels = {
            step: QLabel(get_config_value(STR_ERROR_COUNT, step))
            for step in STEP_SEQUENCES
        }
        self.error_reset_button = QPushButton(STR_RESET)

        # layout
        self.setLayout(layout := QVBoxLayout())
        layout.addWidget(total_groupbox := QGroupBox("TOTAL COUNT"))
        total_groupbox.setLayout(total_layout := QGridLayout())
        total_layout.addWidget(QLabel("TOTAL"), 0, 0)
        total_layout.addWidget(QLabel("OK"), 0, 1)
        total_layout.addWidget(QLabel("NG"), 0, 2)
        total_layout.addWidget(self.total_label, 1, 0)
        total_layout.addWidget(self.ok_label, 1, 1)
        total_layout.addWidget(self.ng_label, 1, 2)
        total_layout.addWidget(self.total_reset_button, 2, 2)

        layout.addWidget(error_groupbox := QGroupBox("ERROR COUNT"))
        error_groupbox.setLayout(error_layout := QGridLayout())
        error_layout.addWidget(QLabel("Error Number"), 0, 1)
        for index, (step, label) in enumerate(self.error_count_labels.items()):
            error_layout.addWidget(QLabel(step), index + 1, 0)
            error_layout.addWidget(label, index + 1, 1)
        error_layout.addWidget(self.error_reset_button, index + 2, 1)

        layout.setStretchFactor(total_groupbox, 3)
        layout.setStretchFactor(error_groupbox, 7)

        self.component_zip()
        self.event_connector()

    def component_zip(self):
        self.total_labels = {
            STR_COUNT_TOTAL: self.total_label,
            STR_COUNT_OK: self.ok_label,
            STR_COUNT_NG: self.ng_label
        }

    def event_connector(self):
        self.total_reset_button.clicked.connect(self.clicked_total_reset_button)
        self.error_reset_button.clicked.connect(self.clicked_error_reset_button)

        self.status_update_signal.connect(self.status_update)

        self.total_pass_fail_signal.connect(self.add_total_count)
        self.step_error_result_signal.connect(self.add_error_count)

    def add_total_count(self, pass_fail):
        self.total += 1
        self.ok += pass_fail
        self.ng += not pass_fail

    def add_error_count(self, pass_fails):
        iter_result = iter(pass_fails)
        self.con += not next(iter_result)
        self.pogo += not next(iter_result)
        self.led += not next(iter_result)
        self.hall += not next(iter_result)
        self.vbat += not next(iter_result)
        self.battery += not next(iter_result)
        self.prox += not next(iter_result)
        self.mic += not next(iter_result)

    def status_update(self, item):
        key, value = item
        if key in [STR_COUNT_TOTAL, STR_COUNT_OK, STR_COUNT_NG]:
            labels = self.total_labels
        else:
            labels = self.error_count_labels
        labels[key].setText(str(value))

    def clicked_total_reset_button(self):
        self.total = 0
        self.ok = 0
        self.ng = 0

    def clicked_error_reset_button(self):
        self.con = 0
        self.pogo = 0
        self.led = 0
        self.hall = 0
        self.vbat = 0
        self.battery = 0
        self.prox = 0
        self.mic = 0

    @property
    def total(self):
        return int(get_config_value(STR_COUNT, STR_COUNT_TOTAL))

    @total.setter
    def total(self, value):
        set_config_value(STR_COUNT, STR_COUNT_TOTAL, value)
        self.status_update_signal.emit([STR_COUNT_TOTAL, value])

    @property
    def ok(self):
        return int(get_config_value(STR_COUNT, STR_COUNT_OK))

    @ok.setter
    def ok(self, value):
        set_config_value(STR_COUNT, STR_COUNT_OK, value)
        self.status_update_signal.emit([STR_COUNT_OK, value])

    @property
    def ng(self):
        return int(get_config_value(STR_COUNT, STR_COUNT_NG))

    @ng.setter
    def ng(self, value):
        set_config_value(STR_COUNT, STR_COUNT_NG, value)
        self.status_update_signal.emit([STR_COUNT_NG, value])

    @property
    def con(self):
        return int(get_config_value(STR_ERROR_COUNT, STR_ERROR_COUNT_CON))

    @con.setter
    def con(self, value):
        set_config_value(STR_ERROR_COUNT, STR_ERROR_COUNT_CON, value)
        self.status_update_signal.emit([STR_ERROR_COUNT_CON, value])

    @property
    def pogo(self):
        return int(get_config_value(STR_ERROR_COUNT, STR_ERROR_COUNT_POGO))

    @pogo.setter
    def pogo(self, value):
        set_config_value(STR_ERROR_COUNT, STR_ERROR_COUNT_POGO, value)
        self.status_update_signal.emit([STR_ERROR_COUNT_POGO, value])

    @property
    def led(self):
        return int(get_config_value(STR_ERROR_COUNT, STR_ERROR_COUNT_LED))

    @led.setter
    def led(self, value):
        set_config_value(STR_ERROR_COUNT, STR_ERROR_COUNT_LED, value)
        self.status_update_signal.emit([STR_ERROR_COUNT_LED, value])

    @property
    def hall(self):
        return int(get_config_value(STR_ERROR_COUNT, STR_ERROR_COUNT_HALL))

    @hall.setter
    def hall(self, value):
        set_config_value(STR_ERROR_COUNT, STR_ERROR_COUNT_HALL, value)
        self.status_update_signal.emit([STR_ERROR_COUNT_HALL, value])

    @property
    def vbat(self):
        return int(get_config_value(STR_ERROR_COUNT, STR_ERROR_COUNT_VBATID))

    @vbat.setter
    def vbat(self, value):
        set_config_value(STR_ERROR_COUNT, STR_ERROR_COUNT_VBATID, value)
        self.status_update_signal.emit([STR_ERROR_COUNT_VBATID, value])

    @property
    def battery(self):
        return int(get_config_value(STR_ERROR_COUNT, STR_ERROR_COUNT_BATTERY))

    @battery.setter
    def battery(self, value):
        set_config_value(STR_ERROR_COUNT, STR_ERROR_COUNT_BATTERY, value)
        self.status_update_signal.emit([STR_ERROR_COUNT_BATTERY, value])

    @property
    def prox(self):
        return int(get_config_value(STR_ERROR_COUNT, STR_ERROR_COUNT_PROX))

    @prox.setter
    def prox(self, value):
        set_config_value(STR_ERROR_COUNT, STR_ERROR_COUNT_PROX, value)
        self.status_update_signal.emit([STR_ERROR_COUNT_PROX, value])

    @property
    def mic(self):
        return int(get_config_value(STR_ERROR_COUNT, STR_ERROR_COUNT_MIC))

    @mic.setter
    def mic(self, value):
        set_config_value(STR_ERROR_COUNT, STR_ERROR_COUNT_MIC, value)
        self.status_update_signal.emit([STR_ERROR_COUNT_MIC, value])
