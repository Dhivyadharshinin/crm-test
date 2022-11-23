import json

class DistrictRequest:
    id = None
    code = None
    name = None
    state_id = None
    state_code = None
    status = None

    def __init__(self, district_obj):
        if 'id' in district_obj:
            self.id = district_obj['id']
        if 'code' in district_obj:
            self.code = district_obj['code']
        if 'name' in district_obj:
            self.name = district_obj['name']
        if 'state_id' in district_obj:
            self.state_id = district_obj['state_id']
        if 'state_code' in district_obj:
            self.state_code = district_obj['state_code']
        if 'status' in district_obj:
            self.status = district_obj['status']



    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_code(self, code):
        self.code = code

    def set_name(self, name):
        self.name = name
    def set_state_id(self, state_id):
        self.state_id = state_id

    def get_id(self):
        return self.id

    def get_code(self):
        return self.code

    def get_name(self):
        return self.name

    def get_state_id(self):
        return self.state_id

    def get_state_code(self):
        return self.state_code

    def get_status(self):
        return self.status
