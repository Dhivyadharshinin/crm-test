from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now
from db.vsolvmodels import VsolvModels
# from masterservice.models import MasterBusinessSegment


class EmployeeAddress(models.Model):
    line1 = models.CharField(max_length=2048)
    line2 = models.CharField(max_length=2048, null=True, blank=True)
    line3 = models.CharField(max_length=2048, null=True, blank=True)
    pincode_id = models.IntegerField(default=-1)
    city_id = models.IntegerField(default=-1)
    district_id = models.IntegerField(default=-1)
    state_id = models.IntegerField(default=-1)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class EmployeeContact(models.Model):
    type_id = models.IntegerField(default=-1, null=True, blank=True)
    name = models.CharField(max_length=128, null=True, blank=True)
    designation_id = models.IntegerField(default=-1, null=True, blank=True)
    landline = models.CharField(max_length=2048, null=True, blank=True)
    landline2 = models.CharField(max_length=2048, null=True, blank=True)
    mobile = models.CharField(max_length=2048, null=True, blank=True)
    mobile2 = models.CharField(max_length=2048, null=True, blank=True)
    email = models.CharField(max_length=2048, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    wedding_date = models.DateField(null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class EmployeeBranch(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=128)
    tanno = models.CharField(max_length=48, null=True, blank=True)
    glno = models.CharField(max_length=48, null=True, blank=True)
    stdno = models.CharField(max_length=48, null=True, blank=True)
    incharge = models.CharField(max_length=128, null=True, blank=True)
    entity = models.CharField(max_length=48, null=True, blank=True)
    entity_detail = models.CharField(max_length=128, null=True, blank=True)
    gstin = models.CharField(max_length=20, null=True, blank=True)
    control_office_branch = models.CharField(max_length=20, null=True, blank=True)
    assetcodeprimary = models.CharField(max_length=10, null=True, blank=True)
    address = models.ForeignKey(EmployeeAddress, on_delete=models.SET_NULL, null=True)
    contact = models.ForeignKey(EmployeeContact, on_delete=models.SET_NULL, null=True)
    status = models.SmallIntegerField(default=1)
    lastsync_date = models.DateTimeField(null=True, blank=True)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class Employee(models.Model):
    code = models.CharField(max_length=25)
    full_name = models.CharField(max_length=256)
    email_id = models.EmailField(null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    first_name = models.CharField(max_length=128, null=True, blank=True)
    middle_name = models.CharField(max_length=128, null=True, blank=True)
    last_name = models.CharField(max_length=128, null=True, blank=True)
    designation = models.CharField(max_length=128, null=True, blank=True)
    grade = models.CharField(max_length=128, null=True, blank=True)
    srlno = models.CharField(max_length=64, null=True, blank=True)
    accountnumber = models.CharField(max_length=128, null=True, blank=True)
    branch = models.IntegerField(null=True, blank=True)
    address = models.ForeignKey(EmployeeAddress, on_delete=models.SET_NULL, null=True)
    lastsync_date = models.DateTimeField(null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    grade1 = models.CharField(max_length=128, null=True, blank=True)
    grade2 = models.CharField(max_length=128, null=True, blank=True)
    gender = models.SmallIntegerField(default=-1, null=True, blank=True)
    department_id = models.CharField(max_length=48, null=True, blank=True)
    employee_branch = models.ForeignKey(EmployeeBranch, on_delete=models.SET_NULL, null=True)
    role = models.CharField(max_length=64, null=True, blank=True)
    RM = models.BigIntegerField(null=True)
    functional_head = models.BigIntegerField(null=True)
    grade1_date = models.CharField(max_length=128, null=True, blank=True)
    grade2_date = models.CharField(max_length=128, null=True, blank=True)
    noticeperiod = models.CharField(max_length=128, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    doj = models.DateField(null=True, blank=True)
    phone_no = models.CharField(max_length=48, null=True, blank=True)
    employee_type = models.IntegerField(null=True, blank=True)
    supervisor = models.IntegerField(null=True, blank=True)
    hierarchy = models.IntegerField(null=True, blank=True)
    costcentre = models.IntegerField(null=True, blank=True)
    businesssegment = models.IntegerField(null=True, blank=True)
    contact = models.ForeignKey(EmployeeContact, on_delete=models.SET_NULL, null=True)
    org_id = models.IntegerField(null=True)

class EmployeeEntityMapping(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    entity_id = models.BigIntegerField()
    is_default = models.BooleanField(default=False)


class Module(VsolvModels):
    refid = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=64)
    logo = models.CharField(max_length=64, null=True, blank=True)
    url = models.CharField(max_length=128, null=True, blank=True)
    issys = models.BooleanField(default=False)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)



class EmployeeModuleMapping(VsolvModels):
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    module = models.ForeignKey(Module, on_delete=models.SET_NULL, null=True)
    order = models.IntegerField(null=True, blank=True)



class Role(VsolvModels):
    code = models.CharField(max_length=8)
    name = models.CharField(max_length=64)
    issys = models.BooleanField(default=False)
    operation_name = models.CharField(max_length=64)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)



class RoleModule(VsolvModels):
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    module = models.ForeignKey(Module, on_delete=models.SET_NULL, null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)



class RoleEmployee(VsolvModels):
    role = models.ForeignKey(RoleModule, on_delete=models.SET_NULL, null=True)
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=False, blank=False)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)



class Department(VsolvModels):
    code = models.CharField(max_length=8, unique=True, null=True, blank=True)
    name = models.CharField(max_length=128, null=True, blank=True)
    branch = models.ForeignKey(EmployeeBranch, on_delete=models.SET_NULL, null=True)
    dept_id = models.IntegerField(null=True, blank=True)
    description = models.CharField(max_length=128, null=True, blank=True)
    short_notation = models.CharField(max_length=8, null=True, blank=True)
    is_sys = models.BooleanField(default=False)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)



class EmployeeDepartmentPermission(VsolvModels):
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    isadmin = models.BooleanField(default=False)
    can_create = models.BooleanField(default=False)



class EmployeeDepartment(VsolvModels):
    employee = models.ManyToManyField(Employee)
    code = models.CharField(max_length=8, unique=True)
    name = models.CharField(max_length=128, null=False, blank=False)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)



class BranchType(VsolvModels):
    branch = models.ForeignKey(EmployeeBranch, on_delete=models.SET_NULL, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    is_branchoffice = models.BooleanField(default=False)


class LogoutInfo(VsolvModels):
    employee = models.IntegerField()
    ip_address = models.CharField(max_length=254)
    login_date = models.DateTimeField(default=now)
    logout_date = models.DateTimeField(default=now)


class MasterBusinessSegment(VsolvModels):
    code = models.CharField(max_length=16)
    sector_id = models.IntegerField()
    no = models.IntegerField()
    name = models.CharField(max_length=32)
    description = models.CharField(max_length=128, null=True, blank=True)
    remarks = models.CharField(max_length=128, null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class BusinessSegment(VsolvModels):
    masterbussinesssegment = models.ForeignKey(MasterBusinessSegment, on_delete=models.SET_NULL, null=True)
    code = models.CharField(max_length=20, unique=True)
    no = models.IntegerField()
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=128, null=True, blank=True)
    remarks = models.CharField(max_length=128, null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class EmployeeHierarchy(VsolvModels):
    layer = models.CharField(max_length=128)
    order = models.IntegerField(default=-1)
    remarks = models.CharField(max_length=128, null=True, blank=True)
    flag = models.CharField(max_length=1)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class EmployeeBusinessSegmentMapping(VsolvModels):
    emp_id = models.IntegerField()
    bs_id = models.IntegerField()
    branch_id = models.IntegerField(null=True)
    finyear = models.CharField(max_length=128)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class CostCentre(VsolvModels):
    businesssegment = models.ForeignKey(BusinessSegment, on_delete=models.SET_NULL, null=True)
    code = models.CharField(max_length=20)
    no = models.IntegerField()
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=128, null=True, blank=True)
    remarks = models.CharField(max_length=128, null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class CostCentreBusinessSegmentMaping(VsolvModels):
    no = models.IntegerField()
    name = models.CharField(max_length=64)
    costcentre = models.ForeignKey(CostCentre, on_delete=models.SET_NULL, null=True)
    businesssegment = models.ForeignKey(BusinessSegment, on_delete=models.SET_NULL, null=True)
    code = models.CharField(max_length=16)
    glno = models.CharField(max_length=20)
    description = models.CharField(max_length=128, null=True, blank=True)
    remarks = models.CharField(max_length=128, null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class General_Ledger(VsolvModels):
    no = models.CharField(max_length=48)
    description = models.CharField(max_length=128, null=True, blank=True)
    currency = models.CharField(max_length=20, null=True, blank=True)
    sch16_sortorder = models.CharField(max_length=64, null=True, blank=True)
    sortorder = models.CharField(max_length=64, null=True, blank=True)
    sortorderdesc = models.CharField(max_length=128, null=True, blank=True)
    sch16_desc_bank = models.CharField(max_length=20, null=True, blank=True)
    type = models.CharField(max_length=20, null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    lastsync_date = models.DateTimeField(null=True, blank=True)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class EmployeeLog(VsolvModels):
    maindata = models.TextField(null=True)
    range_from = models.IntegerField(null=True, blank=True)
    range_to = models.IntegerField(null=True, blank=True)
    lastsync_date = models.DateTimeField(null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_date = models.DateTimeField(default=now)


class EmployeeAccountDetails(VsolvModels):
    employee = models.IntegerField()
    paymode = models.IntegerField()
    bank = models.IntegerField()
    bankbranch = models.IntegerField()
    account_number = models.CharField(max_length=64, null=False, blank=False)
    beneficiary_name = models.CharField(max_length=128, null=False, blank=False)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class LoginInfo(VsolvModels):
    employee = models.IntegerField()
    ip_address = models.CharField(max_length=254)
    login_date = models.DateTimeField(default=now)
    user_info = models.CharField(max_length=1024)


class Authrequest(VsolvModels):
    employee = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    mobile_number = models.CharField(max_length=128, null=True, blank=True)


class Employeemobileno(VsolvModels):
    code = models.CharField(max_length=60)
    mobile_number = models.CharField(max_length=128, null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class ApiRelationalMapping(VsolvModels):
    rel_id = models.CharField(max_length=12)
    sync_id = models.IntegerField(null=True, blank=True)
    type = models.CharField(max_length=64)
    sync = models.BooleanField(default=False)
    created_date = models.DateTimeField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)


class UserModuleMapping(VsolvModels):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    module = models.ForeignKey(Module, on_delete=models.SET_NULL, null=True)
    order = models.IntegerField(null=True, blank=True)


class VysfinMigrations(VsolvModels):
    migration_id = models.IntegerField(default=0)
    status = models.BooleanField(default=False)


class Entity(VsolvModels):
    name = models.CharField(max_length=64, null=False, blank=False)
    namespace = models.CharField(max_length=64, null=False, blank=False)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)

class EmployeeReportAproval(VsolvModels):
    employee_id = models.IntegerField(null=True, blank=True)
    reporting_manager = models.SmallIntegerField(default=0)
    approving_manager = models.SmallIntegerField(default=0)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)

class EmployeeGroup(VsolvModels):
    code =models.CharField(max_length=16,null=True)
    name =models.CharField(max_length=90,null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True)
    updated_date = models.DateTimeField(null=True)
    type=models.IntegerField(default=1,null=True)

class EmployeeGroupMapping(VsolvModels):
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    group = models.ForeignKey(EmployeeGroup, on_delete=models.SET_NULL, null=True)
    role=models.SmallIntegerField(default=1)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True)
    updated_date = models.DateTimeField(null=True)


class Vow_user(VsolvModels):
    code = models.CharField(max_length=25, null=True)
    full_name = models.CharField(max_length=256, null=True)
    email_id = models.EmailField(null=True)
    vow_employee_id =models.IntegerField(null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    role = models.CharField(max_length=64, null=True, blank=True)
    phone_no = models.CharField(max_length=48, null=True, blank=True)
    portal = models.IntegerField(null=True)

class Vow_userEntityMapping(models.Model):
    employee = models.ForeignKey(Vow_user, on_delete=models.CASCADE)
    entity_id = models.BigIntegerField()
    is_default = models.BooleanField(default=False)

class DepartmentDocument(VsolvModels):
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=120, null=True)
    remarks = models.CharField(max_length=540, null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)