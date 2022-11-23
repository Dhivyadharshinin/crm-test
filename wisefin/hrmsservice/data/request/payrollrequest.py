import json


class WorkWeekRequest:
    id=None
    day =None
    is_working =None
    created_by=None
    created_date=None



    def __init__(self,work_days):
        if 'id' in work_days:
            self.id= work_days['id']
        if 'day' in work_days:
            self.day = work_days['day']
        if 'is_working' in work_days:
            self.is_working = work_days['is_working']
        if 'created_by' in work_days:
            self.created_by = work_days['created_by']
        if 'created_date' in work_days:
            self.created_date = work_days['created_date']

    def get_id(self):
        return self.id
    def get_day (self):
        return self.day
    def get_is_working (self):
        return self.is_working
    def get_created_by(self):
        return self.created_by
    def get_created_date(self):
        return self.created_date




class WorkShiftRequest:
    id=None
    shift_name =None
    start_time =None
    end_time=None
    status=None
    created_by=None
    created_date=None
    updated_by=None
    updated_date=None


    def __init__(self,work_days):
        if 'id' in work_days:
            self.id= work_days['id']
        if 'shift_name' in work_days:
            self.shift_name = work_days['shift_name']
        if 'start_time' in work_days:
            self.start_time = work_days['start_time']
        if 'end_time' in work_days:
            self.end_time = work_days['end_time']
        if 'status' in work_days:
            self.status = work_days['status']
        if 'created_by' in work_days:
            self.created_by = work_days['created_by']
        if 'created_date' in work_days:
            self.created_date = work_days['created_date']
        if 'updated_by' in work_days:
            self.updated_by = work_days['updated_by']
        if 'updated_date' in work_days:
             self.updated_date = work_days['updated_date']

    def get_id(self):
        return self.id
    def get_shift_name(self):
        return self.shift_name
    def get_start_time (self):
        return self.start_time
    def get_end_time(self):
        return self.end_time
    def get_status(self):
        return self.status
    def get_created_by(self):
        return self.created_by
    def get_created_date(self):
        return self.created_date
    def get_updated_by(self):
        return self.updated_by
    def get_updated_date(self):
        return self.updated_date





class PayDayRequest:
    id=None
    is_month_last_day=None
    is_month_first_day=None
    day=None
    status=None
    created_by=None
    created_date=None

    def __init__(self,pay_obj):
        if 'id' in pay_obj:
            self.id=pay_obj['id']
        if 'is_month_last_day' in pay_obj:
            self.is_month_last_day=pay_obj['is_month_last_day']
        if 'is_month_first_day' in pay_obj:
            self.is_month_first_day=pay_obj['is_month_first_day']
        if 'day' in pay_obj:
            self.day=pay_obj['day']
        if  'status' in pay_obj:
            self.status=pay_obj['status']
        if  'created_by' in pay_obj:
            self.created_by=pay_obj['created_by']
        if  'created_date' in pay_obj:
            self.created_date=pay_obj['created_date']

    def get_id(self):
        return self.id
    def get_is_month_last_day(self):
        return self.is_month_last_day
    def get_is_month_first_day(self):
        return self.is_month_first_day
    def get_day(self):
        return self.day
    def get_status(self):
       return self.status
    def get_created_by(self):
       return self.created_by
    def get_created_date(self):
       return self.created_date


class  PayrollConfigStatusRequest:
    id = None
    is_work_week_configured = None
    is_shift_configured = None
    is_pay_day_configured = None
    is_pay_component_configured = None


    def __init__(self,pay_obj):
        if 'id' in pay_obj:
            self.id = pay_obj['id']
        if 'is_work_week_configured' in pay_obj:
            self.is_work_week_configured = pay_obj['is_work_week_configured']
        if 'is_shift_configured' in pay_obj:
            self.is_shift_configured = pay_obj['is_shift_configured']
        if 'is_pay_day_configured' in pay_obj:
            self.is_pay_day_configured = pay_obj['is_pay_day_configured']
        if 'is_pay_component_configured' in pay_obj:
            self.is_pay_component_configured = pay_obj['is_pay_component_configured']

    def get_id(self):
        return self.id

    def get_is_work_week_configured(self):
        return self.is_work_week_configured

    def get_is_shift_configured(self):
        return self.is_shift_configured

    def get_is_pay_day_configured(self):
        return self.is_pay_day_configured

    def get_is_pay_component_configured(self):
        return self.is_pay_component_configured



# is_work_week_configured = models.BooleanField(default=False)
#     is_shift_configured = models.BooleanField(default=False)
#     is_pay_day_configured = models.BooleanField(default=False)
#     is_pay_component_configured = models.BooleanField(default=False)











