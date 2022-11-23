import json

class ProjectTypeRequest:
    id = None
    code = None
    name = None

    def __init__(self, data_obj):
        if 'id' in data_obj:
            self.id = data_obj['id']
        if 'code' in data_obj:
            self.code = data_obj['code']
        if 'name' in data_obj:
            self.name = data_obj['name']

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def get_id(self):
        return self.id
    def get_code(self):
        return self.code
    def get_name(self):
        return self.name
