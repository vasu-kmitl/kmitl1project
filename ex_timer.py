from machine import Timer
from machine import Pin
 
led = Pin(2,Pin.OUT) # Build-in LED
timer = Timer(0)
 
def timerISR(timer):
  led.value(not led.value())
  
timer.init(period=1000, mode=Timer.PERIODIC, callback=timerISR)

while True:
    pass
