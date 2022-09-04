import typing
import struct

def decode_int(fa) -> int:
    bytes = fa.read(4)
    return int.from_bytes(bytes, 'little')

def decode_long(fa) -> int:
    bytes = fa.read(8)
    return int.from_bytes(bytes, 'little')

def decode_byte(fa) -> int:
    bytes = fa.read(1)
    return int.from_bytes(bytes, 'little')

def decode_bool(fa) -> bool:
    return 1 == decode_byte(fa)

def decode_string(fa) -> str:
    length = decode_int(fa)
    if length == 0:
        return ''
    result = fa.read(length)
    result = result.decode("utf-8")
    return result

def decode_float(fa) -> float:
    bytes = fa.read(4)
    try:
        result = struct.unpack('f', bytes)
    except:
        raise;
    return result[0]
