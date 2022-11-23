import json
class Branch_emp_resp:
    id= None
    employeeid= None
    branchid= None
    tourapprove= None
    advanceapprove=None
    expenseapprove=None
    status=None
    code=None
    first_name=None
    middle_name= None
    last_name= None
    full_name=None
    employee_name=None
    employee_code=None

    def set_id(self,id):
        self.id=id
    def set_employeeid(self,employeeid):
        self.employeeid=employeeid
    def set_designation(self,designation):
        self.designation=designation
    def set_branchid(self,branchid):
        self.branchid=branchid
    def set_tourapprove(self,tourapprove):
        self.tourapprove=tourapprove
    def set_advanceapprove(self,advanceapprove):
        self.advanceapprove=advanceapprove
    def set_expenseapprove(self,expenseapprove):
        self.expenseapprove=expenseapprove
    def set_status(self,status):
        self.status=status
    def set_code(self,code):
        self.code=code
    def set_first_name(self,first_name):
        self.first_name=first_name
    def set_middle_name(self,middle_name):
        self.middle_name=middle_name
    def set_last_name(self,last_name):
        self.last_name=last_name
    def set_full_name(self,full_name):
        self.full_name=full_name
    def set_employee_branch_id(self,employee_branch_id):
        self.employee_branch_id=employee_branch_id
    def set_header_id(self,header_id):
        self.header_id=header_id
    def set_employee_name(self,employee_name):
        self.employee_name=employee_name
    def set_employee_code(self,employee_code):
        self.employee_code=employee_code
    def set_employee_designation(self,employee_designation):
        self.employee_designation=employee_designation


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)

