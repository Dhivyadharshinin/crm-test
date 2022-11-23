from django.db import models
from db.vsolvmodels import VsolvModels,VModels
from django.utils.timezone import now

class SalaryComponent(VsolvModels):
    code = models.CharField(max_length=8, null=True, blank=True)
    name = models.CharField(max_length=128)
    type = models.CharField(max_length=128)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)

class SalaryLabel(VsolvModels):
    code = models.CharField(max_length=8, null=True, blank=True)
    name = models.CharField(max_length=128)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)

class SalarystructureMapping(VsolvModels):
    name = models.CharField(max_length=128, null=True, blank=True)
    salarycomponent= models.ForeignKey(SalaryComponent, on_delete=models.CASCADE, null=True)
    salarylabel= models.ForeignKey(SalaryLabel, on_delete=models.CASCADE, null=True)
    is_amount = models.CharField(max_length=8, null=True, blank=True)
    amount_value=models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    type = models.CharField(max_length=128)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)

class DetectionInfo(VsolvModels):
    salarymapping = models.ForeignKey(SalarystructureMapping, on_delete=models.CASCADE, null=True)
    from_month = models.CharField(max_length=128)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)

class EmployeeStructure_Mapping(VsolvModels):
    emp_id = models.IntegerField(null=True, blank=True)
    salarymapping = models.ForeignKey(SalarystructureMapping, on_delete=models.CASCADE, null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)

class Employee_Attendancedetails(VsolvModels):
    emp_id = models.IntegerField(null=True, blank=True)
    month = models.CharField(max_length=128,null=True, blank=True)
    year = models.CharField(max_length=128,null=True, blank=True)
    total_days = models.CharField(max_length=128,null=True, blank=True)
    leave_days = models.CharField(max_length=128,null=True, blank=True)
    holiday_count = models.CharField(max_length=128,null=True, blank=True)
    presentday_count = models.CharField(max_length=128,null=True, blank=True)
    designation = models.CharField(max_length=128,null=True, blank=True)
    uan_no = models.CharField(max_length=128,null=True, blank=True)
    doj = models.DateTimeField(null=True, blank=True)
    esic_no = models.CharField(max_length=128,null=True, blank=True)
    bankaccount_number = models.CharField(max_length=128,null=True, blank=True)
    permission_hrs = models.CharField(max_length=128,null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)

class Employee_FinalSalary(VsolvModels):
    employeeStructure = models.ForeignKey(EmployeeStructure_Mapping, on_delete=models.CASCADE, null=True)
    employee_attendancedetails = models.ForeignKey(Employee_Attendancedetails, on_delete=models.CASCADE, null=True)
    amount_formula = models.CharField(max_length=128,null=True, blank=True)
    amount = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    edit_amount = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    flag = models.IntegerField(default=1)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)