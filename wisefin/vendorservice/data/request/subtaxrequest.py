import json


class SubTaxRequest:
    id = None
    tax_id = None
    code = None
    name = None
    remarks = None
    glno = None

    def __init__(self, subtax_obj):
        if 'id' in subtax_obj:
            self.id = subtax_obj['id']
        if 'tax_id' in subtax_obj:
            self.tax_id = subtax_obj['tax_id']
        if 'code' in subtax_obj:
            self.code = subtax_obj['code']
        if 'name' in subtax_obj:
            self.name = subtax_obj['name']
        if 'remarks' in subtax_obj:
            self.remarks = subtax_obj['remarks']
        if 'glno' in subtax_obj:
            self.glno = subtax_obj['glno']
    def get_id(self):
        return self.id

    def get_code(self):
        return self.code

    def get_name(self):
        return self.name

    def get_tax_id(self):
        return self.tax_id

    def get_remarks(self):
        return self.remarks

    def get_glno(self):
        return self.glno

