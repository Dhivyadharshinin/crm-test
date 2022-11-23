import json


class EmployeeSynchResponse:
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
    Message=None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_mobilenumber(self, mobile_number):
        self.mobile_number = mobile_number

    def set_first_name(self, first_name):
        self.first_name = first_name

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
    def set_Message(self, Message):
        self.Message = Message

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

class AddressSynchResponse:
    id = None
    line1 = None
    line2 = None
    line3 = None
    pincode_id = None
    city_id = None
    district_id = None
    state_id = None

    def get(self):
      return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_line1(self, line1):
        self.line1 = line1

    def set_line2(self, line2):
        self.line2 = line2

    def set_line3(self, line3):
        self.line3 = line3

    def set_pincode_id(self, pincode_id):
        self.pincode_id = pincode_id

    def set_city_id(self, city_id):
        self.city_id = city_id

    def set_district_id(self, district_id):
        self.district_id = district_id

    def set_state_id(self, state_id):
        self.state_id = state_id

    def get_id(self):
        return self.id

    def get_line1(self):
        return self.line1

    def get_line2(self):
        return self.line2

    def get_line3(self):
        return self.line3

    def get_pincode_id(self):
        return self.pincode_id

    def get_city_id(self):
        return self.city_id

    def get_district_id(self):
        return self.district_id

    def get_state_id(self):
        return self.state_id

class ContactSynchResponse:
    id = None
    type_id = None
    name = None
    designation_id = None
    landline = None
    landline2 = None
    mobile = None
    mobile2 = None
    email = None
    dob = None
    wedding_date = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_type_id(self, type_id):
        self.type_id = type_id

    def set_name(self, name):
        self.name = name

    def set_designation_id(self, designation_id):
        self.designation_id = designation_id

    def set_landline(self, landline):
        self.landline = landline

    def set_landline2(self, landline2):
        self.landline2 = landline2

    def set_mobile(self, mobile):
        self.mobile = mobile

    def set_mobile2(self, mobile2):
        self.mobile2 = mobile2

    def set_email(self, email):
        self.email = email

    def set_dob(self, dob):
        dob = str(dob)
        self.dob = dob

    def set_wedding_date(self, wedding_date):
        wedding_date = str(wedding_date)
        self.wedding_date = wedding_date

    def get_id(self):
        return self.id

    def get_type_id(self):
        return self.type_id

    def get_name(self):
        return self.name

    def get_designation_id(self):
        return self.designation_id

    def get_landline(self):
        return self.landline

    def get_landline2(self):
        return self.landline2

    def get_mobile(self):
        return self.mobile

    def get_mobile2(self):
        return self.mobile2

    def get_email(self):
        return self.email

    def get_dob(self):
        return self.dob

    def get_wedding_date(self):
        return self.wedding_date


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



