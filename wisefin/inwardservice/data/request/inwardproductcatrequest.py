import json

class ProductcategoryRequest:
    id = None
    code = None
    name = None
    remarks = None
    is_sys = False

    def __init__(self, productcat_obj):
        if 'id' in productcat_obj:
            self.id = productcat_obj['id']
        if 'code' in productcat_obj:
            self.code = productcat_obj['code']
        if 'name' in productcat_obj:
            self.name = productcat_obj['name']
        if 'remarks' in productcat_obj:
            self.remarks = productcat_obj['remarks']
        if 'is_sys' in productcat_obj:
            self.is_sys = productcat_obj['is_sys']


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
    def set_id(self, id):
        self.id = id

    def set_code(self, code):
        self.code = code

    def set_name(self, name):
        self.name = name

    def set_remarks(self, remarks):
        self.remarks = remarks

    def set_is_sys(self, is_sys):
        self.is_sys = is_sys

    def get_id(self):
        return self.id
    def get_code(self):
        return self.code
    def get_name(self):
        return self.name

    def get_remarks(self):
        return self.remarks
    def get_is_sys(self):
        return self.is_sys




