from utilityservice.permissions.util.apisyncutil import EmployeeGender
from userservice.service.branchservice import EmployeeBranchService
import json

class EmployeeRequest:
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

    def __init__(self, user_obj):
        if 'id' in user_obj:
            self.id = user_obj['id']
        if 'full_name' in user_obj:
            self.full_name = user_obj['full_name']
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

    def get_department_id(self):
        return self.department_id

    def get_designation(self):
        return self.designation

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

    def get_employeebranch(self):
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

class EmployeeSyncRequest:
    id = None
    first_name = None
    middle_name = None
    last_name = None
    employee_name = None
    employee_code = None
    dept_name  = None
    designation = None
    grade = None
    user = None
    employee_emailid = None
    dob = None
    doj = None
    employee_gender = None
    employee_mobileno = None
    employee_type = None
    employee_supervisor_gid = None
    hierarchy =None
    branch = None
    cc_name = None
    bs_name = None
    employee_branch = None

    def __init__(self, user_obj):
        if 'id' in user_obj:
            self.id = user_obj['id']
        if 'employee_name' in user_obj:
            self.full_name = user_obj['employee_name']
        if 'first_name' in user_obj:
            self.first_name = user_obj['first_name']
        if 'middle_name' in user_obj:
            self.middle_name = user_obj['middle_name']
        if 'last_name' in user_obj:
            self.last_name = user_obj['last_name']
        if 'employee_code' in user_obj:
            self.code = user_obj['employee_code']
        if 'dept_name' in user_obj:
            self.department_id = user_obj['dept_name']
        if 'designation_name' in user_obj:
            self.designation = user_obj['designation_name']
        if 'grade' in user_obj:
            self.grade = user_obj['grade']
        if 'user' in user_obj:
            self.user = user_obj['user']
        if 'employee_emailid' in user_obj:
            self.email_id = user_obj['employee_emailid']
        if 'dob' in user_obj:
            self.dob = user_obj['dob']
        if 'doj' in user_obj:
            self.doj = user_obj['doj']
        if 'employee_gender' in user_obj:
            if user_obj['employee_gender'] == 'M':
                self.gender = EmployeeGender.male
            elif user_obj['employee_gender'] == 'F':
                self.gender = EmployeeGender.female
            elif user_obj['employee_gender'] == 'O':
                self.gender = EmployeeGender.others
        if 'employee_mobileno' in user_obj:
            self.phone_no = user_obj['employee_mobileno']
        if 'employee_type' in user_obj:
            self.employee_type = user_obj['employee_type']
        if 'employee_supervisor_gid' in user_obj:
            self.supervisor = user_obj['employee_supervisor_gid']
        if 'hierarchy' in user_obj:
            self.hierarchy = user_obj['hierarchy']
        if 'branch' in user_obj:
            self.branch = user_obj['branch']
        if 'cc_name' in user_obj:
            self.costcentre = user_obj['cc_name']
        if 'bs_name' in user_obj:
            self.businesssegment = user_obj['bs_name']

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

    def get_department_id(self):
        return self.department_id

    def get_designation(self):
        return self.designation

    def get_grade(self):
        return self.grade

    def get_user_id(self):
        return self.user

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

    def get_employeebranch(self):
        return self.employee_branch


from masterservice.service.designationservice import DesignationService
class EmployeeSync_MasterRequest:
    id = None
    first_name = None
    middle_name = None
    last_name = None
    employee_name = None
    employee_code = None
    dept_name  = None
    designation = None
    grade = None
    user = None
    employee_emailid = None
    dob = None
    doj = None
    email_id  = None
    gender = None
    employee_mobileno = None
    employee_type = None
    supervisor = None
    hierarchy =None
    branch = None
    cc_name = None
    bs_name = None
    businesssegment = None
    costcentre = None
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
    department_id = None


    def __init__(self, user_obj):
        if 'id' in user_obj:
            self.id = user_obj['id']
        if 'ename' in user_obj:
            self.full_name = user_obj['ename']
        # if 'first_name' in user_obj:
        #     self.first_name = user_obj['first_name']
        # if 'middle_name' in user_obj:
        #     self.middle_name = user_obj['middle_name']
        # if 'last_name' in user_obj:
        #     self.last_name = user_obj['last_name']
        if 'code' in user_obj:
            code_str = user_obj['code']
            if(user_obj['code'].isnumeric() == True):
                if len(str(user_obj['code'])) == 1:
                    code_str = '00000' + str(user_obj['code'])
                elif len(str(user_obj['code'])) == 2:
                    code_str = '0000' + str(user_obj['code'])
                elif len(str(user_obj['code'])) == 3:
                    code_str = '000' + str(user_obj['code'])
                elif len(str(user_obj['code'])) == 4:
                    code_str = '00' + str(user_obj['code'])
                elif len(str(user_obj['code'])) == 5:
                    code_str = '0' + str(user_obj['code'])
            self.code = code_str
        # if 'eDept' in user_obj:
        #     self.department_id = user_obj['eDept']
        if 'eBranch' in user_obj and user_obj['eBranch'] is not None:
            employee_branch = user_obj['eBranch']
            Branch_service = EmployeeBranchService()
            self.employee_branch_id = Branch_service.isbranchid_get(employee_branch)
        if 'edesig' in user_obj and user_obj['edesig'] is not None:
            self.designation = user_obj['edesig']
            # designation_serv = DesignationService()
            # self.designation = designation_serv.get_state_by_designation(self.designation)
        # if 'GRADE' in user_obj:
        #     self.grade = user_obj['GRADE']
        # if 'user' in user_obj:
        #     self.user = user_obj['user']
        if 'eMailid' in user_obj:
            self.email_id = user_obj['eMailid']
        if 'eDOB' in user_obj:
            self.dob = user_obj['eDOB']
        # if 'DOJ' in user_obj:
        #     self.doj = user_obj['DOJ']
        if 'egender' in user_obj:
            if user_obj['egender'] == 'M':
                self.gender = EmployeeGender.male
            elif user_obj['egender'] == 'F':
                self.gender = EmployeeGender.female
            elif user_obj['egender'] == 'O':
                self.gender = EmployeeGender.others
        # if 'MOBILE' in user_obj:
        #     self.phone_no = user_obj['MOBILE']
        # if 'EMPLOYEE_TYPE' in user_obj:
        #     self.employee_type = user_obj['EMPLOYEE_TYPE']
        # if 'employee_supervisor_gid' in user_obj:
        #     self.supervisor = user_obj['employee_supervisor_gid']

        # if 'hierarchy' in user_obj:
        #     self.hierarchy = user_obj['hierarchy']
        # if 'eBranch' in user_obj:
        #     self.branch = user_obj['eBranch']

        if 'eSrlNo' in user_obj:
            self.srlno = user_obj['eSrlNo']

        if 'eAcctNo' in user_obj:
            self.accountnumber = user_obj['eAcctNo']

        if 'egrade1' in user_obj:
            self.grade1 = user_obj['egrade1']

        if 'egrade1dt' in user_obj:
            self.grade1_date = user_obj['egrade1dt']

        if 'egrade2' in user_obj:
            self.grade2 = user_obj['egrade2']

        if 'egrade2dt' in user_obj:
            self.grade2_date = user_obj['egrade2dt']

        if 'eNoticePrd' in user_obj:
            self.noticeperiod = user_obj['eNoticePrd']

        if 'erole' in user_obj:
            self.role = user_obj['erole']

        if 'eDeptID' in user_obj:
            self.department_id = user_obj['eDeptID']



        # if 'cc_name' in user_obj:
        #     self.costcentre = user_obj['cc_name']
        # if 'bs_name' in user_obj:
        #     self.businesssegment = user_obj['bs_name']


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

    def get_department_id(self):
        return self.department_id

    def get_designation(self):
        return self.designation

    def get_grade(self):
        return self.grade

    def get_user_id(self):
        return self.user

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

    def get_employeebranch(self):
        return self.employee_branch_id

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




class vendor_EmployeeSync_MasterRequest:
    id = None
    first_name = None
    middle_name = None
    last_name = None
    employee_name = None
    employee_code = None
    dept_name  = None
    designation = None
    grade = None
    user = None
    employee_emailid = None
    dob = None
    doj = None
    email_id  = None
    gender = None
    employee_mobileno = None
    employee_type = None
    supervisor = None
    hierarchy =None
    branch = None
    cc_name = None
    bs_name = None
    businesssegment = None
    costcentre = None
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
    department_id = None


    def __init__(self, user_obj):
        if 'id' in user_obj:
            self.id = user_obj['id']
        if 'UserName' in user_obj:
            self.full_name = user_obj['UserName']
        if 'EmpCode' in user_obj:
            code_str = user_obj['EmpCode']
            if(user_obj['EmpCode'].isnumeric() == True):
                if len(str(user_obj['EmpCode'])) == 1:
                    code_str = '00000' + str(user_obj['EmpCode'])
                elif len(str(user_obj['EmpCode'])) == 2:
                    code_str = '0000' + str(user_obj['EmpCode'])
                elif len(str(user_obj['EmpCode'])) == 3:
                    code_str = '000' + str(user_obj['EmpCode'])
                elif len(str(user_obj['EmpCode'])) == 4:
                    code_str = '00' + str(user_obj['EmpCode'])
                elif len(str(user_obj['EmpCode'])) == 5:
                    code_str = '0' + str(user_obj['EmpCode'])
            self.code = code_str
        # if 'eDept' in user_obj:
        #     self.department_id = user_obj['eDept']
        if 'UserBrn' in user_obj and user_obj['UserBrn'] is not None:
            self.employee_branch = user_obj['UserBrn']
            Branch_service = EmployeeBranchService()
            self.employee_branch_id = Branch_service.isbranchid_get(self.employee_branch)
        if 'edesig' in user_obj and user_obj['edesig'] is not None:
            self.designation = user_obj['edesig']

        if 'eMailid' in user_obj:
            self.email_id = user_obj['eMailid']
        if 'eDOB' in user_obj:
            self.dob = user_obj['eDOB']

        if 'egender' in user_obj:
            if user_obj['egender'] == 'M':
                self.gender = EmployeeGender.male
            elif user_obj['egender'] == 'F':
                self.gender = EmployeeGender.female
            elif user_obj['egender'] == 'O':
                self.gender = EmployeeGender.others

        if 'UserBrn' in user_obj:
            self.branch = user_obj['UserBrn']

        if 'eSrlNo' in user_obj:
            self.srlno = user_obj['eSrlNo']

        if 'eAcctNo' in user_obj:
            self.accountnumber = user_obj['eAcctNo']

        if 'egrade1' in user_obj:
            self.grade1 = user_obj['egrade1']

        if 'egrade1dt' in user_obj:
            self.grade1_date = user_obj['egrade1dt']

        if 'egrade2' in user_obj:
            self.grade2 = user_obj['egrade2']

        if 'egrade2dt' in user_obj:
            self.grade2_date = user_obj['egrade2dt']

        if 'eNoticePrd' in user_obj:
            self.noticeperiod = user_obj['eNoticePrd']

        if 'erole' in user_obj:
            self.role = user_obj['erole']

        if 'eDeptID' in user_obj:
            self.department_id = user_obj['eDeptID']


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

    def get_department_id(self):
        return self.department_id

    def get_designation(self):
        return self.designation

    def get_grade(self):
        return self.grade

    def get_user_id(self):
        return self.user

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

    def get_employeebranch(self):
        return self.employee_branch_id

    def get_branch(self):
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


class EmployeeLogRequest:

    maindata = None
    range_from = None
    range_to = None

    def __init__(self, user_obj):
        if 'item' in user_obj:
            self.maindata = user_obj['item']
        if 'rangeTo' in user_obj:
            self.range_to = user_obj['rangeTo']
        if 'rangeFrom' in user_obj:
            self.range_from = user_obj['rangeFrom']

    def get_maindata(self):
        return str(self.maindata)
    def get_range_from(self):
        return self.range_from
    def get_range_to(self):
        return self.range_to


class VendorEmployeeLogRequest:

    maindata = None
    range_from = None
    range_to = None

    def __init__(self, user_obj):
        if 'NonEmp_Details' in user_obj:
            self.maindata = user_obj['NonEmp_Details']
        if 'rangeTo' in user_obj:
            self.range_to = user_obj['rangeTo']
        if 'rangeFrom' in user_obj:
            self.range_from = user_obj['rangeFrom']

    def get_maindata(self):
        return str(self.maindata)
    def get_range_from(self):
        return self.range_from
    def get_range_to(self):
        return self.range_to
class EmployeemobileRequest:

    code= None
    id = None
    mobile_number = None

    def __init__(self, user_obj):
        if 'code' in user_obj:
            self.code = user_obj['code']
        if 'mobile_number' in user_obj:
            self.mobile_number = user_obj['mobile_number']
        if 'id' in user_obj:
            self.id = user_obj['id']

    def get_mobile_number(self):
        return self.mobile_number

    def get_code(self):
        return self.code

    def get_id(self):
        return self.id


class EmployeelogininsertRequest:


    code= None
    fullname = None
    employee_branch = None

    def __init__(self, user_obj):
        if 'EmployeeCode' in user_obj:
            self.code = user_obj['EmployeeCode']
        if 'EmployeeName' in user_obj:
            self.full_name = user_obj['EmployeeName']


    def get_full_name(self):
        return self.full_name

    def get_code(self):
        return self.code

    def get_employeebranch(self):
        return self.employee_branch
