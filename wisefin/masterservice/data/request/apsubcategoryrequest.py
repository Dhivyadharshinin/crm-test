import json
class ApsubcategoryRequest:
    id = None
    code = None
    no = None
    name = None
    category_id = None
    category_code = None
    expense_id = None
    expense_code = None
    glno = None
    gstblocked = None
    gstrcm = None
    status = None
    assetcode = None
    head = None

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
        if 'expense_id' in subcategeory_obj:
            self.expense_id = subcategeory_obj['expense_id']
        if 'gstblocked' in subcategeory_obj:
            self.gstblocked = subcategeory_obj['gstblocked']
        if 'gstrcm' in subcategeory_obj:
            self.gstrcm = subcategeory_obj['gstrcm']
        if 'glno' in subcategeory_obj:
            self.glno = subcategeory_obj['glno']
        if 'status' in subcategeory_obj:
            self.status = subcategeory_obj['status']
        if 'assetcode' in subcategeory_obj:
            self.assetcode = subcategeory_obj['assetcode']
        if 'category_code' in subcategeory_obj:
            self.category_code = subcategeory_obj['category_code']
        if 'head' in subcategeory_obj:
            self.head = subcategeory_obj['head']
        if 'expense_code' in subcategeory_obj:
            self.expense_code = subcategeory_obj['expense_code']

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
    def set_expense_id(self, expense_id):
        self.expense_id = expense_id
    def set_gstblocked(self, gstblocked):
        self.gstblocked = gstblocked
    def set_gstrcm(self, gstrcm):
        self.gstrcm = gstrcm
    def set_status(self, status):
        self.status = status
    def set_assetcode(self, assetcode):
        self.assetcode = assetcode

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
    def get_expense_id(self):
        return self.expense_id
    def get_gstblocked(self):
        return self.gstblocked
    def get_gstrcm(self):
        return self.gstrcm
    def get_status(self):
        return self.status
    def get_assetcode(self):
        return self.assetcode

    def get_category_code(self):
        return self.category_code

    def get_head(self):
        return self.head

    def get_expense_code(self):
        return self.expense_code
