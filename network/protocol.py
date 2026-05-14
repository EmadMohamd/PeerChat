import json

def create_packet(packet_type, data):
    packet = {
        "type": packet_type,
        "data": data
    }
    return (json.dumps(packet) + "\n").encode()

def parse_packet(raw_line):
    return json.loads(raw_line.decode())