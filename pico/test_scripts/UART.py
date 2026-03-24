from machine import UART, Pin
import time

uart1 = UART(0, baudrate=9600, tx=Pin(12), rx=Pin(13))

while True:
    # Send the message as bytes (note the 'b' prefix)
    print("writing to uart")
    uart1.write(b'h\n')
    time.sleep(1)