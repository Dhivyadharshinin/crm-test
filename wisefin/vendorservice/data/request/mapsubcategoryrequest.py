import json
class ApsubcategoryRequest:
    id = None
    code = None
    no = None
    name = None
    category = None
    expense = None
    glno = None
    gstblocked = None
    gstrcm = None
    def __init__(self,subcategeory_obj):
        if 'id' in subcategeory_obj:
            self.id = subcategeory_obj['id']
        if 'code' in subcategeory_obj:
            self.code = subcategeory_obj['code']
        if 'no' in subcategeory_obj:
            self.no = subcategeory_obj['no']
        if 'name' in subcategeory_obj:
            self.name = subcategeory_obj['name']
        if 'category_id' in subcategeory_obj:
            self.category_id = subcategeory_obj['category_id']
        if 'expense' in subcategeory_obj:
            self.expense = subcategeory_obj['expense']
        if 'gstblocked' in subcategeory_obj:
            self.gstblocked = subcategeory_obj['gstblocked']
        if 'gstrcm' in subcategeory_obj:
            self.gstrcm = subcategeory_obj['gstrcm']
        if 'glno' in subcategeory_obj:
            self.glno = subcategeory_obj['glno']
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

    def set_category_id(self, category_id):
        self.category_id = category_id

    def set_expense(self, expense):
        self.expense = expense

    def set_gstblocked(self, gstblocked):
        self.gstblocked = gstblocked

    def set_gstrcm(self, gstrcm):
        self.gstrcm = gstrcm

    def get_id(self):
        return self.id
    def get_code(self):
        return self.code
    def get_no(self):
        return self.no
    def get_name(self):
        return self.name
    def get_glno(self):
        return self.glno
    def get_category_id(self):
        return self.category_id
    def get_expense(self):
        return self.expense
    def get_gstblocked(self):
        return self.gstblocked

    def get_gstrcm(self):
        return self.gstrcm
