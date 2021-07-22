# adapted from: https://github.com/gianlucoDev/braccino

from collections import namedtuple
import struct
from cobs import cobs

from serial import Serial, to_bytes

# the 0 byte signals the end of a packet
END_MARKER = b'\x00'

# django -> arduino
SETPOS_ID = 0x01
POS_QUERY_ID = 0x02
SETSPEED_ID = 0x03

# django <- arduino
HELLO_ID = 0x00
SETPOS_REPLY_ID = 0x01
POS_QUERY_REPLY_ID = 0x02


# how many seconds should the Django app wait for the
# Arduino to be ready before showing an error
MAX_CONNECTION_WAIT_TIME = 20

Angles = namedtuple('Angles',
                    field_names=('base', 'shoulder', 'elbow',
                                 'wrist_ver', 'wrist_rot', 'gripper'))


def _write_packet(serial, data):
    data = to_bytes(data)
    packet = cobs.encode(data) + END_MARKER
    serial.write(packet)


def _read_packet(serial, timeout=None):
    serial.timeout = timeout

    packet = serial.read_until(expected=END_MARKER)
    if not packet:
        return None

    packet = packet[:-1]  # remove trailing 0 byte
    data = cobs.decode(packet)
    return data


def connect(path):
    serial = Serial(path, 38400)
    data = _read_packet(serial, timeout=MAX_CONNECTION_WAIT_TIME)
    packet_id, confirmation_byte = struct.unpack('<BB', data)

    if packet_id == HELLO_ID and confirmation_byte == 0xAA:
        return serial
    else:
        return None


def set_angles(serial, angles):
    send_data = struct.pack(
        '<BBBBBBB',
        SETPOS_ID,
        angles.base,
        angles.shoulder,
        angles.elbow,
        angles.wrist_ver,
        angles.wrist_rot,
        angles.gripper,
    )
    _write_packet(serial, send_data)


def is_on_position(serial):
    send_data = struct.pack('<B', POS_QUERY_ID)
    _write_packet(serial, send_data)

    recv_data = _read_packet(serial, timeout=1)
    _id, ok = struct.unpack('<B?', recv_data)
    return ok


def wait_for_position_reached(serial):
    while not is_on_position(serial):
        pass


def set_speed(serial, speed):
    data = struct.pack('<BB', SETSPEED_ID, speed)
    _write_packet(serial, data)
