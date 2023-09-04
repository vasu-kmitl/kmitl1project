#######################################################
# Node 101: Greenhouse Main node: Mode & Valve Control 
# KMITL One Project 2023                        Ver.1a
# Ag Instrumentation & IoT Class 1/2023
# Dept. of Agricultural Engineering, KMITL 
#######################################################
from machine import Pin, Timer
import time
import ujson
import network
from time import sleep
from umqtt.simple import MQTTClient  

# Use your WiFi Configuration
# WIFI_SSID = 'TInhuad_2G'
# WIFI_PASS = 'Patiparn'
WIFI_SSID = 'vNet'
WIFI_PASS = 'poiuytrewq'

# Use your NETPIE Device Configuration
MQTT_BROKER    = 'mqtt.netpie.io'
MQTT_CLIENT_ID = '40722b81-a120-47f7-9a2a-1e1f7ce8434a'
MQTT_TOKEN     = '1m3VbYJJzo4KySXpAEWHqEmBoPVnpt26'
MQTT_SECRET    = 'sbgGDN17e96WAW1aMuNfsWZG38Gi5Wtk'

#########################################################################
# Configurations
#########################################################################
status_led_pin = Pin(2,Pin.OUT) # Build-in LED
valve_status_pin = Pin(4,Pin.OUT)
err_count = 0

shadow_data = {'node':'101', 'mode':'M', 'valve':0}

#########################################################################
# Defined Functions
#########################################################################
def wifi_connect():
    global wlan
    wlan = network.WLAN(network.STA_IF)   # Station Mode
    wlan.active(True)
    wlan.connect(WIFI_SSID,WIFI_PASS)  # Start Connecting
    print('WiFi: ', end='')
    while not wlan.isconnected():
        print('.', end='')
        sleep(0.5)
    print(WIFI_SSID, '/', wlan.ifconfig()[0])

def mqtt_connect():
    global client
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER,
                        user=MQTT_TOKEN, password=MQTT_SECRET,
                        keepalive=60)
    print('MQTT: ', end='')
    while True:
        try:
            if client.connect() == 0:  # Connected
                print(MQTT_BROKER)
                break
        except:
            print('.', end='')
            sleep(0.5)
    payload = ujson.dumps({'data':shadow_data})
    client.publish('@shadow/data/update', payload)

    client.set_callback(on_message)
    client.subscribe('@shadow/data/updated')
    client.subscribe('@msg/#')

def status_blink(num):
    for i in range(num):
        status_led_pin.on()
        sleep(0.05)    
        status_led_pin.off()
        sleep(0.15)
        
# Callback function for responding to the subscribed topics
def on_message(topic,msg):
    m = ujson.loads(msg)
#    print("received: ", ujson.loads(msg))
    if m['data']['valve'] == 1:
        valve_status_pin.on()
        print('Valve #1: ON')
    else:
        valve_status_pin.off()
        print('Valve #1: OFF')

def timerISR(timer):
    global t, t_str, err_count
    err_code = 1 # No Error (One blink)
    
    try:
        client.ping()	# Check if MQTT error
    except:
        err_code = 3 # MQTT error (3 blinks)
        err_count += 1
        print('Err', err_code, 'at', t_str)
        try:
            client.connect() # Try to reconnect
        except:
            pass
       
    
    if not wlan.isconnected():
        err_code = 2 # WiFi error (2 blinks)
        err_count += 1
        print('Err', err_code, 'at', t_str)
        try:
            wlan.connect(WIFI_SSID,WIFI_PASS)
        except:
            pass
    
   
    if err_code == 1:	# No error / Update timing
        t = time.localtime()
        t_str = ('{}:{:02d}'.format(t[3], t[4]))
    
    status_blink(err_code)

#########################################################################
# Main Program
#########################################################################
wifi_connect()
mqtt_connect()

timer = Timer(0)
timer.init(period=5000, mode=Timer.PERIODIC, callback=timerISR)

t = time.localtime()
t_str = ('{}-{}-{} {}:{:02d}'.format(t[0],t[1],t[2],t[3],t[4]))
print('Start at', t_str)
# https://www.geeksforgeeks.org/python-time-localtime-method/

while True:
    try:
        client.check_msg()
    except:
        pass
                
client.disconnect()
