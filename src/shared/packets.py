import json

#################
# Packet Styles:
#   - Command = c
#   - Meta = m
#   - Data = d
#   - Response = r
#   - End Of Data = e
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

    def __repr__(self):
        res = "Packet is:\n\t"
        attrs = [
            'type = ' + self._type,
            'data = ' + str(self.data) or ''
        ]
        res += '\n\t'.join(attrs)
        return res


class MetadataPacket(object):
    _type = 'm'
    _overhead = 84          # Base overhead of packet with empty strings in variables
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

    def serialize(self):
        res = {
            'type': self._type,
            'file_uid': str(self.file_uid).zfill(4) or '',
            'file_name': self.file_name or '',
            'file_type': self.file_type or '',
            'client_id': self.client_id or ''
            }
        return json.dumps(res).encode()

    def __repr__(self):
        res = "Packet is:"
        attrs = [
            'type = ' + self._type,
            'file_uid = ' + str(self.file_uid).zfill(4) or ''.zfill(4),
            'file_name = ' + self.file_name or '',
            'file_type = ' + self.file_type or '',
            'client_id = ' + self.client_id or ''
        ]
        res += '\n\t'.join(attrs)
        return res


class DataPacket(object):  
    _type = 'd' 
    _overhead = 64          # Base overhead of packet with empty strings in variables
    file_uid = None
    seq_num = None
    data = None

    def __init__(self, file_uid, seq_num, data):
        self.file_uid = file_uid
        self.seq_num = seq_num
        self.data = data 
        # Added file_uid and seq_num data to _overhead

    def serialize(self):
        res = {
            'type': self._type,
            'file_uid': str(self.file_uid).zfill(4) or ''.zfill(4),
            'seq_num': str(self.seq_num).zfill(4) or ''.zfill(4),
            'data': self.data.decode('utf8') or ''
            }
        return json.dumps(res).encode()

    def __repr__(self):
        res = "Packet is:\n\t"
        attrs = [
            'type = ' + self._type,
            'file_uid = ' + str(self.file_uid).zfill(4) or '',
            'seq_num = ' + str(self.seq_num).zfill(4) or '',
            'data = ' + self.data or ''
        ]
        res += '\n\t'.join(attrs)
        return res


class EndOfDataPacket(object):
    _type = 'e'
    _overhead = 33
    file_uid = None

    def __init__(self, file_uid):
        self.file_uid = file_uid

    def serialize(self):
        res = {
            'type': self._type,
            'file_uid': str(self.file_uid).zfill(4) or ''.zfill(4)
            }
        return json.dumps(res).encode()
    
    def __repr__(self):
        res = "Packet is:\n\t"
        attrs = [
            'type = ' + self._type,
            'file_uid = ' + str(self.file_uid).zfill(4) or ''
        ]
        res += '\n\t'.join(attrs)
        return res

class ResponsePacket(object):
    _type = 'r'
    _overhead = 25
    data = None

    def __init__(self, data):
        self.data = data

    def serialize(self):
        res = {
            'type': self._type,
            'data': self.data or ''
            }
        return json.dumps(res).encode()
    
    def __repr__(self):
        res = "Packet is:\n\t"
        attrs = [
            'type = ' + self._type,
            'data = ' + str(self.data) or ''
        ]
        res += '\n\t'.join(attrs)
        return res


def deserialize_packet(input_packet):
    attributes = json.loads(input_packet.decode())

    output = None
    packet_type = attributes['type'] 
    if packet_type == 'c':
        output = CommandPacket(attributes['data'])
    elif packet_type == 'm':
        output = MetadataPacket(int(attributes['file_uid']), attributes['file_name'], attributes['file_type'], int(attributes['client_id']))
    elif packet_type == 'd':
        output = DataPacket(attributes['file_uid'], int(attributes['seq_num']), attributes['data'].encode('utf8'))
    elif packet_type == 'r':
        output = ResponsePacket(attributes['data'])
    elif packet_type == 'e':
        output = EndOfDataPacket(attributes['file_uid'])
    else:
        print("Packet type ({}) not recoginzed.".format(attributes['type']))

    return output
    