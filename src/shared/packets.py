import json

#################
# Packet Styles:
#   - Command = c
#   - Meta = m
#   - Data = d
#   - Response = r
#################
class CommandPacket(object):
    _type = 'c'
    _overhead = 25          # Base overhead of packet with empty strings in variables
    data = None

    def __init__(self, data):
        self.data = data

    def serialize(self):
        res = {
            'type': self._type,
            'data': self.data or ''
            }
        return json.dumps(res).encode()


class MetadataPacket(object):
    _type = 'm'
    _overhead = 80          # Base overhead of packet with empty strings in variables
    file_uid = None
    file_name = None
    file_type = None
    client_id = None
    key = None              # Currently set to None since we do have security implemented 

    def __init__(self, file_uid, file_name, file_type, client_id):
        self.file_uid = file_uid
        self.file_name = file_name
        self.file_type = file_type
        self.client_id = client_id
        # Added file_uid and seq_num data to _overhead
        self._overhead = self._overhead + 4 + len(file_name) + len(client_id)

    def serialize(self):
        res = {
            'type': self._type,
            'file_uid': str(self.file_uid).zfill(4) or '',
            'file_name': self.file_name or '',
            'file_type': self.file_type or '',
            'client_id': self.client_id or ''
            }
        return json.dumps(res).encode()



class DataPacket(object):  
    _type = 'd' 
    _overhead = 56          # Base overhead of packet with empty strings in variables
    file_uid = None
    seq_num = None
    data = None

    def __init__(self, file_uid, seq_num, data):
        self.file_uid = file_uid
        self.seq_num = seq_num
        self.data = data 
        # Added file_uid and seq_num data to _overhead
        self._overhead = self._overhead + 4 + 4

    def serialize(self):
        res = {
            'type': self._type,
            'file_uid': str(self.file_uid).zfill(4) or '',
            'seq_num': str(self.seq_num).zfill(4) or '',
            'data': self.data or ''
            }
        return json.dumps(res).encode()

# TODO: Figure out Response Packet
class ResponsePacket(object):
    _type = 'r'

    def __init__(self):
        pass

def deserialize_packet(input_packet):
    attributes = json.loads(input_packet.decode())

    output = None
    packet_type = attributes['type'] 
    if packet_type == 'c':
        output = CommandPacket(attributes['data'])
    elif packet_type == 'm':
        output = MetadataPacket(int(attributes['file_uid']), attributes['file_name'], attributes['file_type'], int(attributes['client_id']))
    elif packet_type == 'd':
        output = DataPacket(attributes['file_uid'], int(attributes['seq_num']), attributes['data'])
    elif packet_type == 'r':
        pass
    else:
        print("Packet type ({}) not recoginzed.".format(attributes['type']))

    return output
    