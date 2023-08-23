###########################################
# Node 101: Main node for the Greenhoude
# KMITL One Project 2023
# Ag Instrumentation & IoT Class 1/2023
# Dept. of Agricultural Engineering, KMITL 
###########################################
# https://mpython.readthedocs.io/en/master/library/mPython/umqtt.simple.html
# https://pypi.org/project/ujson/

import dht
from machine import Pin    # Required for dht library
import ujson
import network
from time import sleep
from umqtt.simple import MQTTClient  

WiFi_ssid = 'vNet'
WiFi_pwd = 'poiuytrewq'

MQTT_BROKER    = 'mqtt.netpie.io'
MQTT_CLIENT_ID = 'c9925f3c-e9f7-4937-803a-0b0d48900652'
MQTT_TOKEN     = 'QRR6gu8UaGBFbcM6wUjX7ApyowC9XYcL'
MQTT_SECRET    = '7ECnH4LwK4PLYtyAzEfStwk6C46AQrAQ'

# Connect to WiFi
sta_if = network.WLAN(network.STA_IF)   # Set WiFi Mode to Station
sta_if.active(True)

sta_if.connect(WiFi_ssid,WiFi_pwd)  # Start Connecting
print('WiFi ...', end='')
while not sta_if.isconnected():
    print('.', end='')
    sleep(0.5)
print(' Connected to', sta_if.ifconfig()[0])

# Connect to MQTT broker
client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER,
                    user=MQTT_TOKEN, password=MQTT_SECRET)
print('MQTT ...', end='')
while True:
    try:
        if client.connect() == 0:  # Connected
            print(' Connected to', MQTT_BROKER)
            break
    except:
        print('.', end='')

# Callback function for responding to the subscribed topics
def on_message(topic,msg):
    print("<-- ", end='')
    print(msg)

#client.setBufferSize(512)
client.set_callback(on_message)
client.subscribe('@shadow/data/updated')

payload = ujson.dumps({'data':{'node':'101'}})
client.publish('@shadow/data/update', payload)

sensor = dht.DHT11(Pin(15))
i=0
while True:
    try:
        sleep(5)
        sensor.measure()
        sensor_data = {
            'data':{
                'temp': sensor.temperature(),
                'humid': sensor.humidity()
                }
            }
        payload = ujson.dumps(sensor_data)
        client.publish('@shadow/data/update', payload)
    #    client.publish('@msg/101', payload)
        print(i, end='')
        i = i+1
        print(" -->", payload)
    except:
        pass
  
client.disconnect()
