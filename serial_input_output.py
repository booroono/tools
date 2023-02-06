# This is a sample Python script.
import struct
import serial
import variables


def one_byte_to_int(data):
        if type(data) is bytes and len(data) == 1:
            return ord(data)
        else:
            return data


def config_set(data):
    data = one_byte_to_int(data)
    print('OK' if data == 1 else 'NG')


def zig_down(data):
    data = one_byte_to_int(data)
    print('zig down')


def test_end(data):
    data = one_byte_to_int(data)
    print('test end')


def result_data(data):
    data = one_byte_to_int(data)
    step = data[0]
    step_length = struct.unpack('>H', data[1:3])[0]
    print('result data')


def connection_version(data):
    data = one_byte_to_int(data)
    print(f"firmware version v{struct.unpack('>H', data)[0] / 100}")


def ad_read(data):
    data = one_byte_to_int(data)
    data_len = len(data)
    if data_len == 2:
        val = struct.unpack('>H', data)[0]
    elif data_len == 4:
        val = struct.unpack('>I', data)[0]
    elif data_len == 5:
        val = struct.unpack('>I', data[1:])[0], data[0]
    return val


PROCESS_CMD_RX = {
    variables.CMD_CONFIG_SET: config_set,
    variables.CMD_ZIG_DOWN: zig_down,
    variables.CMD_TEST_END: test_end,
    variables.CMD_RESULT_DATA: result_data,
    variables.CMD_CONNECTION_VERSION: connection_version,
    variables.CMD_AD_READ: ad_read,
}


def make_checksum(packet):
    xor = 0
    for data in packet:
        xor ^= data
    return xor


def is_valid_packet(packet):
    if packet[0] != ord(variables.SOT):
        return
    if packet[1] != ord(variables.MCU):
        return
    if packet[-3:] != variables.EOT:
        return

    if packet[-4] != make_checksum(packet[:-4]):
        return

    return True


def parse_packet(packet):
    cmd = packet[2:3]
    data_length = struct.unpack('>H', packet[3:5])[0]
    data = packet[5:5 + data_length]
    func = PROCESS_CMD_RX[cmd]
    a = func(data)
    return a


def make_send_packet(cmd, data):
    """
    cmd와 data를 넣으면 전송 패킷 return
    cmd : 1 byte
    data : bytes
    """
    if type(data) == int:
        data = data.to_bytes(1, byteorder='big')
    send_packet = variables.SOT + variables.UI + struct.pack('>BH', ord(cmd), len(data))
    # send_packet = variables.SOT + variables.MCU + struct.pack('>BH', ord(cmd), len(data))
    send_packet += data
    send_packet += struct.pack('B', make_checksum(send_packet)) + variables.EOT
    return send_packet


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    serial_buff = b''
    s = serial.Serial('com14', 115200)
    while True:
        serial_buff += s.read_until(b'\x20')
        if is_valid_packet(serial_buff):
            parse_packet(serial_buff)
