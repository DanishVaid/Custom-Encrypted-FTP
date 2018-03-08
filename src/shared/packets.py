import json

#################
# Packet Styles:
#   - Command = c
#   - Meta = m
#   - Data = d
#################
class Command_Packet(object):
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


class Meta_Packet(object):
    _type = 'm'
    _overhead = 9999    # Modify to figure out overhead


class Data_Packet(object):  
    _type = 'd' 
    _overhead = 9999    # Modify to figure out overhead 


def deserialize_packet(inp_pack):
    decoded_pack = inp_pack.decode()
    attr_dict = json.loads(decoded_pack)
    ret_pack = None
    this_type = attr_dict['type'] 
    if this_type == 'c':
        ret_pack = Command_Packet(attr_dict['data'])
    elif this_type == 'm':
        pass
    elif this_type == 'd':
        pass
    else:
        print("Packet type ({}) not recoginzed.".format(attr_dict['type']))

    return ret_pack
    