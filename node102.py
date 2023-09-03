###########################################
# Node 102: Greenhouse's Temp & RH (DHT22)
# KMITL One Project 2023
# Ag Instrumentation & IoT Class 1/2023
# Dept. of Agricultural Engineering, KMITL 
###########################################

from machine import Pin, Timer
import time
import ujson
import network
from time import sleep
from umqtt.simple import MQTTClient  
import dht

#########################################################################
# Configurations
#########################################################################
status_led = Pin(2,Pin.OUT) # Build-in LED
err_count = 0

# WIFI_SSID = 'TInhuad_2G'
# WIFI_PASS = 'Patiparn'
WIFI_SSID = 'vNet'
WIFI_PASS = 'poiuytrewq'

MQTT_BROKER    = 'mqtt.netpie.io'
MQTT_CLIENT_ID = 'c9925f3c-e9f7-4937-803a-0b0d48900652'
MQTT_TOKEN     = 'QRR6gu8UaGBFbcM6wUjX7ApyowC9XYcL'
MQTT_SECRET    = '7ECnH4LwK4PLYtyAzEfStwk6C46AQrAQ'

#########################################################################
# Defined Functions
#########################################################################
def sensor_connect():
    global sensor
    sensor = dht.DHT22(Pin(15))
    print('DHT22: ', end='')
    while True:		# Frequently finds few first readings 
        try:
            if sensor.measure() == None: # Available
                print('Ready')
                break
        except:
            print('.', end='')
            sleep(0.5)
 
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
    client.set_callback(on_message)
    client.subscribe('@shadow/data/updated')

def status_blink(num):
    for i in range(num):
        status_led.on()
        sleep(0.05)    
        status_led.off()
        sleep(0.15)
        
# Callback function for responding to the subscribed topics
def on_message(topic,msg):
    m = ujson.loads(msg)
#    print("<- ", end='')
#    print(ujson.loads(msg))
#    print(m['data'])

sensor_data = {'temp':None, 'humid':None}

def timerISR(timer):
    global t, t_str, err_count, sensor_data
    err_code = 1 # No Error (One blink)
    
    try:
        sensor.measure()
        sensor_data['temp']  = sensor.temperature()
        sensor_data['humid'] = sensor.humidity()
    except:
        err_code = 4 # Sensor error (4 blinks)
        err_count += 1
        print('Err', err_code, 'at', t_str)
        sensor_data['temp']  = None
        sensor_data['humid'] = None
        
    payload = ujson.dumps({'data':sensor_data})

    try:
        client.publish('@shadow/data/update', payload)
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
    
    print('->', payload, 'err_count =', err_count)
    
    if err_code == 1:	# No error / Update timing
        t = time.localtime()
        t_str = ('{}:{:02d}'.format(t[3], t[4]))
    
    status_blink(err_code)
    
#########################################################################
# Main Program
#########################################################################
sensor_connect()
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
