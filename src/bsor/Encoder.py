import typing
import struct

def encode_int(fa: typing.BinaryIO, i: int):
    fa.write(i.to_bytes(4, 'little'))

def encode_long(fa: typing.BinaryIO, lo: int):
    fa.write(lo.to_bytes(8, 'little'))

def encode_byte(fa: typing.BinaryIO, by: int):
    fa.write(by.to_bytes(1, 'little'))

def encode_bool(fa: typing.BinaryIO, bo: bool) -> bool:
    if bo:
        wb = 1
    else:
        wb = 0
    fa.write(wb.to_bytes(1, 'little'))

def encode_string(fa: typing.BinaryIO, s: str):
    encode_int(fa, len(s.encode('utf-8')))
    fa.write(s.encode("utf-8"))

def encode_float(fa: typing.BinaryIO, f: float) -> float:
    bytes = bytearray(struct.pack('f', f))
    fa.write(bytes)
