
import sys
import message



def send(msg):
     serial = msg.serialize()
     sys.stdout.write(serial)
     sys.stdout.flush()

def receive():
     packet = sys.stdin.readlines()
     msg = Message(packet)
     return msg

     
