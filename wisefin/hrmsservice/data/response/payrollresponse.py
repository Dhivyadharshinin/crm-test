import json


class WorkWeekResponse:
 id = None
 day = None
 is_working = None
 created_by = None
 created_date = None

 def get(self):
     return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

 def set_id(self, id):
     self.id = id

 def set_day(self, day):
     self.day = day

 def set_is_working(self, is_working):
     self.is_working = is_working

 def set_created_by(self, created_by):
     self.created_by = created_by

 def set_created_date(self, created_date):
     self.created_date = created_date




class WorkShiftResponse:
    id = None
    shift_name = None
    start_time = None
    end_time = None
    status = None
    created_by = None
    created_date = None
    updated_by = None
    updated_date = None


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True, indent=4)

    def set_id(self,id):
        self.id = id

    def set_shift_name(self,shift_name):
        self.shift_name =shift_name

    def set_start_time(self,start_time):
        self.start_time= str(start_time)

    def set_end_time(self,end_time):
        self.end_time=str(end_time)

    def set_status (self,status):
         self.status=status

    def set_created_by(self, created_by):
        self.created_by = created_by

    def set_created_date(self, created_date):
        self.created_date = str(created_date)

    def set_updated_by(self, updated_by):
         self.updated_by = updated_by

    def set_updated_date(self, updated_date):
         self.updated_date = str(updated_date)

class PayDayResponse:
    id = None
    is_month_last_day = None
    kis_month_first_day = None
    day = None
    status = None
    created_by = None
    created_date = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True, indent=4)

    def set_id(self,id):
        self.id=id
    def set_is_month_last_day(self, is_month_last_day):
         self. is_month_last_day= is_month_last_day

    def set_is_month_first_day(self, is_month_first_day):
        self.is_month_first_day = is_month_first_day

    def set_day(self,day):
        self.day = str(day)

    def set_status(self,status):
        self.status = status

    def set_created_by(self,created_by):
        self.created_by = created_by

    def set_created_date(self,created_date):
        self.created_date = created_date

class PayrollConfigStatusResponse:
    id = None
    is_work_week_configured = None
    is_shift_configured = None
    is_pay_day_configured = None
    is_pay_component_configured = None


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True, indent=4)
    def set_id(self,id):
        self.id=id

    def set_is_work_week_configured(self,is_work_week_configured):
        self.is_work_week_configured = is_work_week_configured

    def set_is_shift_configured(self, is_shift_configured):
        self.is_shift_configured = is_shift_configured

    def set_is_pay_day_configured(self, is_pay_day_configured):
        self.is_pay_day_configured = is_pay_day_configured

    def set_is_pay_component_configured(self, is_pay_component_configured):
        self.is_pay_component_configured = is_pay_component_configured











