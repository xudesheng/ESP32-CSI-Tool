import sys,os
import time
import paho.mqtt.client as mqtt #import the client1
import socket
import serial
broker_address="192.168.1.23" #Broker address
#
# Run this utility to append the current real timestamp.
#
# Run:
# `idf.py monitor | python ../python_utils/serial_append_timestamp.py`
#

#
# Append the first line with ",timestamp"
#
class ReadLine:
    def __init__(self, s):
        self.s = s
        self.buf = bytearray()

    def readline(self):
        i = self.buf.find(b"\n")
        if i >= 0:
            r = self.buf[:i+1]
            self.buf = self.buf[i+1:]
            return r
        while True:
            if serial.VERSION.startswith("3."):
                i = max(1,min(2048, self.s.in_waiting))
            else:
                i = max(1, min(2048, self.s.inWaiting()))
            data = self.s.read(i)
            i = data.find(b"\n")
            if i >= 0:
                r = self.buf + data[:i+1]
                self.buf[0:] = data[i+1:]
                return r
            else:
                self.buf.extend(data)

# while True:
#     line = sys.stdin.readline()

#     if "CSI_DATA" in line:
#         l = line.rstrip()
#         print(line.rstrip() + ",timestamp")
#         break

if len(sys.argv) > 1:
    id = sys.argv[1]
else:
    id = socket.getfqdn()

if len(sys.argv) > 2:
    broker_address = sys.argv[2]

if len(sys.argv) > 3:
    port = sys.argv[3]
else:
    if os.path.exists("/dev/ttyUSB0"):
        port = "/dev/ttyUSB0"
    elif os.path.exists("/dev/cu.usbserial-0001"):
        port = "/dev/cu.usbserial-0001"
    else:
        raise Exception("No serial port found")
        
print("id:{},IP:{},serial port:{}".format(id,broker_address,port))

client = mqtt.Client(id) #create new instance
connected = False
for i in range(5):
    try:
        client.connect(broker_address) #connect to broker
        print("Connecting to broker done.")
        connected = True
    except:
        client=None
        print("Failed to connect to broker")
    
    if connected:
        break
    print("Sleeping for 3 seconds...:{}".format(i))
    time.sleep(3)

#
# Append subsequent lines with the current timestamp
#
ser = serial.Serial(port, 115200)
print("Serial port opened.")
rl = ReadLine(ser)

while True:
    try:
        line = rl.readline().decode()
    except:
        line = ""

    if "CSI_DATA" in line:
        l = line.rstrip() + "," + str(time.time())
        #print(l)
        if client:
            try:
                client.publish("csi/data", "{},{}".format(l,id))
            except:
                client=None
                print("Failed to publish to broker")
