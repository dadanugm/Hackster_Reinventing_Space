from platform import node
import time
import paho.mqtt.client as mqtt
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

import time
import threading
import math

node1 = {}
node2 = {}
node3 = {}
RSSI_device = []
coordinate = []
coodinate_data = ["zero",0.0,0.0]
execute_flag = 0

#matplotlib
#fig, ax = plt.subplots(111)
#triangulation
A = -19.38
B = -48.86
N = 0.817
NLog = 0.72
#coordinate

#def matplotlib_update(frame):
#    global coodinate_data
#    ax.plot(coodinate_data[1],coodinate_data[2],'g-',marker='o')
    #ln.set_data(coodinate_data[1],coodinate_data[2])

def on_connect_aws(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("ESP32/pub")
    #client.publish("Node/sub",json.dumps(message))

def on_message_aws(client, userdata, msg):
    message = json.loads(msg.payload)
    pyld1 = str(message["NODE"]) # get value on key NODE
    pyld2 = str(message["ADDR"]) # get value on key ADDR
    pyld3 = str(message["RSSI"]) # get value on key RSSI
    #print(pyld1)
    #print(pyld2)
    #print(pyld3)

    if (pyld1 == 'NODE1'):
        print ("data node 1")
        node1.update({pyld2:pyld3}) # store key:value on empty dictionary node1
        #print(node1)
    elif (pyld1 == 'NODE2'):
        print ("data node 2")
        node2.update({pyld2:pyld3}) # store key:value on empty dictionary node2
        #print(node2)
    elif (pyld1 == 'NODE3'):
        print ("data node 3")
        node3.update({pyld2:pyld3}) # store key:value on empty dictionary node2
        #print(node3)
    else :
        print ("not recognized node")

def triangulation_calc(rssi):
    global coordinate
    #print("list rssi: ",rssi)
    #print("length rssi: ",len(rssi))
    #extract rrsi from list and convert to range
    distance = []
    for i in range(len(rssi)):
        pow_val = (float(rssi[i])-B)/A
        dist = (pow(10,pow_val))/10
        distance.append(dist)
    print("distance: ",distance)
    #print("len distance: ",len(distance))
    #convert to coordinate, using abc formula
    #print ("d1, d2, d3:", distance[0],distance[1],distance[2])

    ax = 1.36
    bx = 0.12*(34 - (pow(distance[1],2)) - (pow(distance[2],2)))
    cx = (pow(((34 - (pow(distance[1],2)) - (pow(distance[2],2)))/10),2)) - (pow(distance[0],2))
    dx = (pow(bx,2))-(4*ax*cx)
    
    ay = 3.78
    by = 0.56*((pow(distance[1],2)) + (pow(distance[2],2)) -34)
    cy = (pow((( (pow(distance[1],2)) + (pow(distance[2],2)) - 34)/6),2)) - (pow(distance[0],2))
    dy = (pow(by,2))-(4*ay*cy)
    print ("ax, bx, cx, dx:", ax,bx,cx,dx)
    if dx>0:
        X1 = (((-1)*bx) + (math.sqrt(dx))) / (2*ax)
        X2 = (((-1)*bx) - (math.sqrt(dx))) / (2*ax)
        #print ("x1,x2: ", X1,X2)
        Y1 = (((-1)*by) + (math.sqrt(dy))) / (2*ay)
        Y2 = (((-1)*by) - (math.sqrt(dy))) / (2*ay)
        #print ("y1,y2: ", Y1,Y2)
    
        if X1>=0:
            X=X1
        else:
            X=X2
        if Y1>=0:
            Y=Y1
        else:
            Y=Y2
        print("coordinate:",X,Y)
    
    coordinate.append(1)
    coordinate.append(0)

def doing_calculation():
    global node1, node2, node3, coodinate_data, coordinate
    # extracting dictionary 
    len_node1 = len(node1) # measure the length of dict node1
    len_node2 = len(node2) # get dictionary length
    len_node3 = len(node3)
    print(len_node1,len_node2,len_node3) 
    keys_node1 = list(node1.keys()) # convert dictionary key to list
    keys_node2 = list(node2.keys())
    keys_node3 = list(node3.keys())

    #print(str(keys_node1[0])) # print the key[0] of dictionary node 1
    # we get the length of every node, lenght = amount of device
    # scan and combine all RSSI to a single addr of devices
    # put RSSI to payload
    data_tmp = []
    for i in range(len_node1):
        data_tmp.clear()
        for j in range (len_node2):
            for k in range (len_node3):
                if keys_node1[i] == keys_node2[j] == keys_node3[k]:
                    data_tmp.append(node1[keys_node1[i]]) # put RSSI to list
                    data_tmp.append(node2[keys_node2[j]])
                    data_tmp.append(node3[keys_node3[k]])
                    #perform triangulation
                    coordinate.clear()
                    triangulation_calc(data_tmp)
                    print("ble add",keys_node1[i],"pos",coordinate)
                    coodinate_data.append(keys_node1[i])
                    coodinate_data.append(coordinate[0])
                    coodinate_data.append(coordinate[1])
                    #matplotlib_update(coodinate_data)
                else:
                    time.sleep(0.001)
        RSSI_device.append(data_tmp) # put RSSI list to collection
    print("coordinate data",coodinate_data)
    #matplotlib_update(coodinate_data)
    #print(filename[0])

def triangulation_main():
    while(True):
        time.sleep(10)
        print("loop")
        #client_to_aws.publish("ESP32/sub",json.dumps(message))
        doing_calculation()
        coodinate_data.clear()
        RSSI_device.clear()
        node1.clear()
        node2.clear()
        node3.clear()

client_to_aws = mqtt.Client("MqttScript")
client_to_aws.on_connect = on_connect_aws
client_to_aws.on_message = on_message_aws
client_to_aws.tls_set(  ca_certs="D:/Hackster/Hackster_Reinventing_Space/AmazonESP32Cert/Tokyo/AmazonRootCA1.pem", 
                        certfile="D:/Hackster/Hackster_Reinventing_Space/AmazonESP32Cert/Tokyo/certificate.pem.crt", 
                        keyfile="D:/Hackster/Hackster_Reinventing_Space/AmazonESP32Cert/Tokyo/private.pem.key")
client_to_aws.connect("",8883,60)
client_to_aws.loop_start()

th1 = threading.Thread(target=triangulation_main, name="triangulation thread")
th1.start()
print("hello world")
#ax.set_xlim(0,5)
#ax.set_ylim(0,5)
#plt.ion()
#plt.show()
#ani = FuncAnimation(fig, matplotlib_update, frames=(5,5),  blit=True, interval=1000, repeat=True)


#EOF
