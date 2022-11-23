import json
class Approveresponse:
    id = 1
    employeeid = None
    branchid = None
    tourapprove = None
    advanceapprove = None
    expenseapprove = None
    status = 1
    data =[]
    employee_name=None
    employee_code=None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_employeeid(self, employeeid):
        self.employeeid = employeeid
    def set_employee_name(self, employee_name):
        self.employee_name = employee_name
    def set_employee_code(self, employee_code):
        self.employee_code = employee_code

    def set_branchid(self, branchid):
        self.branchid = branchid
    def set_branch_name(self,branch_name):
        self.branch_name=branch_name
    def set_branch_code(self,branch_code):
        self.branch_code=branch_code

    def set_tourapprove(self, tourapprove):
        self.tourapprove = tourapprove

    def set_advanceapprove(self, advanceapprove):
        self.advanceapprove = advanceapprove

    def set_status(self, status):
        self.status = status

    def set_expenseapprove(self, expenseapprove):
        self.expenseapprove = expenseapprove

    def set_data(self,data):
        self.data = data


