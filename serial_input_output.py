# This is a sample Python script.
import struct

import serial

from CustomException import AvailableError
from variables import *


def make_checksum(packet):
    xor = 0
    for data in packet:
        xor ^= data
    return xor


def is_valid_packet(packet):
    if packet[0] != SOT:
        return
    if packet[1] != MCU and packet[1] != UI:
        return
    if packet[-3:] != EOT:
        return

    if packet[-4] != make_checksum(packet[:-4]):
        return

    return True


def make_zero_byte_data_packet(cmd):
    send_packet = struct.pack('>3B', SOT, UI, cmd)
    send_packet += struct.pack('>H', 0)
    send_packet += struct.pack('B', make_checksum(send_packet)) + EOT
    return send_packet


def make_one_byte_data_packet(cmd, data):
    send_packet = struct.pack('>3B', SOT, UI, cmd)
    send_packet += struct.pack('>H', 1)
    send_packet += struct.pack('B', data[0])
    send_packet += struct.pack('B', make_checksum(send_packet)) + EOT
    return send_packet


def make_two_bytes_data_packet(cmd, data):
    send_packet = struct.pack('>3B', SOT, UI, cmd)
    send_packet += struct.pack('>H', 2)
    send_packet += struct.pack('>2B', data[0], data[1])
    send_packet += struct.pack('B', make_checksum(send_packet)) + EOT
    return send_packet


def make_five_bytes_data_packet(cmd, data):
    send_packet = struct.pack('>3B', SOT, UI, cmd)
    send_packet += struct.pack('>H', 5)
    send_packet += struct.pack('>5B', data[0], data[1], data[2], data[3], data[4])
    send_packet += struct.pack('B', make_checksum(send_packet)) + EOT
    return send_packet


def make_config_data_packet(cmd, data):
    data_size = len(data) + 2
    step_no = data[0]
    step_size = len(data[1:])
    values = data[1:]

    send_packet = struct.pack('>3B', SOT, UI, cmd)
    send_packet += struct.pack('>H', data_size)
    send_packet += struct.pack('>BH', step_no, step_size)
    send_packet += b''.join([struct.pack('B', value) for value in values])
    send_packet += struct.pack('B', make_checksum(send_packet)) + EOT
    return send_packet


def make_send_packet(*args):
    """
    cmd와 data를 넣으면 전송 패킷 return
    cmd : int
    data : list[int]
    """
    cmd, *data = args
    if cmd in ZERO_BYTE_SEND_CMD:
        return make_zero_byte_data_packet(cmd)
    if cmd in ONE_BYTE_SEND_CMD:
        return make_one_byte_data_packet(cmd, data)
    if cmd == CMD_SOL_VALVE_CONTROL:
        return make_two_bytes_data_packet(cmd, data)
    if cmd == CMD_CONTACT_CONTROL:
        return make_five_bytes_data_packet(cmd, data)
    if cmd == CMD_CONFIG_SET:
        return make_config_data_packet(cmd, data)

    raise AvailableError


def parse_ad_value(datas):
    data_length = len(datas)
    if data_length == 5:
        return struct.unpack('>BI', datas)
    if data_length == 4:
        return struct.unpack('>I', datas)
    if data_length == 2:
        return struct.unpack('>H', datas)

    raise AvailableError


def parse_result(data):
    step_no = data[0]
    step_length = struct.unpack('>H', data[1:3])[0]
    if step_no == RESULT_CONNECTOR_OPEN_SHORT:
        open_short_size = len(data[3:])
        return struct.unpack(f'>BH{open_short_size}I', data)
    if step_no == RESULT_POGO_OPEN_SHORT:
        return struct.unpack('>BH3I', data)
    if step_no == RESULT_LED:
        return struct.unpack('>BH4HI', data)
    if step_no == RESULT_HALL_SENSOR:
        return struct.unpack('>BHH6BHBHBH2BI', data)
    if step_no in [RESULT_VBAT_ID, RESULT_BATTERY]:
        return struct.unpack('>BHH', data)
    if step_no == RESULT_PROX_TEST:
        return struct.unpack('>BH2H2BHB2HB2I', data)
    if step_no == RESULT_MIC_TEST:
        return struct.unpack('>BHI', data)

    raise AvailableError


def parse_packet(packet) -> list:
    cmd = packet[2]
    data_length = struct.unpack('>H', packet[3:5])[0]
    data = packet[5:5 + data_length]

    if data_length == 0:
        return [cmd]
    if data_length == 1:
        return [cmd] + list(struct.unpack('B', data))
    if cmd == CMD_CONNECTION_VERSION:
        return [cmd] + list(struct.unpack('>H', data))
    if cmd == CMD_AD_READ:
        return [cmd] + list(parse_ad_value(data))
    if cmd == CMD_RESULT_DATA:
        return [cmd] + list(parse_result(data))

    raise AvailableError


def parse_received_packet(packet):
    if is_valid_packet(packet):
        try:
            return parse_packet(packet)
        except AvailableError:
            return None
    else:
        return None


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    serial_buff = b''
    s = serial.Serial('com4', 115200)
    while True:
        serial_buff += s.read_until(b'\x20')
        if is_valid_packet(serial_buff):
            parse_packet(serial_buff)
