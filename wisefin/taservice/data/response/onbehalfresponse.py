import json
from taservice.util.ta_util import Status
class Onbehalfresponse:
    id = 1
    employeegid = None
    branchgid = None
    onbehalf_employeegid = None
    status = Status.REQUESTED
    data =[]
    onbehalf_employee_name=None
    employee_name=None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_employeegid(self, employeegid):
        self.employeegid = employeegid

    def set_branchgid(self, branchgid):
        self.branchgid = branchgid

    def set_employee(self, employee):
        self.employee = employee

    def set_branch(self, branch):
        self.branch = branch
    def set_branch_name(self, branch_name):
        self.branch_name = branch_name
    def set_branch_code(self, branch_code):
        self.branch_code = branch_code
    def set_branch_id(self, branch_id):
        self.branch_id = branch_id
    def set_full_name(self, full_name):
        self.full_name = full_name

    def set_onbehalf_employeegid(self, onbehalf_employeegid):
        self.onbehalf_employeegid = onbehalf_employeegid
    def set_onbehalf_employee(self, onbehalf_employee):
        self.onbehalf_employee = onbehalf_employee

    def set_status(self, status):
        self.status = status
    def set_onb_header_id(self, onb_header_id):
        self.onb_header_id = onb_header_id
    def set_onb_present_status(self, onb_present_status):
        self.onb_present_status = onb_present_status
    def set_ta_onb_status(self, ta_onb_status):
        self.ta_onb_status = ta_onb_status

    def set_data(self,data):
        self.data = data
    def set_employee_name(self,employee_name):
        self.employee_name=employee_name
    def set_code(self,code):
        self.code=code
    def set_employee_data(self,employee_data):
        self.employee_data=employee_data
    def set_employee_code(self,employee_code):
        self.employee_code=employee_code
    def set_onbehalf_employee_name(self,onbehalf_employee_name):
        self.onbehalf_employee_name=onbehalf_employee_name
    def set_onbehalf_employee_data(self,onbehalf_employee_data):
        self.onbehalf_employee_data=onbehalf_employee_data

class Ccbs_resp:
    id= None
    tour= None
    requestid= None
    ccid= None
    bsid=None
    status=None
    ccbs_type=None
    amount=None
    percentage=None

    def set_id(self,id):
        self.id=id
    def set_tour(self,tour):
        self.tour=tour
    def set_tourgid(self,tourgid):
        self.tourgid=tourgid
    def set_requestid(self,requestid):
        self.requestid=requestid
    def set_ccid(self,ccid):
        self.ccid=ccid
    def set_bsid(self,bsid):
        self.bsid=bsid
    def set_status(self,status):
        self.status=status
    def set_ccbs_edit_status(self,ccbs_edit_status):
        self.ccbs_edit_status=ccbs_edit_status
    def set_ccbs_type(self,ccbs_type):
        self.ccbs_type=ccbs_type
    def set_amount(self,amount):
        self.amount=amount
    def set_percentage(self,percentage):
        self.percentage=percentage
    def set_cc_data(self,cc_data):
        self.cc_data=cc_data
    def set_bs_data(self,bs_data):
        self.bs_data=bs_data

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)