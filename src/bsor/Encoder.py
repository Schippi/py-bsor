import typing
import struct

def encode_int(fa: typing.BinaryIO, value: int) -> None:
    bytes = value.to_bytes(4, 'little')
    fa.write(bytes)

def encode_long(fa: typing.BinaryIO, value: int) -> None:
    bytes = value.to_bytes(8, 'little')
    fa.write(bytes)

def encode_byte(fa: typing.BinaryIO, value: int) -> None:
    bytes = value.to_bytes(1, 'little')
    fa.write(bytes)

def encode_bool(fa: typing.BinaryIO, value: bool) -> None:
    encode_byte(fa, 1 if value else 0)

def encode_string(fa: typing.BinaryIO, value: str) -> None:
    encoded_value = value.encode("utf-8")
    encode_int(fa, len(encoded_value))
    fa.write(encoded_value)

# Corresponding encoding function for a string that might be UTF-16
def encode_string_maybe_utf16(fa: typing.BinaryIO, value: str) -> None:
    encoded_value = value.encode("utf-8")
    encode_int(fa, len(encoded_value))
    fa.write(encoded_value)

def encode_float(fa: typing.BinaryIO, value: float) -> None:
    bytes = struct.pack('f', value)
    fa.write(bytes)
