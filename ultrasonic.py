# https://wiki.dfrobot.com/ME007YS%20Waterproof%20Ultrasonic%20Sensor%20SKU:%20SEN0312#target_5
# https://github.com/adafruit/Adafruit_Learning_System_Guides/blob/main/DYP_ultrasonics/me007ys.py

import time
from machine import UART

uart = UART(2, 9600) # Rx/Tx 16/17

def read_dist():    # Read the distance from ME007YS
    timeout = 5.0
    ts = time.time()

    while True:
        if time.time() - ts > timeout:     # Set timeout error
            raise RuntimeError("Timed out waiting for data")
        
        try:
            header = uart.read(1)          # fine the header byte 0xFF 
            if header[0] == 0xFF:
                data = uart.read(2)        # read following 2 bytes for data
                crc = uart.read(1)         # read the checksum byte
                if crc[0] == sum(header + data) & 0xFF:		# compare the checksum
                    return (data[0] << 8) + data[1]         # convert into distance and return the value
        except:
            pass    # skip reading errors (a lot)

while True:
    dist = read_dist()
    print(dist,'mm')
