import sys
import app.message as message



def send(msg):
     serial = msg.serialize()
     sys.stdout.write(serial)
     sys.stdout.flush()

def receive():
     packet = sys.stdin.readlines()
     msg = deserialize(packet)
     return msg

     
