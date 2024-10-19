from machine import Pin
from simple1 import MQTTClient
import random
import ubinascii
import network
import time
import dht
import ntptime

class Client:
    def __init__(self, client_id, sensor_type):
        self.client_id = client_id
        self.temperature = None
        self.humidity = None
        self.type = sensor_type
        
        if self.type == 1:
            # 16 = Pin D0 on board
            self.dht_pin = Pin(16, Pin.IN)
            self.dht_sensor = dht.DHT11(self.dht_pin)
            
        
    def get_data(self):
        if self.type == 0:
            result = str(self.client_id) + ',' + str(randrange(10,30)) + ',' + str(randrange(30,60))
        elif self.type == 1:
            try:
                self.dht_sensor.measure()
                result = str(self.client_id) + ',' + str(self.dht_sensor.temperature()) + ',' + str(self.dht_sensor.humidity())
            except:
                result = str(self.client_id) + ',' + '0'+ ',' + '0'
        else:
            result = "ERROR: INVALID SENSOR TYPE"
        
        return result

def randrange(start, stop=None):
    if stop is None:
        stop = start
        start = 0
    upper = stop - start
    bits = 0
    pwr2 = 1
    while upper > pwr2:
        pwr2 <<= 1
        bits += 1
    while True:
        r = random.getrandbits(bits)
        if r < upper:
            break
    return r + start

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

CLIENT_ID = 0

# MQTT topics
PUB_TOPIC = f"TOPIC-{CLIENT_ID}/pub"
SUB_TOPIC = f"TOPIC-{CLIENT_ID}/sub"

# AWS info for connection
CLIENT_NAME = f"CLIENT_NAME-{CLIENT_ID}"
AWS_ENDPOINT = "ENDPOINT HERE"

# Connect to the Wi-Fi network
ssid = 'SSID'
password = 'PASSWORD'

# Private Key and Certificate, uses read_cert function to convert to binary
PRIVATE_KEY = read_cert("cert/private.key")
CERTIFICATE = read_cert("cert/certificate.crt")

# Create sensor object, 1st arg ID, 2nd type (0=random,1=DHT)
sensor = Client(CLIENT_ID,0)

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

# Sync Time
try:
    ntptime.host="0.ie.pool.ntp.org"
    ntptime.settime()
except:
    pass

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

current_time = None



while True:

    # Get Current time
    current_time = time.localtime()

    # Format date
    date = f"{current_time[2]}/{current_time[1]}/{current_time[0]} {current_time[3]+1}:{current_time[4]}:{current_time[5]}"

    message = date + ',' + sensor.get_data()

    print(f"Publishing message {message} to topic {PUB_TOPIC}")

    # Publish Message to topic
    mqttc.publish(topic=PUB_TOPIC, msg=message, qos=1)

    # Check for message from server
    mqttc.check_msg()
    time.sleep(15)