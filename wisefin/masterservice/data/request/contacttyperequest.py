import json


class ContactTypeRequest:
    id = None
    code = None
    name = None
    remarks = None

    def __init__(self, contacttype_obj):
        if 'id' in contacttype_obj:
            self.id = contacttype_obj['id']
        if 'code' in contacttype_obj:
            self.code = contacttype_obj['code']
        if 'name' in contacttype_obj:
            self.name = contacttype_obj['name']
        if 'remarks' in contacttype_obj:
            self.remarks = contacttype_obj['remarks']

    def get_id(self):
        return self.id

    def get_code(self):
        return self.code

    def get_name(self):
        return self.name

    def get_remarks(self):
        return self.remarks


