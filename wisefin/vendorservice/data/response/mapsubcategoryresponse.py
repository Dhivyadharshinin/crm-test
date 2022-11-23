import json
class ApsubcategoryResponse:
    id = None
    code = None
    no = None
    name = None
    category = None
    expense = None
    glno = None
    gstblocked = None
    gstrcm = None
    created_by = None
    updated_by = None
    status = None
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
    def set_status(self, status):
        self.status = status
    def set_created_by(self, created_by):
        self.created_by = created_by

    def set_updated_by(self, updated_by):
        self.updated_by = updated_by

    def get_id(self):
        return self.id
    def get_code(self):
        return self.code

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

    def get_no(self):
        return self.no
    def get_status(self):
        return self.status
    def get_created_by(self):
        return self.created_by
    def get_updated_by(self):
        return self.updated_by