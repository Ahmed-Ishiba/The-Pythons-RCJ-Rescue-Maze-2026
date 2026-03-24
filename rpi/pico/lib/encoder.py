from rp2 import PIO, StateMachine, asm_pio
from machine import Pin, PWM
import time
import math
import utime

BASE_SPEED = 60
MIN_SPEED = 50
MAX_SPEED = 255

DIAMETER = 70
CIRCUM = DIAMETER * math.pi
PPR = 979.62

def max_val(a, b):
    return a if a > b else b

def min_val(a, b):
    return a if a < b else b

def clamp(v, lo, hi):
    return min(max(v, lo), hi)

def cm_to_pulses(cm):
    return int(cm * (10 * PPR / CIRCUM))

def pulses_to_cm(p):
    return p * (CIRCUM / (10 * PPR))

_30_CM = int(300.0 * PPR / CIRCUM)



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

class Encoder:
    def __init__(self, sm_id:int, pin_a:int, pin_b:int):
        self.sm = StateMachine(sm_id, encoder, 
                           freq=125_000_000, 
                           in_base=Pin(pin_a), 
                           jmp_pin=Pin(pin_b))
        self.sm.active(1)
        self.offset =0
    def value(self):
        self.sm.exec("in_(x,32)")
        return self.sm.get()-self.offset
    
    def distance_value(self):
        return pulses_to_cm(self.value())
    def reset(self):
        self.sm.exec("in_(x,32)")
        self.offset = self.sm.get()

class Motor:
    def __init__(self,dir_pin:int,pwm_pin:int, forward_dir:int):
        self.forward_dir = forward_dir
        self.motor_dir = Pin(dir_pin,Pin.OUT)
        self.motor_pwm = PWM(Pin(pwm_pin))
        self.motor_pwm.freq(20000)
    def forward(self,speed:int):
        d_cycle = int((speed*65535)/255)
        self.motor_dir.value(self.forward_dir)
        self.motor_pwm.duty_u16(d_cycle)
    def reverse(self,speed:int):
        d_cycle = int((speed*65535)/255)
        self.motor_dir.value(not(self.forward_dir))
        self.motor_pwm.duty_u16(d_cycle)
    def stop(self):
        self.motor_dir.value(0)
        self.motor_pwm.duty_u16(0)



    
