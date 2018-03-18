import json
import os
import binascii
from Crypto.Cipher import AES


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

    def serialize(self, enc_obj):
        res = {
            'type': self._type,
            'data': self.data or '',
            }
        payload = json.dumps(res)
        pad = '0' * (16 - (len(payload) % 16 ))
        payload_to_enc = (pad + payload).encode()
        return enc_obj.encrypt(payload_to_enc)

    def __repr__(self):
        res = "Packet is:\n\t"
        attrs = [
            'type = ' + self._type,
            'data = ' + str(self.data) or '',
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

    def __init__(self, file_uid, file_name, file_type, client_id):
        self.file_uid = file_uid
        self.file_name = file_name
        self.file_type = file_type
        self.client_id = client_id
        # Added file_uid and seq_num data to _overhead

    def serialize(self, enc_obj):
        res = {
            'type': self._type,
            'file_uid': str(self.file_uid).zfill(4) or '',
            'file_name': self.file_name or '',
            'file_type': self.file_type or '',
            'client_id': self.client_id or ''
            }
        payload = json.dumps(res)
        pad = '0' * (16 - (len(payload) % 16 ))
        payload_to_enc = (pad + payload).encode()
        return enc_obj.encrypt(payload_to_enc)


    def __repr__(self):
        res = "Packet is:"
        attrs = [
            'type = ' + self._type,
            'file_uid = ' + str(self.file_uid).zfill(4) or ''.zfill(4),
            'file_name = ' + self.file_name or '',
            'file_type = ' + self.file_type or '',
            'client_id = ' + str(self.client_id)or ''
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

    def serialize(self, enc_obj):
        res = {
            'type': self._type,
            'file_uid': str(self.file_uid).zfill(4) or ''.zfill(4),
            'seq_num': str(self.seq_num).zfill(4) or ''.zfill(4),
            'data': self.data.decode('utf8') or ''
            }
        payload = json.dumps(res)
        pad = '0' * (16 - (len(payload) % 16 ))
        payload_to_enc = (pad + payload).encode()
        return enc_obj.encrypt(payload_to_enc)

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

    def serialize(self, enc_obj):
        res = {
            'type': self._type,
            'file_uid': str(self.file_uid).zfill(4) or ''.zfill(4)
            }
        payload = json.dumps(res)
        pad = '0' * (16 - (len(payload) % 16 ))
        payload_to_enc = (pad + payload).encode()
        return enc_obj.encrypt(payload_to_enc)
    
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

    def serialize(self, enc_obj):
        res = {
            'type': self._type,
            'data': self.data or ''
            }
        payload = json.dumps(res)
        pad = '0' * (16 - (len(payload) % 16 ))
        payload_to_enc = (pad + payload).encode()
        print("LENGTH IS:", len(payload_to_enc))
        return enc_obj.encrypt(payload_to_enc)
    
    def __repr__(self):
        res = "Packet is:\n\t"
        attrs = [
            'type = ' + self._type,
            'data = ' + str(self.data) or ''
        ]
        res += '\n\t'.join(attrs)
        return res

class InitializerPacket(object):
    _type = 'i'
    sym_key = None
    client_id = None

    def __init__(self, sym_key=None, client_id=None):
        if sym_key is None:
            self.sym_key = binascii.hexlify(os.urandom(16))
        else:
            self.sym_key = sym_key
        self.client_id = client_id

    def serialize(self, public=False):
        from client_pkg.client import get_server_public_key
        res = {
            'type': self._type,
            'sym_key': self.sym_key.decode('utf8'),
            'client_id': self.client_id or ''
            }

        print("RES DICT IS:", res)
        # JSON Dump and pad it to 128
        payload = json.dumps(res).zfill(128).encode()

        if public:
            pub_key_obj = get_server_public_key()
            return pub_key_obj.encrypt(payload, 32)[0] 
        else:
            encryption = AES.new(self.sym_key, AES.MODE_ECB)
            return encryption.encrypt(payload)
    
    def __repr__(self):
        res = "Packet is:\n\t"
        attrs = [
            'type = ' + self._type,
            'sym_key = ' + str(self.sym_key) or '',
            'client_id = ' + str(self.client_id) or ''
        ]
        res += '\n\t'.join(attrs)
        return res


def deserialize_init_packet(init_packet, public=False, sym_key=None):
    from server_pkg.server import get_server_private_key
    decrypted_packet = None
    # Print statements are here to showcase each step of the packet conversion
    print("ENCRYPTED PACKET IS:", init_packet)
    if public:
        private_key_obj = get_server_private_key()
        decrypted_packet = private_key_obj.decrypt(init_packet)
    else:
        encryption = AES.new(sym_key, AES.MODE_ECB)
        decrypted_packet = encryption.decrypt(init_packet)
    print("DECODED PACKET IS:", decrypted_packet.decode())
    decrypted_packet_cleaned = decrypted_packet.decode().lstrip('0')
    print("CLEANED UP PACKET IS:", decrypted_packet_cleaned)

    attributes = json.loads(decrypted_packet_cleaned)
    assert attributes['type'] == 'i', ("[ERROR] Excepted Initilizaton Packet, got: TYPE - {}".format(attributes['type']))

    output = InitializerPacket(attributes['sym_key'].encode('utf8'), attributes['client_id'])
    print("BUILT PACK IS:", output)
    return output

def deserialize_packet(input_packet, enc_obj):
    print("ENCRYPT PACK IS:", input_packet)

    payload = enc_obj.decrypt(input_packet).decode().lstrip('0')
    attributes = json.loads(payload)

    print("DECRYPT ATTR ARE:", attributes)

    output = None
    packet_type = attributes['type'] 
    if packet_type == 'c':
        output = CommandPacket(attributes['data'])
    elif packet_type == 'm':
        output = MetadataPacket(int(attributes['file_uid']), attributes['file_name'], attributes['file_type'], int(attributes['client_id']))
    elif packet_type == 'd':
        output = DataPacket(int(attributes['file_uid']), int(attributes['seq_num']), attributes['data'].encode('utf8'))
    elif packet_type == 'r':
        output = ResponsePacket(attributes['data'])
    elif packet_type == 'e':
        output = EndOfDataPacket(int(attributes['file_uid']))
    else:
        print("Packet type ({}) not recoginzed.".format(attributes['type']))

    return output
    