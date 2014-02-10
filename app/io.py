
import sys
import message



def send(msg):
     serial = msg.serialize()
     sys.stdout.write(serial)
     sys.stdout.flush()

def recieve():
     packet = sys.stdin.readlines()
     msg = Message(packet)
     return msg

     
