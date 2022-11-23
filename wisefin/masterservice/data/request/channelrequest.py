import json

class ChannelRequest:
    id = None
    code = None
    name = None

    def __init__(self, channel_obj):
        if 'id' in channel_obj:
            self.id = channel_obj['id']
        if 'code' in channel_obj:
            self.code = channel_obj['code']
        if 'name' in channel_obj:
            self.name = channel_obj['name']


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_code(self, code):
        self.code = code

    def set_name(self, name):
        self.name = name


    def get_id(self):
        return self.id

    def get_code(self):
        return self.code

    def get_name(self):
        return self.name
