import json
class ApcategoryRequest:
    id = None
    code = None
    no = None
    name = None
    glno = None
    isasset = None
    def __init__(self, categeory_obj):
        if 'id' in categeory_obj:
            self.id = categeory_obj['id']
        if 'code' in categeory_obj:
            self.code = categeory_obj['code']
        if 'no' in categeory_obj:
            self.no = categeory_obj['no']
        if 'name' in categeory_obj:
            self.name = categeory_obj['name']
        if 'glno' in categeory_obj:
            self.glno = categeory_obj['glno']
        if 'isasset' in categeory_obj:
            self.isasset = categeory_obj['isasset']
    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
    def set_id(self, id):
        self.id = id
    def set_code(self, code):
        self.code = code
    def set_no(self, no):
        self.no = no
    def set_name(self, name):
        self.name = name
    def set_glno(self, glno):
        self.glno = glno
    def set_isasset(self, isasset):
        self.isasset = isasset
    def get_id(self):
        return self.id
    def get_code(self):
        return self.code
    def get_name(self):
        return self.name
    def get_glno(self):
        return self.glno
    def get_isasset(self):
        return self.isasset
    def get_no(self):
        return self.no