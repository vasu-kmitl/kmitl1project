###########################################
# Node 101: Main node for the Greenhoude
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

# Use your WiFi Configuration
WiFi_ssid = 'TInhuad_2G'
WiFi_pwd = 'Patiparn'
# WiFi_ssid = 'vNet'
# WiFi_pwd = 'poiuytrewq'

# Use your NETPIE Device Configuration
MQTT_BROKER    = 'mqtt.netpie.io'
MQTT_CLIENT_ID = 'c9925f3c-e9f7-4937-803a-0b0d48900652'
MQTT_TOKEN     = 'QRR6gu8UaGBFbcM6wUjX7ApyowC9XYcL'
MQTT_SECRET    = '7ECnH4LwK4PLYtyAzEfStwk6C46AQrAQ'

# Connect to WiFi
sta_if = network.WLAN(network.STA_IF)   # Station Mode
sta_if.active(True)
sta_if.connect(WiFi_ssid,WiFi_pwd)  # Start Connecting
print('WiFi ...', end='')
while not sta_if.isconnected():
    print('.', end='')
    sleep(0.5)
print(' Connected to', WiFi_ssid, 'on', sta_if.ifconfig()[0])

# Connect to MQTT broker
client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER,
                    user=MQTT_TOKEN, password=MQTT_SECRET,
                    keepalive=60)
print('MQTT ...', end='')
while True:
    try:
        if client.connect() == 0:  # Connected
            print(' Connected to', MQTT_BROKER)
            break
    except:
        print('.', end='')
        sleep(0.5)

# Callback function for responding to the subscribed topics
def on_message(topic,msg):
    print("<-- ", end='')
    print(msg)

#client.setBufferSize(512) #Doesn't work / Find how to increase the buffer
client.set_callback(on_message)
client.subscribe('@shadow/data/updated')

payload = ujson.dumps({'data':{'node':'101'}})
client.publish('@shadow/data/update', payload)

sensor = dht.DHT22(Pin(15))
try:
    sensor.measure()	# The first reading is typically an error
except:
    pass

timer = Timer(0)

status_led = Pin(2,Pin.OUT) # Build-in LED

def status_blink(num):
    for i in range(num):
        status_led.on()
        sleep(0.05)    
        status_led.off()
        sleep(0.15)
        
t = time.localtime()
t_str = ('{}:{}'.format(t[3], t[4]))
#t_str = ('{}-{}-{} :{}:{}'.format(t[0],t[1],t[2],t[3],t[4],t[5]))
print('Start at', t_str)

def timerISR(timer):
    global t, t_str
    err_status = 1 # No Error (One blink)
    try:
        sensor.measure()
    except:
        sensor_data = None
        err_status = 4 # Sensor error (4 blinks)
        
    sensor_data = {
        'data':{
            'temp': sensor.temperature(),
            'humid': sensor.humidity()
            }
        }
    payload = ujson.dumps(sensor_data)
    print('-->', payload)

    try:
        client.publish('@shadow/data/update', payload)
    except:
        err_status = 3 # MQTT error (3 blinks)
        client.connect() # Try to reconnect
    
    if err_status == 1:	# No error
        t = time.localtime()
        t_str = ('{}:{}'.format(t[3], t[4]))
    else:
        print('Err', str(err_status),'at', t_str)
    
    status_blink(err_status)

timer.init(period=5000, mode=Timer.PERIODIC, callback=timerISR)

while True:
    client.check_msg()
