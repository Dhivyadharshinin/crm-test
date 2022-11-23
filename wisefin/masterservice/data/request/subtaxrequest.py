import json


class SubTaxRequest:
    id = None
    tax_id = None
    tax_code = None
    code = None
    name = None
    remarks = None
    category_id=None
    subcategory_id=None
    subtaxamount=None
    glno = None
    status = None

    def __init__(self, subtax_obj):
        if 'id' in subtax_obj:
            self.id = subtax_obj['id']
        if 'tax_id' in subtax_obj:
            self.tax_id = subtax_obj['tax_id']
        if 'tax_code' in subtax_obj:
            self.tax_code = subtax_obj['tax_code']
        if 'code' in subtax_obj:
            self.code = subtax_obj['code']
        if 'name' in subtax_obj:
            self.name = subtax_obj['name']
        if 'subtaxamount' in subtax_obj:
            self.subtaxamount=subtax_obj['subtaxamount']
        if 'remarks' in subtax_obj:
            self.remarks = subtax_obj['remarks']
        if 'category_id'in subtax_obj:
            self.category_id=subtax_obj['category_id']
        if 'subcategory_id'in subtax_obj:
            self.subcategory_id=subtax_obj['subcategory_id']
        if 'glno' in subtax_obj:
            self.glno = subtax_obj['glno']
        if 'status' in subtax_obj:
            self.status = subtax_obj['status']


    def get_id(self):
        return self.id

    def get_code(self):
        return self.code

    def get_name(self):
        return self.name

    def get_tax_id(self):
        return self.tax_id

    def get_subtaxamount(self):
        return self.subtaxamount

    def get_remarks(self):
        return self.remarks

    def get_category_id(self):
        return self.category_id

    def get_subcategory_id(self):
        return self.subcategory_id

    def get_glno(self):
        return self.glno

    def get_taxcode(self):
        return self.tax_code

    def get_status(self):
        return self.status

