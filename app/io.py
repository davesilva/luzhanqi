import sys
import logging
import app.message as message

log = logging.getLogger("io")


def send(msg):
    serial = msg.serialize()
    sys.stdout.write(serial)
    sys.stdout.flush()
    log.debug("sent: " + serial)


def receive():
    packet = sys.stdin.readline()
    log.debug("received: " + packet)
    msg = message.deserialize(packet)
    return msg
