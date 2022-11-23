from django.db import models
from db.vsolvmodels import VsolvModels,VModels
from django.utils.timezone import now


class LeaveRequest(VsolvModels):
    user_id = models.IntegerField(null=True)
    leave_type = models.IntegerField(null=True)
    from_date = models.DateTimeField(null=True)
    to_date = models.DateTimeField(null=True)
    total_days = models.IntegerField(null=True)
    total_hrs = models.IntegerField(null=True)
    reason = models.TextField(null=True)
    status = models.IntegerField(default=1)
    approve_status = models.IntegerField(default=-1)
    approved_by = models.IntegerField(default=-1)
    created_date = models.DateTimeField(default=now)
    created_by = models.IntegerField(null=True)
    updated_date = models.DateTimeField(null=True)
    updated_by = models.IntegerField(null=True)


class LeaveApproveQueue(VsolvModels):
    leave_request = models.ForeignKey(LeaveRequest, on_delete=models.CASCADE)
    status = models.IntegerField(default=1)
    remarks = models.CharField(max_length=128, null=True)
    created_date = models.DateTimeField(default=now)
    created_by = models.IntegerField(null=True)


class CheckInLog(VsolvModels):
    user_id = models.IntegerField(null=True)
    log_date = models.DateField(default=now)
    log_type = models.IntegerField(null=True)
    log_time = models.DateTimeField(default=now)
    check_in_mode = models.IntegerField(null=True)
    status = models.IntegerField(default=1)
    org_detail_id = models.IntegerField(null=True) # org arc detail

class AttendanceSchd(VsolvModels):
    log_date = models.DateField(null=True)
    status = models.IntegerField(default=1)
    is_scheduler =models.BooleanField(default=False)
    created_date = models.DateTimeField(null=True)

class Attendance(VsolvModels):
    user_id = models.IntegerField(null=True)
    first_check_in = models.DateTimeField(null=True)
    last_check_in = models.DateTimeField(null=True)
    is_present = models.BooleanField(default=False)
    log_date = models.DateField(null=True)
    is_leave = models.IntegerField(default=-1)
    is_holiday = models.BooleanField(default=False)
    is_weekend = models.BooleanField(default=False)
    duration = models.FloatField(null=True)
    status = models.IntegerField(default=1)


class AlertMessage(VsolvModels):
    leave_data = models.ForeignKey(LeaveRequest, on_delete=models.CASCADE, null=True)
    status = models.IntegerField(default=0)
    message = models.TextField(null=True)
    created_date = models.DateTimeField(default=now)
    alert_to = models.IntegerField(null=True)
    alert_from = models.IntegerField(null=True)


class AttendanceFileAttachments(VsolvModels):
    ref_id = models.IntegerField(null=True)
    tab_type = models.IntegerField(null=True)
    file_name = models.CharField(max_length=256, null=True)
    gen_file_name = models.CharField(max_length=512, null=True)
    status = models.SmallIntegerField(default=1)
    file_id = models.CharField(max_length=256, default=-1)

#  LEAVE EMP count
class LeaveEmployeeCount(VsolvModels):
    employee_id =models.IntegerField()
    leave_id =models.IntegerField()
    leave_count = models.IntegerField()
    year = models.IntegerField(null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True)
    updated_date = models.DateTimeField(null=True)
    balance_type=models.SmallIntegerField(null=True)

# Attendance report
class AttendanceReport(VModels):
    employee_id = models.IntegerField()
    month= models.IntegerField()
    year= models.IntegerField()
    present_count = models.SmallIntegerField(null=True)
    leave_count = models.SmallIntegerField(null=True)
    premission_hr = models.FloatField(null=True)
    duration = models.FloatField(null=True)
    status = models.IntegerField(default=1)

#  Rule engine 1
class LeaveOrderEngine(VModels):
    leave_type =models.IntegerField()
    child_id = models.IntegerField()
    leave_limit = models.SmallIntegerField(null=True)
    status=models.SmallIntegerField(default=1)
    created_date=models.DateTimeField(default=now)

# rule engine 2
class leaveRequestSplit(VModels):
    leave_request = models.ForeignKey(LeaveRequest, on_delete=models.CASCADE)
    leave_type = models.SmallIntegerField(null=True)
    count = models.SmallIntegerField(null=True)
    status = models.SmallIntegerField(default=1)
    created_by=models.IntegerField(null=True)
    created_date = models.DateTimeField(default=now)
    updated_by =models.IntegerField(null=True)
    updated_date = models.DateTimeField(null=True)
