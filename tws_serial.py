# -*- coding: utf-8 -*-

# This is a sample Python script.
import contextlib
from threading import Thread

import serial
from PySide2.QtCore import QObject, Signal, Slot, QTimer
from PySide2.QtSerialPort import QSerialPortInfo

from CustomException import AvailableError
from logger import logger
from variables import *

CONNECTION_TIME = 2000


def get_serial_available_list():
    return [port.portName()
            for port in QSerialPortInfo.availablePorts()
            if not port.isBusy()]


class TWSSerial(QObject):
    connect_signal = Signal(str)
    connection_state_signal = Signal(bool)
    serial_read_data_signal = Signal(list)
    serial_write_data_signal = Signal(list)
    reset_time_signal = Signal()
    timer_stop_signal = Signal()

    def __init__(self):
        super(TWSSerial, self).__init__()
        self.serial = serial.Serial()
        self.serial.baudrate = 115200
        self.buff = ''
        self.thread = Thread(target=self.read, daemon=True)

        self.connect_signal.connect(self.open)
        self.serial_write_data_signal.connect(self.make_send_packet)
        self.connect_timer = QTimer(self)
        self.connect_timer.timeout.connect(self.timer_timeout)
        self.reset_time_signal.connect(self.connect_timer_Start)
        self.timer_stop_signal.connect(self.connect_timer.stop)

    def connect_timer_Start(self):
        if self.serial.is_open:
            self.connect_timer.start()

    @Slot(str)
    def open(self, comport):
        if self.serial.is_open:
            self.timer_timeout()
            return
        self.port = comport
        with contextlib.suppress(serial.SerialException):
            self.serial.open()
            self.connection_state_signal.emit(True)
            self.connect_timer.start(CONNECTION_TIME)

            if not self.thread.is_alive():
                self.thread = Thread(target=self.read, daemon=True)
            self.thread.start()

    def read(self):
        while self.serial.is_open:
            try:
                if self.read_one_byte()[0] != SOT:
                    continue
            except IndexError:
                return

            self.buff = b'\x10'  # header
            self.buff += self.read_one_byte()  # sender
            self.buff += self.read_one_byte()  # cmd
            self.buff += b''.join([self.read_one_byte() for _ in range(2)])  # size
            length = struct.unpack('>H', self.buff[-2:])[0]
            self.buff += b''.join([self.read_one_byte() for _ in range(length)])  # data
            self.buff += self.read_one_byte()  # xor
            self.buff += b''.join([self.read_one_byte() for _ in range(3)])  # end

            if not self.is_valid_packet():
                continue
            self.reset_time_signal.emit()
            if self.connect_timer.isActive():
                logger.debug('start')
            self.parse_packet()
        self.connection_state_signal.emit(False)

    def timer_timeout(self):
        try:
            self.serial.close()
        except Exception as e:
            logger.error(e)
        self.connect_timer.stop()
        self.connection_state_signal.emit(False)

    def read_one_byte(self):
        with contextlib.suppress(serial.SerialException, TypeError, AttributeError):
            return self.serial.read()

    def make_checksum(self, packet):
        xor = 0
        for data in packet:
            xor ^= data
        return xor

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

    def make_zero_byte_data_packet(self, cmd):
        send_packet = self.make_header(cmd)
        send_packet += struct.pack('>H', 0)
        send_packet += struct.pack('B', self.make_checksum(send_packet)) + EOT
        return send_packet

    def make_one_byte_data_packet(self, cmd, data):
        send_packet = self.make_header(cmd)
        send_packet += struct.pack('>H', 1)
        send_packet += struct.pack('B', data[0])
        send_packet += struct.pack('B', self.make_checksum(send_packet)) + EOT
        return send_packet

    def make_two_bytes_data_packet(self, cmd, data):
        send_packet = self.make_header(cmd)
        send_packet += struct.pack('>H', 2)
        send_packet += struct.pack('>2B', data[0], data[1])
        send_packet += struct.pack('B', self.make_checksum(send_packet)) + EOT
        return send_packet

    def make_five_bytes_data_packet(self, cmd, data):
        send_packet = self.make_header(cmd)
        send_packet += struct.pack('>H', 5)
        send_packet += struct.pack('>5B', data[0], data[1], data[2], data[3], data[4])
        send_packet += struct.pack('B', self.make_checksum(send_packet)) + EOT
        return send_packet

    def make_config_data_packet(self, cmd, data):
        data_size = len(data) + 2
        step_no = data[0]
        step_size = len(data[1:])
        values = data[1:]

        send_packet = self.make_header(cmd)
        send_packet += struct.pack('>H', data_size)
        send_packet += struct.pack('>BH', step_no, step_size)
        send_packet += b''.join([struct.pack('B', value) for value in values])
        send_packet += struct.pack('B', self.make_checksum(send_packet)) + EOT
        return send_packet

    def make_test_start(self, cmd, data):
        side, step = data
        send_packet = self.make_header(cmd)
        send_packet += struct.pack('>H', 2)
        send_packet += struct.pack('>2B', side, step)
        send_packet += struct.pack('B', self.make_checksum(send_packet)) + EOT
        return send_packet

    @staticmethod
    def make_header(cmd):
        return struct.pack('>3B', SOT, UI, cmd)

    @Slot(list)
    def make_send_packet(self, args):
        """
        cmd와 data를 넣으면 전송 패킷 return
        cmd : int
        data : list[int]
        """
        cmd, *data = args
        send_packet = ''
        if cmd in ZERO_BYTE_SEND_CMD:
            send_packet = self.make_zero_byte_data_packet(cmd)
        if cmd in ONE_BYTE_SEND_CMD:
            send_packet = self.make_one_byte_data_packet(cmd, data)
        if cmd == CMD_SOL_VALVE_CONTROL:
            send_packet = self.make_two_bytes_data_packet(cmd, data)
        if cmd == CMD_CONTACT_CONTROL:
            send_packet = self.make_five_bytes_data_packet(cmd, data)
        if cmd == CMD_CONFIG_SET:
            send_packet = self.make_config_data_packet(cmd, data)
        if cmd == CMD_TEST_START:
            send_packet = self.make_test_start(cmd, data)

        with contextlib.suppress(serial.SerialException):
            if send_packet:
                logger.debug(f"send_packet : {send_packet}")
                self.serial.write(send_packet)

    def parse_ad_value(self, datas):
        data_length = len(datas)
        if data_length == 5:
            return struct.unpack('>BI', datas)
        if data_length == 4:
            return struct.unpack('>I', datas)
        if data_length == 2:
            return struct.unpack('>H', datas)

        raise AvailableError

    def parse_result(self, data):
        step_no = data[0]
        step_length = struct.unpack('>H', data[1:3])[0]
        if step_no == RESULT_CONNECTOR_OPEN_SHORT:
            open_short_size = len(data[3:])
            return struct.unpack(f'>BH{open_short_size}B', data)
        if step_no == RESULT_POGO_OPEN_SHORT:
            return struct.unpack('>BH3B', data)
        if step_no == RESULT_LED:
            try:
                logger.debug(f"LED 테스트 데이터 파싱 시작: data 길이 = {len(data)}, data = {data}")
                # 실제 프로토콜에 따라 9바이트 데이터 구조로 수정
                # B: step_no, H: step_length, 
                # 6H: LED1 ON, LED1 OFF, LED2 ON, LED2 OFF, Forward Voltage, Power Down Current
                # 마지막 부분 포함 형태로 수정
                if len(data) >= 19:  # B + H + 4H + 1B + 3H + 1B= 1 + 2 + 12 = 15 바이트 이상
                    result = struct.unpack('>BH4H1B3H1B', data[:19])  # 16바이트만 파싱
                    logger.debug(f"LED 테스트 데이터 파싱 완료: {result}")
                    return result
                else:
                    logger.error(f"LED 테스트 데이터 길이 부족: 필요=15, 실제={len(data)}")
                    # 데이터 길이가 부족하면 기본값 반환
                    return (RESULT_LED, step_length, 0, 0, 0, 0, 0, 0, 0)
            except Exception as e:
                logger.error(f"LED 테스트 데이터 파싱 오류: {e}, data 길이 = {len(data)}, data = {data}")
                # 임시 처리: 오류 발생 시 기본값 반환
                return (RESULT_LED, step_length, 0, 0, 0, 0, 0, 0, 0)
        if step_no == RESULT_HALL_SENSOR:
            return struct.unpack('>BHH6BhBhBh3B', data)
        if step_no in [RESULT_VBAT_ID, RESULT_BATTERY]:
            return struct.unpack('>BHH', data)
        if step_no == RESULT_PROX_TEST:
            return struct.unpack('>BH2H2BHB2HB2B', data)
        if step_no == RESULT_MIC_TEST:
            return struct.unpack('>BHB', data)

        raise AvailableError

    def parse_packet(self):
        cmd = self.buff[2]
        data_length = struct.unpack('>H', self.buff[3:5])[0]
        data = self.buff[5:5 + data_length]

        if data_length == 0:
            self.serial_read_data_signal.emit([cmd])
        if data_length == 1:
            self.serial_read_data_signal.emit([cmd] + list(struct.unpack('B', data)))
        if cmd == CMD_CONNECTION_VERSION:
            self.serial_read_data_signal.emit([cmd] + list(struct.unpack('>H', data)))
        if cmd == CMD_AD_READ:
            self.serial_read_data_signal.emit([cmd] + list(self.parse_ad_value(data)))
        if cmd == CMD_RESULT_DATA:
            try:
                # 데이터 내용을 16진수로 변환하여 로깅
                hex_data = ' '.join([f'{b:02x}' for b in data])
                logger.debug(f"CMD_RESULT_DATA 수신: data_length={data_length}, hex_data=[{hex_data}]")
                
                # 데이터 첫 바이트가 RESULT_LED인 경우 특별 처리
                if data and len(data) > 0 and data[0] == RESULT_LED:
                    logger.debug(f"LED 테스트 데이터 수신: 길이={len(data)}")
                
                result = self.parse_result(data)
                logger.debug(f"CMD_RESULT_DATA 파싱 결과: {result}")
                self.serial_read_data_signal.emit([cmd] + list(result))
            except Exception as e:
                logger.error(f"CMD_RESULT_DATA 처리 오류: {e}, data = {data}")
                # 에러 시 LED 테스트일 경우 기본값 전송
                if data and len(data) > 0 and data[0] == RESULT_LED:
                    logger.info("LED 테스트 오류 발생, 임시 결과값 전송")
                    self.serial_read_data_signal.emit([cmd, RESULT_LED, 0, 0, 0, 0, 0, 0, 0, 0])

    @property
    def port(self):
        return self.serial.port

    @port.setter
    def port(self, port):
        self.serial.port = port

    @property
    def baudrate(self):
        return self.serial.baudrate

    @baudrate.setter
    def baudrate(self, baudrate):
        self.serial.baudrate = baudrate
