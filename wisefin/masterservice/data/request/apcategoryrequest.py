import json
class ApcategoryRequest:
    id = None
    code = None
    no = None
    name = None
    glno = None
    isasset = None
    isodit = None
    status = None
    expense_id = None
    expense_code = None
    expense=None
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
        if 'isodit' in categeory_obj:
            self.isodit = categeory_obj['isodit']
        if 'status' in categeory_obj:
            self.status = categeory_obj['status']
        if 'expense_id' in categeory_obj:
            self.expense_id = categeory_obj['expense_id']
        if 'expense_code' in categeory_obj:
            self.expense_code = categeory_obj['expense_code']
        if 'expense' in categeory_obj:
            self.expense = categeory_obj['expense']

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
    def set_isodit(self, isodit):
        self.isodit = isodit
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
    def set_status(self, status):
        self.status = status
    def get_status(self):
        return self.status
    def get_isodit(self):
        return self.isodit
    def get_expense_id(self):
        return self.expense_id
    def get_expense(self):
        return self.expense

    def get_expense_code(self):
        return self.expense_code