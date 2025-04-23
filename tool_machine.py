import contextlib
import struct
import sys
import traceback

import serial
from PySide2.QtCore import QObject, QTimer, Signal
from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton

from variables import *
from varialble_tools import *

READ_TIME = 1000


class TWSView(QWidget):
    out_zigdown = Signal()

    def __init__(self):
        super(TWSView, self).__init__()
        self.setLayout(layout := QVBoxLayout())
        layout.addWidget(zigdown := QPushButton('zig down'))
        zigdown.clicked.connect(self.out_zigdown.emit)


class TWSTool(QApplication):

    def __init__(self):
        super(TWSTool, self).__init__()
        self.serial = TWSToolSerial()

        self.serial.open('com4')
        self.view = TWSView()
        self.view.out_zigdown.connect(self.serial.in_zigdown.emit)
        self.view.show()


class TWSToolSerial(QObject):
    in_write = Signal(bytes)
    in_zigdown = Signal()

    def __init__(self):
        super(TWSToolSerial, self).__init__()
        self.serial = serial.Serial()
        self.serial.baudrate = 115200
        self.read_time = QTimer()
        self.heart_bit_timer = QTimer()
        self.min_data = self.load_file()

        self.buff = b''
        self.event_connect()

    def event_connect(self):
        self.in_write.connect(self.write)
        self.in_zigdown.connect(self.zigdown)

        self.read_time.timeout.connect(self.read)
        self.read_time.setInterval(READ_TIME)
        self.heart_bit_timer.timeout.connect(self.heart_bit)
        self.heart_bit_timer.setInterval(1000)

    def load_file(self):
        with open('min_max_test.dat', 'r') as f:
            lines = f.readlines()
        lines = [line.replace('\n', '') for line in lines]
        step_start_num = [index for index, line in enumerate(lines) if ':' in line]

        steps = []
        for index, step_num in enumerate(step_start_num):
            if index == len(step_start_num) - 1:
                steps.append(lines[step_num + 1:])
                continue
            line_data = [float(line.split('\t')[1]) for line in lines[step_num + 1:step_start_num[index + 1]]]
            if index == STEP_SEQUENCES.index(STR_LED):
                print(line_data)
                for row in range(6):
                    line_data[row] *= 1000
            if index == STEP_SEQUENCES.index(STR_HALL_SENSOR):
                line_data[0] *= 1000
                line_data[1] *= 10
                line_data[7] *= 10
                line_data[9] *= 10
                line_data[11] *= 10
            if index in [STEP_SEQUENCES.index(STR_VBAT_ID),
                             STEP_SEQUENCES.index(STR_BATTERY),
                             STEP_SEQUENCES.index(STR_PROX)]:
                line_data[0] *= 1000
            if index == STEP_SEQUENCES.index(STR_PROX):
                line_data[1] *= 1000
            line_data = list(map(int, line_data))


            steps.append(line_data)

        return steps

    def write(self, data):
        self.heart_bit_timer.start()
        self.serial.write(data)

    def zigdown(self):
        packet = struct.pack('>3BH', SOT, MCU, CMD_ZIG_DOWN, 0)
        self.in_write.emit(packet + struct.pack('B', self.make_checksum(packet)) + EOT)

    def read(self):
        while self.serial.inWaiting():
            try:
                if self.read_one_byte()[0] != SOT:
                    continue
            except IndexError:
                return

            self.buff = b'\x10'
            self.buff += self.read_one_byte()  # sender
            self.buff += self.read_one_byte()  # cmd
            self.buff += b''.join([self.read_one_byte() for _ in range(2)])  # size
            length = struct.unpack('>H', self.buff[-2:])[0]
            self.buff += b''.join([self.read_one_byte() for _ in range(length)])  # data
            self.buff += self.read_one_byte()  # xor
            self.buff += b''.join([self.read_one_byte() for _ in range(3)])  # end

            if not self.is_valid_packet():
                continue
            print(self.buff)
            self.parse_packet()
            break

    def read_one_byte(self):
        with contextlib.suppress(serial.SerialException, TypeError, AttributeError):
            return self.serial.read()

    def heart_bit(self):
        packet = struct.pack('>3BH', SOT, MCU, 115, 0)
        self.in_write.emit(packet + struct.pack('B', self.make_checksum(packet)) + EOT)

    def open(self, comport):
        self.serial.port = comport
        self.serial.open()
        self.read_time.start()
        self.heart_bit_timer.start()

    def is_valid_packet(self):
        if self.buff[0] != SOT:
            return
        if self.buff[1] not in [MCU, UI]:
            return
        if self.buff[-3:] != EOT:
            return

        if self.buff[-4] != self.make_checksum(self.buff[:-4]):
            return

        return True

    def make_checksum(self, packet):
        xor = 0
        for data in packet:
            xor ^= data
        return xor

    def parse_packet(self):
        cmd = self.buff[2]
        step_no = self.buff[6]

        if cmd == CMD_CONFIG_SET:
            write_data = struct.pack('>3B', SOT, MCU, CMD_CONFIG_SET)
            write_data += struct.pack('>H', 1)
            write_data += b'\x01'
            write_data += struct.pack('B', self.make_checksum(write_data)) + EOT
            print("write", write_data)
            self.in_write.emit(write_data)
            return
        if cmd != CMD_TEST_START:
            return

        if step_no > 9 or step_no < 1:
            return

        write_data = struct.pack('>3B', SOT, MCU, CMD_RESULT_DATA)
        if step_no in [RESULT_CONNECTOR_OPEN_SHORT, RESULT_POGO_OPEN_SHORT, RESULT_MIC_TEST]:
            data_len = len(self.min_data[step_no - 1])
            data_struct = f'>{data_len}B'
        if step_no == RESULT_LED:
            data_len = 13
            data_struct = '>6HB'
        if step_no == RESULT_HALL_SENSOR:
            data_len = 19
            data_struct = '>H6BhBhBh3B'
        if step_no in [RESULT_VBAT_ID, RESULT_BATTERY]:
            data_len = 2
            data_struct = '>H'
        if step_no == RESULT_PROX_TEST:
            data_len = 16
            data_struct = '>2H2BHB2HB2B'

        write_data += struct.pack('>HBH', data_len + 3, step_no, data_len)
        write_data += struct.pack(data_struct, *self.min_data[step_no - 1])
        write_data += struct.pack('B', self.make_checksum(write_data)) + EOT
        print(write_data)
        self.in_write.emit(write_data)


if __name__ == "__main__":
    try:
        app = TWSTool()
        sys.exit(app.exec_())
    except Exception as e:
        print(e)
        print(traceback.format_exc())
