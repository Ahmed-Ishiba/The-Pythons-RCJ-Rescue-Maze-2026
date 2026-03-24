# SPDX-FileCopyrightText: 2022 Jamon Terrell <github@jamonterrell.com>
# SPDX-License-Identifier: MIT

from rp2 import PIO, StateMachine, asm_pio
from machine import Pin
import utime
from encoder import Motor

motorL = Motor(8,9,1)
motorR = Motor(10,11,0)

@asm_pio(autopush=True, push_thresh=32)
def encoder():
    label("start")
    wait(0, pin, 0)         # Wait for CLK to go low
    jmp(pin, "WAIT_HIGH")   # if Data is low
    mov(x, invert(x))           # Increment X
    jmp(x_dec, "nop1")
    label("nop1")
    mov(x, invert(x))
    label("WAIT_HIGH")      # else
    jmp(x_dec, "nop2")          # Decrement X
    label("nop2")
    
    wait(1, pin, 0)         # Wait for CLK to go high
    jmp(pin, "WAIT_LOW")    # if Data is low
    jmp(x_dec, "nop3")          # Decrement X
    label("nop3")
    
    label("WAIT_LOW")       # else
    mov(x, invert(x))           # Increment X
    jmp(x_dec, "nop4")
    label("nop4")
    mov(x, invert(x))
    wrap()

    
sm1 = StateMachine(1, encoder, freq=125_000_000, in_base=Pin(0), jmp_pin=Pin(1))
sm2 = StateMachine(2, encoder, freq=125_000_000, in_base=Pin(2), jmp_pin=Pin(3))
sm3 = StateMachine(3, encoder, freq=125_000_000, in_base=Pin(4), jmp_pin=Pin(5))
sm4 = StateMachine(4, encoder, freq=125_000_000, in_base=Pin(6), jmp_pin=Pin(7))

sm1.active(1)
sm2.active(1)
sm3.active(1)
sm4.active(1)
while(True):
    motorL.forward(100)
    motorR.forward(100)
    utime.sleep(1)
    sm1.exec("in_(x, 32)")
    sm2.exec("in_(x, 32)")
    sm3.exec("in_(x, 32)")
    sm4.exec("in_(x, 32)")
    x_1 = sm1.get()
    x_2 = sm2.get()
    x_3 = sm3.get()
    x_4 = sm4.get()
    print("first encoder: ",x_1)
    print("second encoder: ",x_2)
    print("third encoder: ",x_3)
    print("fourth encoder: ",x_4)

