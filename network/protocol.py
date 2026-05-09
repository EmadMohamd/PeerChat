import json

def create_packet(sender, recipient, message):

    packet = {
        "sender": sender,
        "recipient": recipient,
        "message": message
    }

    return json.dumps(packet).encode()

def parse_packet(data):

    return json.loads(data.decode())


def create_packet(packet_type, data):

    packet = {
        "type": packet_type,
        "data": data
    }

    return json.dumps(packet).encode()

def parse_packet(raw):

    return json.loads(raw.decode())