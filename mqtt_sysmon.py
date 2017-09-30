#!/usr/bin/env python
# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import time,sys
import socket
#import subprocess
import os
import netifaces

# mqtt broker settings
broker="mqtt.ttlexceeded.com"
port=1883
hostname=socket.gethostname()
mqttTopicTree="hosts"
mqttHostTopic=mqttTopicTree+"/"+hostname+"/"

def on_log(mqttClient, userdata, level, buf):
    print("log: " + buf)

def on_disconnect(mqttClient, userdata, flags, rc=0):
    print("Disconnected flags"+"result code "+str(rc)+"mqttClient_id ")
    mqttClient.connected_flag=False

def on_connect(mqttClient, userdata, flags, rc):
    if rc==0:
        mqttClient.connected_flag=True
        print("connected OK")
        mqttClient.subscribe(mqttHostTopic+"command") # subscribe to inbound command topic
        gws = netifaces.gateways()
        addrs = netifaces.ifaddresses(gws['default'][netifaces.AF_INET][1])
        activeIP=addrs[netifaces.AF_INET][0]['addr']
        ret=mqttClient.publish(mqttHostTopic+"ipaddr", activeIP,2, retain=True)
    else:
        print("Bad connection return code = " + rc)
        mqttClient.bad_connection_flag=True

def on_message(mqttClient, userdata, message):
    global mpdCurrentPlaylist
    commandString = str(message.payload.decode("utf-8"))
    if( message.topic == mqttHostTopic+"command"):
        print(commandString + " command received")
        if( commandString == "halt" ):
            ret=mqttClient.publish(mqttHostTopic+"status","halting",2, retain=True) # update current status
            os.system('sudo /bin/systemctl halt')
        elif( commandString == "reboot" ):
            ret=mqttClient.publish(mqttHostTopic+"status","rebooting",2, retain=True) # update current status
            os.system('sudo /bin/systemctl reboot')
        elif( commandString == "poweroff" ):
            ret=mqttClient.publish(mqttHostTopic+"status","powering off",2, retain=True) # update current status
            os.system('sudo /bin/systemctl poweroff')
        else:
            print("unknown command")

mqttClient = mqtt.Client(hostname)      # our client name
# callbacks
# mqttClient.on_log=on_log              # log mqtt event messges
mqttClient.on_connect=on_connect        # 
mqttClient.on_disconnect=on_disconnect  #
mqttClient.on_message=on_message        #

print("Connecting to broker " + broker)
mqttClient.will_set(mqttHostTopic+"status", payload="offline", qos=1, retain=True) # set will to indicate offline status
mqttClient.connect(broker)
mqttClient.loop_start()

# Initialize runtime
run_flag=True
count=1
ret=mqttClient.publish(mqttHostTopic+"status","online",2, retain=True) # update current status

# Main loop
while run_flag:
    count+=1
    mqttClient.loop()
    time.sleep(1)

