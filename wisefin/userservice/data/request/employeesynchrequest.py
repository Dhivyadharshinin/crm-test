from utilityservice.permissions.util.apisyncutil import EmployeeGender
from userservice.service.branchservice import EmployeeBranchService
import json

class EmployeeSynchRequest:
    id = None
    first_name = None
    middle_name = None
    last_name = None
    full_name = None
    code = None
    department_id = None
    designation = None
    grade = None
    user = None
    email_id = None
    dob = None
    doj = None
    gender = None
    phone_no = None
    employee_type = None
    supervisor = None
    hierarchy =None
    branch = None
    costcentre = None
    businesssegment = None
    employee_branch = None

    employee_branch_id = None
    srlno = None
    accountnumber = None
    grade1 = None
    grade1_date = None
    grade2 = None
    grade2_date = None
    noticeperiod = None
    role = None
    branch_code=None
    rm_id=None
    functional_head_id=None
    bank_name=None
    bank_branch_name=None
    def __init__(self, user_obj):
        print(user_obj)
        if 'id' in user_obj:
            self.id = user_obj['id']
        if 'full_name' in user_obj:
            self.full_name = user_obj['full_name']
        if 'branch_code' in user_obj:
            self.branch_code = user_obj['branch_code']
        if 'first_name' in user_obj:
            self.first_name = user_obj['first_name']
        if 'middle_name' in user_obj:
            self.middle_name = user_obj['middle_name']
        if 'last_name' in user_obj:
            self.last_name = user_obj['last_name']
        if 'code' in user_obj:
            self.code = user_obj['code']
        if 'department_id' in user_obj:
            self.department_id = user_obj['department_id']
        if 'designation' in user_obj:
            self.designation = user_obj['designation']
        if 'grade' in user_obj:
            self.grade = user_obj['grade']
        if 'user' in user_obj:
            self.user = user_obj['user']
        if 'email_id' in user_obj:
            self.email_id = user_obj['email_id']
        if 'dob' in user_obj:
            self.dob = user_obj['dob']
        if 'doj' in user_obj:
            self.doj = user_obj['doj']
        if 'gender' in user_obj:
            self.gender = user_obj['gender']
        if 'phone_no' in user_obj:
            self.phone_no = user_obj['phone_no']
        if 'employee_type' in user_obj:
            self.employee_type = user_obj['employee_type']
        if 'supervisor' in user_obj:
            self.supervisor = user_obj['supervisor']
        if 'hierarchy' in user_obj:
            self.hierarchy = user_obj['hierarchy']
        if 'branch' in user_obj:
            self.branch = user_obj['branch']
        if 'costcentre' in user_obj:
            self.costcentre = user_obj['costcentre']
        if 'businesssegment' in user_obj:
            self.businesssegment = user_obj['businesssegment']
        if 'employee_branch' in user_obj:
            self.employee_branch = user_obj['employee_branch']
        if 'employee_branch_id' in user_obj:
            self.employee_branch_id = user_obj['employee_branch_id']
        if 'accountnumber' in user_obj:
            self.accountnumber = user_obj['accountnumber']
        if 'rm_id' in user_obj:
            self.rm_id = user_obj['rm_id']
        if 'functional_head_id' in user_obj:
            self.functional_head_id = user_obj['functional_head_id']



    def get_id(self):
        return self.id

    def get_first_name(self):
        return self.first_name

    def get_branch_code(self):
        return self.branch_code

    def get_middle_name(self):
        return self.middle_name

    def get_last_name(self):
        return self.last_name

    def get_full_name(self):
        return self.full_name

    def get_code(self):
        return self.code

    def get_department_id(self):
        return self.department_id

    def get_designation(self):
        return self.designation

    def get_employee_branch_id(self):
        return self.employee_branch_id

    def get_grade(self):
        return self.grade

    def get_user_id(self):
        return self.user_id

    def get_email_id(self):
        return self.email_id

    def get_dob(self):
        return self.dob

    def get_doj(self):
        return self.doj

    def get_gender(self):
        return self.gender

    def get_phone_no(self):
        return self.phone_no

    def get_employee_type(self):
        return self.employee_type

    def get_supervisor(self):
        return self.supervisor

    def get_hierarchy(self):
        return self.hierarchy

    def get_branch(self):
        return self.branch

    def get_costcentre(self):
        return self.costcentre

    def get_businesssegment(self):
        return self.businesssegment

    def set_user_id(self, user_id):
        self.user_id = user_id

    def get_employee_branch(self):
        return self.employee_branch

    def get_srlno(self):
        return self.srlno

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

    def get_rm_id(self):
        return self.rm_id

    def get_functional_head_id(self):
        return self.functional_head_id




class AddressSynchRequest:
    id = None
    line1 = None
    line2 = None
    line3 = None
    pincode_id = None
    city_id = None
    district_id = None
    state_id = None

    def __init__(self, address_obj):
        if 'id' in address_obj:
            self.id = address_obj['id']
        if 'line1' in address_obj:
            self.line1 = address_obj['line1']
        if 'line2' in address_obj:
            self.line2 = address_obj['line2']
        if 'line3' in address_obj:
            self.line3 = address_obj['line3']
        if 'pincode_id' in address_obj:
            self.pincode_id = address_obj['pincode_id']
        if 'city_id' in address_obj:
            self.city_id = address_obj['city_id']
        if 'district_id' in address_obj:
            self.district_id = address_obj['district_id']
        if 'state_id' in address_obj:
            self.state_id = address_obj['state_id']


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



class ContactSynchRequest:
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

    def __init__(self, contact_obj):
        if 'id' in contact_obj:
            self.id = contact_obj['id']
        if 'type_id' in contact_obj:
            self.type_id = contact_obj['type_id']
        if 'name' in contact_obj:
            self.name = contact_obj['name']
        if 'designation_id' in contact_obj:
            self.designation_id = contact_obj['designation_id']
        if 'landline' in contact_obj:
            self.landline = contact_obj['landline']
        if 'landline2' in contact_obj:
            self.landline2 = contact_obj['landline2']
        if 'mobile' in contact_obj:
            self.mobile = contact_obj['mobile']
        if 'mobile2' in contact_obj:
            self.mobile2 = contact_obj['mobile2']
        if 'email' in contact_obj:
            self.email = contact_obj['email']
        if 'dob' in contact_obj:
            self.dob = contact_obj['dob']
        if 'wedding_date' in contact_obj:
            self.wedding_date = contact_obj['wedding_date']

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

class AccountDetailsSynchRequest:
    benficiary_name=None
    id=None

    def __init__(self, acc_obj):
        if 'id' in acc_obj:
            self.id = acc_obj['id']

        if 'benficiary_name' in acc_obj:
            self.benficiary_name = acc_obj['benficiary_name']
        if 'bank_name' in acc_obj:
            self.bank_name = acc_obj['bank_name']
        if 'branch_name' in acc_obj:
            self.branch_name = acc_obj['branch_name']
        if 'ifsc_code' in acc_obj:
            self.ifsc_code = acc_obj['ifsc_code']
        if 'bank' in acc_obj:
            self.bank = acc_obj['bank']
        if 'account_number' in acc_obj:
            self.account_number = acc_obj['account_number']


    def get_beneficiary_name(self):
        return self.benficiary_name

    def get_bank_name(self):
        return self.bank_name

    def get_branch_name(self):
        return self.branch_name

    def get_ifsc_code(self):
        return self.ifsc_code

    def get_bank(self):
        return self.bank

    def get_account_number(self):
        return self.account_number

    def get_address(self):
        return self.address
