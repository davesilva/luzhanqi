import sys
import logging
import app.message as message

log = logging.getLogger("io")


def send(msg):
    """
    Message ->

    Serializes the message and writes it to stdout

    """
    serial = msg.serialize()
    sys.stdout.write(serial)
    sys.stdout.flush()
    log.debug("sent: " + serial)


def receive():
    """
    -> Message

    Receive a message from stdin and deserializes it
    """
    packet = sys.stdin.readline()
    log.debug("received: " + packet)
    msg = message.deserialize(packet)
    return msg
