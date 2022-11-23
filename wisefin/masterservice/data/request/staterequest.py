import json

class StateRequest:
    id = None
    code = None
    name = None
    country_id = None

    def __init__(self, state_obj):
        if 'id' in state_obj:
            self.id = state_obj['id']
        if 'code' in state_obj:
            self.code = state_obj['code']
        if 'name' in state_obj:
            self.name = state_obj['name']
        if 'country_id' in state_obj:
            self.country_id = state_obj['country_id']



    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_code(self, code):
        self.code = code

    def set_name(self, name):
        self.name = name

    def set_country_id(self, country_id):
        self.country_id = country_id

    def get_id(self):
        return self.id

    def get_code(self):
        return self.code

    def get_name(self):
        return self.name

    def get_country_id(self):
        return self.country_id
