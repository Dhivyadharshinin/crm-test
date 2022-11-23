import json

from masterservice.data.response.expenseresponse import ExpenseResponse
class ApcategoryResponse:
    id = None
    code = None
    no = None
    name = None
    glno = None
    isasset = None
    expense = None
    isodit = None
    created_by = None
    updated_by = None
    status = None
    expense_id = None
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
    def set_status(self, status):
        self.status = status
    def set_created_by(self, created_by):
        self.created_by = created_by
    def set_updated_by(self, updated_by):
        self.updated_by = updated_by
    def set_expense_id(self,expense_id):
        self.expense_id=expense_id

    def set_expense(self, expense):
        if expense is not None:
            expense_data = ExpenseResponse()
            expense_data.set_id(expense.id)
            expense_data.set_head(expense.head)
            expense_data.set_linedesc(expense.linedesc)
            expense_data.set_group(expense.group)
            expense_data.set_sch16(expense.sch16)
            expense_data.set_sch16desc(expense.sch16desc)
            self.expense = expense_data
        else:
            self.expense_id = expense

    # def set_expense_id(self, expense_id):
    #     self.expense_id = expense_id

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
    def get_isodit(self):
        return self.isodit
    def get_no(self):
        return self.no
    def get_status(self):
        return self.status
    def get_created_by(self):
        return self.created_by
    def get_updated_by(self):
        return self.updated_by
    def get_expense_id(self):
        return self.expense_id


