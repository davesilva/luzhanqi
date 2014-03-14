import sys
import app.message as message



def send(msg):
     serial = msg.serialize()
     sys.stdout.write(serial)
     sys.stdout.flush()

def receive():
     packet = sys.stdin.readline()
     msg = message.deserialize(packet)
     return msg

     
