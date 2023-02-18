import csv
import os.path
import time

from PySide2.QtCore import Signal, Slot
from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QFileDialog, QHeaderView, \
    QTableWidgetItem

from component.components import Button
from logger import logger
from varialble_tools import *


class TWSResultView(QWidget):
    result_received_signal = Signal(list)
    result_send_signal = Signal(bool)
    result_value_clear_signal = Signal()

    make_result_file_signal = Signal()

    def __init__(self):
        super(TWSResultView, self).__init__()
        self.setWindowTitle(STR_RESULT)

        self.setMinimumWidth(WINDOW_WIDTH)
        self.setMinimumHeight(WINDOW_HEIGHT)
        self.setLayout(layout := QVBoxLayout())
        layout.addLayout(load_save_layout := QHBoxLayout())
        layout.addLayout(main_layout := QHBoxLayout())
        layout.setStretchFactor(load_save_layout, 1)
        layout.setStretchFactor(main_layout, 9)

        load_save_layout.addWidget(load_button := QPushButton(STR_LOAD))
        load_save_layout.addWidget(save_button := QPushButton(STR_SAVE))

        main_layout.addLayout(steps_layout := QVBoxLayout())
        main_layout.addLayout(config_layout := QHBoxLayout())
        main_layout.setStretchFactor(steps_layout, 3)
        main_layout.setStretchFactor(config_layout, 7)

        steps = [Button(step) for step in STEP_SEQUENCES]
        for step in steps:
            steps_layout.addWidget(step)
        step_pages = {step: self.make_table_widget(step) for step in STEP_SEQUENCES}
        for table in step_pages.values():
            config_layout.addWidget(table)
        step_pages[STR_CONN_OS].setVisible(True)

        self.load_button = load_button
        self.save_button = save_button
        self.steps = steps
        self.step_pages = step_pages

        self.set_config_list = []

        self.connect_event()

        localtime = time.localtime()
        self.filename = f"./{localtime.tm_year}{localtime.tm_mon:02d}{localtime.tm_mday:02d}.csv"
        num = 0
        while os.path.exists(self.filename):
            self.filename = self.filename[:-4] + num + '.csv'
            num += 1
        self.result_num = 0

    @Slot(list)
    def process_result(self, values):
        step, *datas = values
        table = self.get_table_widget_from_step_num(step - 1)
        float_datas = self.preprocess_result_data(step - 1, datas)
        self.visible_table(table)
        self.result_send_signal.emit(self.compare_min_max_value(table, float_datas))

    @Slot()
    def clear_value(self):
        for table in self.step_pages.values():
            for row in range(table.rowCount()):
                table.takeItem(row, INDEX_COLUMN_VALUE)
                table.takeItem(row, INDEX_COLUMN_RESULT)
        self.visible_table(self.step_pages[STR_CONN_OS])

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
            table.setItem(index, INDEX_COLUMN_VALUE, QTableWidgetItem(str(data)))
            if min_value <= data <= max_value:
                table.setItem(index, INDEX_COLUMN_RESULT, QTableWidgetItem(STR_PASS))
            else:
                ok_flag = False
                table.setItem(index, INDEX_COLUMN_RESULT, QTableWidgetItem(STR_FAIL))
        return ok_flag

    @staticmethod
    def preprocess_result_data(step, datas):
        return_datas = list(map(float, datas))
        if step == STEP_SEQUENCES.index(STR_HALL_SENSOR):
            return_datas[1] /= 10
            return_datas[7] /= 10
            return_datas[9] /= 10
            return_datas[11] /= 10
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

        # event connect
        self.result_received_signal.connect(self.process_result)
        self.result_value_clear_signal.connect(self.clear_value)
        self.make_result_file_signal.connect(self.make_result_file)

    def button_clicked(self):
        button_name = self.sender().text()
        if button_name == STR_LOAD:
            if fname := QFileDialog.getOpenFileName(self, 'Open file', './', 'Data Files(*.dat)')[0]:
                self.load_file(fname)
        if button_name == STR_SAVE:
            if fname := QFileDialog.getSaveFileName(self, 'Save file', './', 'Data Files(*.dat)')[0]:
                self.save_file(fname)

    def step_clicked(self):
        logger.debug(f"{self.sender().text()} button clicked!!!")
        for steps_page in self.step_pages.values():
            steps_page.setVisible(False)

        self.step_pages[self.sender().text()].setVisible(True)

    def get_column_item(self, table, column):
        items = []
        for row in range(table.rowCount()):
            if item := table.item(row, column):
                items.append(item.text())
        return items

    def get_pass_fail(self):
        items = []
        for table in self.step_pages.values():
            items.extend(self.get_column_item(table, INDEX_COLUMN_RESULT))

        return next((item for item in items if item == STR_FAIL), STR_PASS)

    def make_result_file(self):
        descriptions = []
        min_values = []
        max_values = []
        values = []
        for table in self.step_pages.values():
            descriptions.extend(self.get_column_item(table, INDEX_COLUMN_DESCRIPTION))
            min_values.extend(self.get_column_item(table, INDEX_COLUMN_MIN))
            max_values.extend(self.get_column_item(table, INDEX_COLUMN_MAX))
            values.extend(self.get_column_item(table, INDEX_COLUMN_VALUE))

        self.result_num += 1
        if os.path.exists(self.filename):
            with open(self.filename, 'a', newline="") as f:
                wr = csv.writer(f)
                values.insert(0, self.result_num)
                wr.writerow(values)
        else:
            with open(self.filename, 'w', newline="") as f:
                wr = csv.writer(f)
                descriptions.insert(0, 'description')
                min_values.insert(0, 'MIN')
                max_values.insert(0, 'MAX')
                values.insert(0, self.result_num)
                wr.writerow(descriptions)
                wr.writerow(min_values)
                wr.writerow(max_values)
                wr.writerow(values)

