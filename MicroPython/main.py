from machine import Pin
from simple1 import MQTTClient
import random
import ubinascii
import network
import time
import dht
import ntptime

##### Configuration #####

# Client ID
CLIENT_ID = 0

# Sensor type, 0 = random, 1 = DHT
SENSOR_TYPE = 0

# DHT SENSOR PIN, 16 = D0
DHT_SENSOR_PIN = 16

# WIFI SSID and Password
ssid = 'SSID'
password = 'PASS'

# AWS info for connection
CLIENT_NAME = f"esp-python-{CLIENT_ID}"
AWS_ENDPOINT = "ENDPOINT"

# Directory for private key and certificate
PRIVATE_KEY_DIR = "cert/private.key"
CERTIFICATE_DIR = "cert/certificate.crt"

# MQTT topics
PUB_TOPIC = f"esp-python-{CLIENT_ID}/pub"
SUB_TOPIC = f"esp-python-{CLIENT_ID}/sub"


##### Script #####

class Client:
    def __init__(self, client_id, sensor_type):
        self.client_id = client_id
        self.temperature = None
        self.humidity = None
        self.type = sensor_type
        
        if self.type == 0:
            self.temperature = randrange(12,28)
            self.humidity = randrange(40,60)

        if self.type == 1:
            self.dht_pin = Pin(DHT_SENSOR_PIN, Pin.IN)
            self.dht_sensor = dht.DHT11(self.dht_pin)
            
        
    def get_data(self):
        if self.type == 0:
            if self.temperature > 32:
                self.temperature +=  randrange(-2,0)
            elif self.temperature < 8:
                self.temperature +=  randrange(0,2)
            else:
                self.temperature +=  randrange(-2,2)

            if self.humidity > 65:
                self.humidity +=  randrange(-2,0)
            elif self.humidity < 35:
                self.humidity +=  randrange(0,2)
            else:
                self.humidity += randrange(-2,2)

        elif self.type == 1:
            try:
                self.dht_sensor.measure()
                self.temperature = self.dht_sensor.temperature()
                self.humidity = self.dht_sensor.humidity()
            except:
                self.temperature = 0
                self.humidity = 0
        else:
            result = "ERROR: INVALID SENSOR TYPE"
        
        result = str(self.client_id) + ',' + str(self.temperature) + ',' + str(self.humidity)
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




# Create sensor object
sensor = Client(CLIENT_ID,SENSOR_TYPE)

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

# Private Key and Certificate, uses read_cert function to convert to binary
PRIVATE_KEY = read_cert(PRIVATE_KEY_DIR)
CERTIFICATE = read_cert(CERTIFICATE_DIR)

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
    date = f"{current_time[2]}/{current_time[1]}/{current_time[0]} {current_time[3]}:{current_time[4]}:{current_time[5]}"

    message = date + ',' + sensor.get_data()

    print(f"Publishing message {message} to topic {PUB_TOPIC}")

    # Publish Message to topic
    mqttc.publish(topic=PUB_TOPIC, msg=message, qos=1)

    # Check for message from server
    mqttc.check_msg()
    time.sleep(15)