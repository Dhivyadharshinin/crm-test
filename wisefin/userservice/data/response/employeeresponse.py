import json


class EmployeeResponse:
    id = None
    first_name = None
    middle_name = None
    last_name = None
    full_name = None
    code = None
    department = None
    grade = None
    designation = None
    user_id = None
    email_id = None
    mobile_number = None
    dob = None
    doj = None
    gender = None
    phone_no = None
    employee_type = None
    supervisor = None
    hierarchy = None
    branch = None
    costcentre = None
    businesssegment = None
    srlno = None
    accountnumber = None
    grade1 = None
    grade1_date = None
    grade2 = None
    grade2_date = None
    noticeperiod = None
    role = None
    department_id =None
    employee_branch_id = None
    limit = None
    employee_name = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_mobilenumber(self, mobile_number):
        self.mobile_number = mobile_number

    def set_first_name(self, first_name):
        self.first_name = first_name
    def set_employee_name(self, employee_name):
        self.employee_name = employee_name

    def set_middle_name(self, middle_name):
        self.middle_name = middle_name

    def set_last_name(self, last_name):
        self.last_name = last_name

    def set_full_name(self, full_name):
        self.full_name = full_name

    def set_email_id(self, email_id):
        self.email_id = email_id

    def set_code(self, code):
        self.code = code

    def set_department(self, department):
        self.department = department

    def set_designation(self, designation):
        self.designation = designation

    def set_grade(self, grade):
        self.grade = grade

    def set_user(self, user):
        self.user = user

    def set_gender(self, gender):
        self.gender = gender

    def set_branch_gst(self, branch_gst):
        self.branch_gst = branch_gst

    def set_phone_no(self, phone_no):
        self.phone_no = phone_no

    def set_employee_type(self, employee_type):
        self.employee_type = employee_type

    def set_supervisor(self, supervisor):
        self.supervisor = supervisor

    def set_hierarchy(self, hierarchy):
        self.hierarchy = hierarchy

    def set_branch(self, branch):
        self.branch = branch

    def set_costcentre(self, costcentre):
        self.costcentre = costcentre

    def set_businesssegment(self, businesssegment):
        self.businesssegment = businesssegment

    def set_address_id(self, address_id):
        self.address_id = address_id

    def set_contact_id(self, contact_id):
        self.contact_id = contact_id

    def set_dob(self, dob):
        dob = str(dob)
        self.dob = dob

    def set_doj(self, doj):
        doj = str(doj)
        self.doj = doj

    def set_accountnumber(self, accountnumber):
        self.accountnumber = accountnumber

    def set_grade1(self, grade1):
        self.grade1 = grade1

    def set_grade1_date(self, grade1_date):
        grade1_date = str(grade1_date)
        self.grade1_date = grade1_date

    def set_grade2(self, grade2):
        self.grade2 = grade2

    def set_grade2_date(self, grade2_date):
        grade2_date = str(grade2_date)
        self.grade2_date = grade2_date

    def set_noticeperiod(self, noticeperiod):
        self.noticeperiod = noticeperiod

    def set_role(self, role):
        self.role = role

    def set_department_id(self, department_id):
        self.department_id = department_id

    def set_employee_branch_id(self, employee_branch_id):
        self.employee_branch_id = employee_branch_id
    def set_employee_branch_name(self, employee_branch_name):
        self.employee_branch_name = employee_branch_name
    def set_team(self, team):
        self.team = team
    def set_sub_team(self, sub_team):
        self.sub_team = sub_team

    def set_limit(self, limit):
        self.limit = limit


    def get_id(self):
        return self.id

    def get_first_name(self):
        return self.first_name

    def get_middle_name(self):
        return self.middle_name

    def get_last_name(self):
        return self.last_name

    def get_full_name(self):
        return self.full_name

    def get_code(self):
        return self.code

    def get_department(self):
        return self.department

    def get_grade(self):
        return self.grade

    def get_designation(self):
        return self.designation

    def get_user(self):
        return self.user

    def get_accountnumber(self):
        return self.accountnumber

    def get_grade1(self):
        return self.grade1

    def get_grade1_date(self):
        return self.grade1_date

    def get_grade2(self):
        return self.grade2

    def get_grade2_date(self):
        return self.grade2_date

    def get_noticeperiod(self):
        return self.noticeperiod

    def get_role(self):
        return self.role

    def get_role(self):
        return self.srlno

class EmployeeRoleResponse :
    role_id = None
    role = None
    empolyee_id = None

    def set_role_id(self, role_id):
        self.role_id = role_id

    def set_role(self, role):
        self.role = role

    def set_employee_id(self, employee_id):
        self.employee_id = employee_id
class EmployeeMobieResponse :
    id = None
    code = None
    mobile_number = None

    def set_mobile_number(self, mobile_number):
        self.mobile_number = mobile_number

    def set_id(self, id):
        self.id = id

    def set_code(self, code):
        self.code = code

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

class EmployeeLogResponse :
    id = None
    maindata = None
    range_to = None
    range_from = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id


    def set_maindata(self, maindata):
        self.maindata = maindata
    def set_range_from(self, range_from):
        self.range_from = range_from
    def set_range_to(self, range_to):
        self.range_to = range_to
class empdepartmentres:
    id=None
    code=None
    name=None
    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)
    def set_id(self,id):
        self.id=id
    def set_code(self,code):
        self.code=code
    def set_name(self,name):
        self.name=name


# TA Dependents api call
class Employee_data_resp:
    id= None
    employeeid= None
    branchid= None
    employee_name=None
    employee_code=None
    employee_designation=None
    bankgstno=None
    bank_name=None

    def set_id(self,id):
        self.id=id
    def set_approver(self,approver):
        self.approver=approver
    def set_employeeid(self,employeeid):
        self.employeeid=employeeid
    def set_employee_branch_id(self,employee_branch_id):
        self.employee_branch_id=employee_branch_id
    def set_name(self,name):
        self.name=name
    def set_code(self,code):
        self.code=code
    def set_grade(self,grade):
        self.grade=grade
    def set_designation(self,designation):
        self.designation=designation
    def set_bankgstno(self,bankgstno):
        self.bankgstno=bankgstno
    def set_bank_name(self,bank_name):
        self.bank_name=bank_name


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)



