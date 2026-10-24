"""A small WebSocket (RFC 6455) implementation for the interactive terminal.

Only what the terminal needs: text frames, ping/pong and close, messages up to 1 MB.
"""
import base64
import hashlib
import json
import struct

GUID = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
MAX_MESSAGE = 1 << 20


class Closed(Exception):
    pass


def accept_key(key):
    return base64.b64encode(hashlib.sha1((key + GUID).encode()).digest()).decode()


def _read_exact(sock, n):
    data = b''
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise Closed()
        data += chunk
    return data


def recv_frame(sock):
    """Returns (opcode, payload bytes). Handles fragmented messages."""
    message = b''
    message_opcode = None
    while True:
        b1, b2 = _read_exact(sock, 2)
        fin = b1 & 0x80
        opcode = b1 & 0x0f
        masked = b2 & 0x80
        length = b2 & 0x7f
        if length == 126:
            length = struct.unpack('!H', _read_exact(sock, 2))[0]
        elif length == 127:
            length = struct.unpack('!Q', _read_exact(sock, 8))[0]
        if length > MAX_MESSAGE:
            raise Closed()
        mask = _read_exact(sock, 4) if masked else b'\0\0\0\0'
        payload = bytearray(_read_exact(sock, length))
        for i in range(length):
            payload[i] ^= mask[i % 4]
        payload = bytes(payload)

        if opcode >= 0x8:            # control frames are never fragmented
            return opcode, payload
        if opcode != 0:
            message_opcode = opcode
        message += payload
        if len(message) > MAX_MESSAGE:
            raise Closed()
        if fin:
            return message_opcode, message


def send_frame(sock, payload, opcode=0x1):
    header = bytes([0x80 | opcode])
    n = len(payload)
    if n < 126:
        header += bytes([n])
    elif n < 65536:
        header += bytes([126]) + struct.pack('!H', n)
    else:
        header += bytes([127]) + struct.pack('!Q', n)
    sock.sendall(header + payload)


def send_json(sock, data):
    send_frame(sock, json.dumps(data, ensure_ascii=False).encode('utf-8'))


def close(sock, code=1000):
    try:
        send_frame(sock, struct.pack('!H', code), opcode=0x8)
    except OSError:
        pass
