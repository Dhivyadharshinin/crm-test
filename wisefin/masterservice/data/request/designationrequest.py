import json


class DesignationRequest:
    id = None
    code = None
    name = None
    status = None

    def __init__(self, designation_obj):
        if 'id' in designation_obj:
            self.id = designation_obj['id']
        if 'code' in designation_obj:
            self.code = designation_obj['code']
        if 'name' in designation_obj:
            self.name = designation_obj['name']

        if 'status' in designation_obj:
            self.status = designation_obj['status']


    def get_id(self):
        return self.id

    def get_code(self):
        return self.code

    def get_name(self):
        return self.name

    def get_status(self):
        return self.status


