import json


class UomRequest:
    id = None
    code = None
    name = None
    status = 1

    def __init__(self, uom_obj):
        if 'id' in uom_obj:
            self.id = uom_obj['id']
        if 'code' in uom_obj:
            self.code = uom_obj['code']
        if 'name' in uom_obj:
            self.name = uom_obj['name']
        if 'status' in uom_obj:
            self.status = uom_obj['status']

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def get_id(self):
        return self.id

    def get_code(self):
        return self.code

    def get_name(self):
        return self.name

    def get_status(self):
        return self.status


