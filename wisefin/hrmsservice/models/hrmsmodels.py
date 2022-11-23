from django.db import models
from django.utils.timezone import now
from db.vsolvmodels import VsolvModels,VModels


class EmployeePay(VsolvModels):
    employee_id = models.IntegerField(null=True)
    basic_pay = models.CharField(max_length=128, null=True)
    effective_from = models.DateTimeField(null=True)
    effective_to = models.DateTimeField(null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True)
    updated_date = models.DateTimeField(null=True)


class WorkWeek(VsolvModels):
    day = models.SmallIntegerField(null=True)
    is_working = models.BooleanField(default=True)
    org_id = models.SmallIntegerField(null=True)
    status=models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)


class WorkShift(VsolvModels):
    shift_name = models.CharField(max_length=128, null=True)
    start_time = models.DecimalField(max_digits=4, decimal_places=2,null=True)
    end_time = models.DecimalField(max_digits=4, decimal_places=2,null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True)
    updated_date = models.DateTimeField(null=True)


class PayDay(VsolvModels):
    is_month_last_day = models.BooleanField(default=True)
    is_month_first_day = models.BooleanField(default=True)
    day = models.DateTimeField(default=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)


class EmployeeAdvanceRequest(VsolvModels):
    employee_id = models.IntegerField(null=True)
    requested_advance_amount = models.CharField(max_length=128, null=True)
    approved_advance_amount = models.CharField(max_length=128, null=True)
    status = models.SmallIntegerField(default=1)
    reason = models.CharField(max_length=256, null=True)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True)
    updated_date = models.DateTimeField(null=True)


class EmployeeAdvanceApproval(VsolvModels):
    employee_request = models.ForeignKey(EmployeeAdvanceRequest, on_delete=models.CASCADE, null=True)
    employee_id = models.IntegerField(null=True)
    remarks = models.CharField(max_length=256, null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True)
    updated_date = models.DateTimeField(null=True)


class PayrollConfigStatus(VsolvModels):
    is_work_week_configured = models.BooleanField(default=False)
    is_shift_configured = models.BooleanField(default=False)
    is_pay_day_configured = models.BooleanField(default=False)
    is_pay_component_configured = models.BooleanField(default=False)

#  EMPLOYEE DETAILS INFO

class HrmsAddress(VsolvModels):
    line1 = models.CharField(max_length=2048)
    line2 = models.CharField(max_length=2048, null=True)
    line3 = models.CharField(max_length=2048, null=True)
    pincode_id = models.IntegerField(null=True)
    city_id = models.IntegerField(null=True)
    district_id = models.IntegerField(null=True)
    state_id = models.IntegerField(null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True)
    updated_date = models.DateTimeField(null=True)

class EmployeeDetails(VsolvModels):
    employee_id = models.IntegerField()
    nationality = models.CharField(max_length=120, null=True)
    marital_status = models.CharField(max_length=120, null=True)
    height = models.FloatField(null=True)
    weight = models.FloatField(null=True)
    blood_grp =models.CharField(max_length=10, null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True)
    updated_date = models.DateTimeField(null=True)

class EmployeeFamilyInfo(VsolvModels):
    employee_id = models.IntegerField()
    name=models.CharField(max_length=120, null=True)
    relationship=models.SmallIntegerField(default=1)  # maintain  in util
    dob = models.DateField(null=True)
    no=models.CharField(max_length=20,null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True)
    updated_date = models.DateTimeField(null=True)


class EmployeeEducationDetails(VsolvModels):
    employee_id = models.IntegerField()
    inst_name = models.CharField(max_length=128, null=True)
    passing_year = models.IntegerField(null=True)
    passing_month = models.IntegerField(null=True)
    percentage = models.FloatField(null=True)
    city = models.CharField(max_length=120, null=True)
    title = models.CharField(max_length=120, null=True)
    stream = models.CharField(max_length=120, null=True)
    status = models.IntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True)
    updated_date = models.DateTimeField(null=True)


class EmployeeExperiences(VsolvModels):
    employee_id = models.IntegerField()
    company = models.CharField(max_length=240)
    work_experience = models.FloatField(null=True)
    doj = models.DateField(null=True)
    dor = models.DateField(null=True)
    role = models.CharField(max_length=120)
    city = models.CharField(max_length=120)
    status = models.IntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True)
    updated_date = models.DateTimeField(null=True)

class EmployeeBankDetails(VsolvModels):
    employee_id = models.IntegerField()
    account_name= models.CharField(max_length=120)
    bank_id = models.IntegerField(null=True)
    bank_branch = models.CharField(max_length=120)
    account_no = models.IntegerField(null=True)
    ifsc = models.CharField(max_length=120)
    status = models.IntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True)
    updated_date = models.DateTimeField(null=True)

class EmployeeEmergencyContact(VsolvModels):
    employee_id = models.IntegerField()
    name = models.CharField(max_length=120)
    phone_no = models.CharField(max_length=15,null=True)
    relationship = models.SmallIntegerField(null=True)
    address_id = models.IntegerField(null=True)
    status = models.IntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True)
    updated_date = models.DateTimeField(null=True)

class EmployeeDocuments(VModels):
    rel_id = models.IntegerField(default=-1)
    rel_type = models.IntegerField(default=-1)
    file_name = models.CharField(max_length=256)
    gen_file_name = models.CharField(max_length=512)
    file_id = models.CharField(max_length=64, null=True)
    type = models.IntegerField(null=True)
    status = models.SmallIntegerField(default=1)
    is_user = models.BooleanField(default=True)
    created_by = models.SmallIntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True)
    updated_date = models.DateTimeField(null=True)

class EmployeeRequestQueue(VModels):
    employee_id =models.IntegerField()
    rel_id =models.IntegerField(null=True)
    rel_type =models.IntegerField(null=True)  # Request Util
    approver =models.IntegerField(null=True)
    reason = models.CharField(max_length=512,null=True)
    request_status=models.SmallIntegerField(default=1)
    status = models.SmallIntegerField(default=1)
    is_user = models.BooleanField(default=True)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True)
    updated_date = models.DateTimeField(null=True)

class EmployeeShiftMapping(VModels):
    employee_id =models.IntegerField()
    shift = models.ForeignKey(WorkShift, on_delete=models.CASCADE, null=True)
    effective_from = models.DateField(null=True)
    effective_to = models.DateField(null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True)
    updated_date = models.DateTimeField(null=True)