import json

#################
# Packet Styles:
#   - Command = c
#   - Meta = m
#   - Data = d
#################
class CommandPacket(object):
    _type = 'c'
    data = None

    def __init__(self, data):
        self.data = data

    def serialize(self):
        res = {
            'type': self._type,
            'data': self.data
            }
        return json.dumps(res).encode()


class MetadataPacket(object):
    _type = 'm'
    _overhead = 9999    # Modify to figure out overhead


class DataPacket(object):  
    _type = 'd' 
    _overhead = 9999    # Modify to figure out overhead 


class ResponsePacket(object):
    _type = 'r'
    data = None

    def __init__(self, data):
        self.data = data

def deserialize_packet(input_packet):
    attributes = json.loads(input_packet.decode())

    output = None
    packet_type = attributes['type'] 
    if packet_type == 'c':
        output = CommandPacket(attributes['data'])
    elif packet_type == 'm':
        pass
    elif packet_type == 'd':
        pass
    else:
        print("Packet type ({}) not recoginzed.".format(attributes['type']))

    return output
    