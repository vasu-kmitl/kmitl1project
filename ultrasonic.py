# https://github.com/adafruit/Adafruit_Learning_System_Guides/blob/main/DYP_ultrasonics/me007ys.py
import time
from machine import UART

uart = UART(2, 9600) # Rx/Tx 16/17
uart.init(9600, bits=8, parity=None, stop=1) # init with given parameters

def read_me007ys(ser, timeout = 1.0):
    ts = time.monotonic()
    buf = bytearray(3)
    idx = 0

    while True:
        # Option 1, we time out while waiting to get valid data
        if time.monotonic() - ts > timeout:
            raise RuntimeError("Timed out waiting for data")

        c = ser.read(1)[0]
        #print(c)
        if idx == 0 and c == 0xFF:
            buf[0] = c
            idx = idx + 1
        elif 0 < idx < 3:
            buf[idx] = c
            idx = idx + 1
        else:
            chksum = sum(buf) & 0xFF
            if chksum == c:
                return (buf[1] << 8) + buf[2]
            idx = 0
    return None

while True:
    dist = read_me007ys(uart)
    print("Distance = %d mm" % dist)
