import json

class CGUMasterRequest:
    id = None
    name = None
    code = None


    def __init__(self, cgumst_obj):
        if 'id' in cgumst_obj:
            self.id = cgumst_obj['id']

        if 'name' in cgumst_obj:
            self.name = cgumst_obj['name']

        if 'code' in cgumst_obj:
            self.code = cgumst_obj['code']

    def get_id(self):
        return self.id
    def get_name(self):
        return self.name
    def get_code(self):
        return self.code