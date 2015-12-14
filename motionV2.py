#!/usr/bin/env python

# Send Grove sensor data periodically to AWS IoT and process actuation commands received.

import time
import datetime
import ssl
import json
import paho.mqtt.client as mqtt
import grovepi
from grovepi import *
import os

# TODO: Name of our Raspberry Pi, also known as our "Thing Name"
deviceName = "g36_pi"
# TODO: Public certificate of our Raspberry Pi, as provided by AWS IoT.
deviceCertificate = "/home/pi/GrovePi/Software/Python/7ed56edd7d-certificate.pem.crt"
# TODO: Private key of our Raspberry Pi, as provided by AWS IoT.
devicePrivateKey = "/home/pi/GrovePi/Software/Python/7ed56edd7d-private.pem.key"
# Root certificate to authenticate AWS IoT when we connect to their server.
awsCert = "/home/pi/GrovePi/Software/Python/aws-iot-rootCA.crt"
isConnected = False

# Assume we connected the Grove Digital Humidity/Temperature Sensor (DHT11) to digital port D2,
# Buzzer Sensor to D8, Grove LED to digital port D4.
#dht_sensor = 2
led = 4
pir_sensor = 8
light = 0
buzzer = 2
button = 3

# This is the main logic of the program.  We connect to AWS IoT via MQTT, send sensor data periodically to AWS IoT,
# and handle any actuation commands received from AWS IoT.
def main():
    global isConnected
    # Create an MQTT client for connecting to AWS IoT via MQTT.
    client = mqtt.Client(deviceName + "_sr")  # Client ID must be unique because AWS will disconnect any duplicates.
    client.on_connect = on_connect  # When connected, call on_connect.
    client.on_message = on_message  # When message received, call on_message.
    client.on_log = on_log  # When logging debug messages, call on_log.

    # Set the certificates and private key for connecting to AWS IoT.  TLS 1.2 is mandatory for AWS IoT and is supported
    # only in Python 3.4 and later, compiled with OpenSSL 1.0.1 and later.
    client.tls_set(awsCert, deviceCertificate, devicePrivateKey, ssl.CERT_REQUIRED, ssl.PROTOCOL_TLSv1_2)

    # Connect to AWS IoT server.  Use AWS command line "aws iot describe-endpoint" to get the address.
    print("Connecting to AWS IoT...")
    client.connect("A1P01IYM2DOZA0.iot.us-west-2.amazonaws.com", 8883, 60)

    # Start a background thread to process the MQTT network commands concurrently, including auto-reconnection.
    client.loop_start()

    # Configure the Grove LED and Buzzer port for output.
    grovepi.pinMode(led, "OUTPUT")
    grovepi.pinMode(pir_sensor,"INPUT")
    grovepi.pinMode(light,"INPUT")
    grovepi.pinMode(buzzer,"OUTPUT")
    grovepi.pinMode(button,"INPUT")
    time.sleep(1)

    # Loop forever.
    while True:
        try:
            # If we are not connected yet to AWS IoT, wait 1 second and try again.
            if not isConnected:
                time.sleep(1)
                continue
            if grovepi.digitalRead(button):
                os.system('/usr/bin/python -W ignore /home/pi/GrovePi/Software/Python/cheeming/relay.py')
                continue
            # Read Grove sensor values. Prepare our sensor data in JSON format.
            payload = {
                "state": {
                    "reported": {
                        # Uncomment the next line if you're using the Grove Analog Temperature Sensor.
                        # "temperature": round(grovepi.temp(temp_sensor, '1.1'), 1),
                        # Comment out the next 2 lines if you're using the Grove Analog Temperature Sensor.
                        #"temperature": grovepi.dht(dht_sensor, 0)[0],  # The first 0 means that the DHT module is DHT11.
                        #"humidity": grovepi.dht(dht_sensor, 0)[1],
			"motion": grovepi.digitalRead(pir_sensor),	
			"light": grovepi.analogRead(light),
                        "timestamp": datetime.datetime.now().isoformat()
                    }
                }
            }
            print("Sending sensor data to AWS IoT...\n" +
                  json.dumps(payload, indent=4, separators=(',', ': ')))

            # Publish our sensor data to AWS IoT via the MQTT topic, also known as updating our "Thing Shadow".
            client.publish("$aws/things/" + deviceName + "/shadow/update", json.dumps(payload))
            print("Sent to AWS IoT")

            # Wait 900 seconds before sending the next set of sensor data.
            time.sleep(10)

        except KeyboardInterrupt:
            break
        except IOError:
            print("Error")


# This is called when we are connected to AWS IoT via MQTT.
# We subscribe for notifications of desired state updates.
def on_connect(client, userdata, flags, rc):
    global isConnected
    isConnected = True
    print("Connected to AWS IoT")
    # Subscribe to our MQTT topic so that we will receive notifications of updates.
    topic = "$aws/things/" + deviceName + "/shadow/update/accepted"
    print("Subscribing to MQTT topic " + topic)
    client.subscribe(topic)


# This is called when we receive a subscription notification from AWS IoT.
# If this is an actuation command, we execute it.
def on_message(client, userdata, msg):
    # Convert the JSON payload to a Python dictionary.
    # The payload is in binary format so we need to decode as UTF-8.
    payload2 = json.loads(msg.payload.decode("utf-8"))
    print("Received message, topic: " + msg.topic + ", payload:\n" +
          json.dumps(payload2, indent=4, separators=(',', ': ')))

    # If there is a desired state in this message, then we actuate, e.g. if we see "led=on", we switch on the LED.
    if payload2.get("state") is not None and payload2["state"].get("desired") is not None:
        # Get the desired state and loop through all attributes inside.
        desired_state = payload2["state"]["desired"]
        for attribute in desired_state:
            # We handle the attribute and desired value by actuating.
            value = desired_state.get(attribute)
            actuate(client, attribute, value)


# Control my actuators based on the specified attribute and value, e.g. "led=on" will switch on my LED.
def actuate(client, attribute, value):
    if attribute == "timestamp":
        # Ignore the timestamp attribute, it's only for info.
        return
    print("Setting " + attribute + " to " + value + "...")
    if attribute == "led":
        # We actuate the LED for "on", "off" or "flash1".
        if value == "Motion_Detected":
            # Switch on LED.
            grovepi.digitalWrite(led, 1)
            send_reported_state(client, "led", "Motion_Detected")
            time.sleep(5)
            grovepi.digitalWrite(led,0)
            send_reported_state(client, "led", "off")
            os.system('/usr/bin/fswebcam /home/pi/GrovePi/Software/Python/IMAGE/$(date +%Y%m%d_%H%M).jpg')
            os.system('/usr/bin/mpack -s "Motion Detected Room G36" /home/pi/GrovePi/Software/Python/IMAGE/$(date +%Y%m%d_%H%M).jpg cheeming@tp.edu.sg &') 
            time.sleep(1)
            return
        elif value == "flash2":
            # Switch on LED, wait 1 second, switch it off.
            grovepi.digitalWrite(led, 1)
            send_reported_state(client, "led", "on")
            time.sleep(.5)

            grovepi.digitalWrite(led, 0)
            send_reported_state(client, "led", "off")
            time.sleep(.5)

            grovepi.digitalWrite(led,1)
            send_reported_state(client, "led", "on")
            time.sleep(.5)

            grovepi.digitalWrite(led,0)
            send_reported_state(client, "led", "off")
            time.sleep(.5)
            return
    # We actuate the buzzer for "on" or "off"
    if attribute == "buzzer":
        if value == "Projector_On":
            # Switch on Buzzer.
            grovepi.digitalWrite(buzzer, 1)
            #send_reported_state(client, "buzzer", "buzzy1")
            os.system('/usr/bin/python -W ignore /home/pi/GrovePi/Software/Python/cheeming/relay.py')
            time.sleep(1)
            grovepi.digitalWrite(buzzer, 0)
            os.system('/usr/bin/python -W ignore /home/pi/GrovePi/Software/Python/cheeming/relayoff.py')
            send_reported_state(client, "buzzer", "buzzy1")
            return
        elif value == "buzzy2":
            # Switch off Buzzer.
            grovepi.digitalWrite(buzzer, 1)
            time.sleep(.5)
            grovepi.digitalWrite(buzzer, 0)
            #send_reported_state(client, "buzzer", "off")
            time.sleep(.5)
            grovepi.digitalWrite(buzzer, 1)
            #send_reported_state(client, "buzzer", "on")
            time.sleep(.5)
            grovepi.digitalWrite(buzzer, 0)
            send_reported_state(client, "buzzer", "buzzy2")
            return
    # Show an error if attribute or value are incorrect.
    print("Error: Don't know how to set " + attribute + " to " + value)


# Send the reported state of our actuator tp AWS IoT after it has been triggered, e.g. "led": "on".
def send_reported_state(client, attribute, value):
    # Prepare our sensor data in JSON format.
    payload = {
        "state": {
            "reported": {
                attribute: value,
                "timestamp": datetime.datetime.now().isoformat()
            }
        }
    }
    print("Sending sensor data to AWS IoT...\n" +
          json.dumps(payload, indent=4, separators=(',', ': ')))

    # Publish our sensor data to AWS IoT via the MQTT topic, also known as updating our "Thing Shadow".
    client.publish("$aws/things/" + deviceName + "/shadow/update", json.dumps(payload))
    print("Sent to AWS IoT")


# Print out log messages for tracing.
def on_log(client, userdata, level, buf):
    print("Log: " + buf)


# Start the main program.
main()

