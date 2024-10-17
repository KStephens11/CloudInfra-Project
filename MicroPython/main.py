from machine import Pin
from simple1 import MQTTClient
import ubinascii
import network
import time
import dht

# Function to convert certificate to binary (.der)
def read_cert(filename):
    try:   
        with open(filename, 'r') as f:
            # Get each line from file
            cert = f.read().split('\n')
            # Select all lines except the header and tail
            cert_data = ''.join(cert[1:-1])
            # Return cert as binary
            return ubinascii.a2b_base64(cert_data)
    except Exception as e:
        raise e

# Function to print recieved message from mqtt server
def mqtt_subscribe_callback(topic, msg):
    print(f"Received topic: {topic} message: {msg}")

# 16 = Pin D0 on board
dht_pin = Pin(16, Pin.IN)
dht_sensor = dht.DHT11(dht_pin)


# Connect to the Wi-Fi network
ssid = 'SSID'
password = 'PASSWORD'

# MQTT topics
PUB_TOPIC = "TOPIC/HERE"
SUB_TOPIC = "TOPIC/HERE"

# Private Key and Certificate, uses read_cert function to convert to binary
PRIVATE_KEY = read_cert("cert/PRIVATE_KEY_HERE")
CERTIFICATE = read_cert("cert/CERTIFICATE_HERE")

# AWS info for connection
CLIENT_NAME = "iotconsole-df76009c-e82b-4eca-8541-99bccc96ff9c"
AWS_ENDPOINT = "a3e3ax1jc10k8o-ats.iot.eu-west-1.amazonaws.com"

# Set up WIFI in station mode
station = network.WLAN(network.STA_IF)

# Activate Station
station.active(True)

# Connect to WIFI
station.connect(ssid, password)

# Loop to make sure WIFI is connected before proceeding
while True:
    # Wait for connection
    while not station.isconnected():
        print('Connecting to WIFI')
        time.sleep(1)
    
    # When station connects
    if station.isconnected():
        print('Connected to WIFI')
        print('Network config:', station.ifconfig())
        break

# Create MQTT Client
mqttc = MQTTClient(
    client_id=CLIENT_NAME,
    server=AWS_ENDPOINT,
    port=8883,
    keepalive=120,
    ssl=True,
    ssl_params={'key':PRIVATE_KEY, 'cert':CERTIFICATE, 'server_side':False})

print("Connecting to AWS...")
mqttc.connect()
print("Connected to AWS")

# Set client to listen on subtopic and set callback function to print recieved message
mqttc.set_callback(mqtt_subscribe_callback)
mqttc.subscribe(SUB_TOPIC)

while True:

    # Get Sensor Data
    try:
        dht_sensor.measure()
        message = str(dht_sensor.temperature())
    # If it cannot set to zero
    except:
        message = "0"

    print(f"Publishing message {message} to topic {PUB_TOPIC}")
    # Publish Message to topic
    mqttc.publish(topic=PUB_TOPIC, msg=message, qos=1)
    # Check for message from server
    mqttc.check_msg()
    time.sleep(1)