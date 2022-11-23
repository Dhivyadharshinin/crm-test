import json

class PaymodeRequest:
    id = None
    code = None
    name = None

    def __init__(self, paymode_obj):
        if 'id' in paymode_obj:
            self.id = paymode_obj['id']
        if 'code' in paymode_obj:
            self.code = paymode_obj['code']
        if 'name' in paymode_obj:
            self.name = paymode_obj['name']


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
