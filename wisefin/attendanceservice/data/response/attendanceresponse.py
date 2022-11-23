import json
from attendanceservice.util.attendanceutil import time_to_m_sec ,common_util_fetch,leaveTypeUtil

class CheckINLOGResponse:
    id = ''
    user_id = ''
    log_date = ''
    log_time = ''
    log_type = ''
    check_in_mode = ''
    status = 1
    org_detail_id = ''
    log_date_time = ''
    location=''

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id_val):
        self.id = ''
        if id_val is not None:
            self.id = id_val

    def set_user_id(self, user_id):
        self.user_id = ''
        if user_id is not None:
            self.user_id = user_id

    def set_log_date(self, log_date):
        self.log_date = ''
        if log_date is not None:
            self.log_date = str(log_date)

    def set_log_time(self, log_time):
        self.log_time = ''
        if log_time is not None:
            self.log_time = time_to_m_sec(log_time)

    def set_log_date_time(self, log_date_time):
        self.log_date_time = ''
        if log_date_time is not None:
            self.log_date_time = str(log_date_time)

    def set_log_type(self, log_type):
        self.log_type = ''
        if log_type is not None:
            self.log_type = log_type

    def set_check_in_mode(self, check_in_mode):
        self.check_in_mode = ''
        if check_in_mode is not None:
            self.check_in_mode = check_in_mode

    def set_status(self, status):
        self.status = 1
        if status is not None:
            self.status = status

    def set_org_detail_id(self, org_detail_id):
        self.org_detail_id = ''
        if org_detail_id is not None:
            self.org_detail_id = org_detail_id

    def set_org_arc_detail(self, org_detail_id,arr):
        self.location = ''
        for i in arr :
            if org_detail_id == i['id']:
                self.location = i
                break


class DailyAttendanceResponse:
    id = ''
    user_id = ''
    first_check_in = ''
    last_check_in = ''
    is_present = ''
    log_date = ''
    is_holiday = ''
    is_weekend = ''
    duration = ''
    status = ''

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id_val):
        self.id = ''
        if id_val is not None:
            self.id = id_val

    def set_user_id(self, user_id):
        self.user_id = ''
        if user_id is not None:
            self.user_id = user_id

    def set_first_check_in(self, first_check_in):
        self.first_check_in = ''
        if first_check_in is not None:
            self.first_check_in = time_to_m_sec(first_check_in)

    def set_last_check_in(self, last_check_in):
        self.last_check_in = ''
        if last_check_in is not None:
            self.last_check_in = time_to_m_sec(last_check_in)

    def set_is_present(self, is_present):
        self.is_present = ''
        if is_present is not None:
            self.is_present = is_present
    def set_is_leave(self, is_leave,is_holiday,is_weekend):
        self.is_leave = ''
        if is_leave is not None:
            if is_weekend is True:
                data = common_util_fetch(leaveTypeUtil.arr , leaveTypeUtil.weekend)
            elif is_holiday is True:
                data = common_util_fetch(leaveTypeUtil.arr , leaveTypeUtil.holiday)
            else:
                data = common_util_fetch(leaveTypeUtil.arr , leaveTypeUtil.other)
            # if data != None:
            self.is_leave = data

    def set_log_date(self, log_date):
        self.log_date = ''
        if log_date is not None:
            self.log_date = str(log_date)

    def set_is_holiday(self, is_holiday):
        self.is_holiday = ''
        if is_holiday is not None:
            self.is_holiday = is_holiday

    def set_is_weekend(self, is_weekend):
        self.is_weekend = ''
        if is_weekend is not None:
            self.is_weekend = is_weekend

    def set_duration(self, duration):
        self.duration = ''
        if duration is not None:
            self.duration = duration

    def set_status(self, status):
        self.status = ''
        if status is not None:
            self.status = status


class PerDayCheckInResponse:
    user_id = ''
    check_in_time = ''
    check_out_time = ''
    duration = ''
    status = 1
    check_in_date_time = ''
    check_out_date_time = ''

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_user_id(self, user_id):
        self.user_id = ''
        if user_id is not None:
            self.user_id = user_id

    def set_check_in_time(self, check_in_time):
        self.check_in_time = ''
        if check_in_time is not None:
            self.check_in_time = check_in_time

    def set_check_out_time(self, check_out_time):
        self.check_out_time = ''
        if check_out_time is not None:
            self.check_out_time = check_out_time

    def set_duration(self, duration):
        self.duration = ''
        if duration is not None:
            self.duration = duration

    def set_status(self, status):
        self.status = 1
        if status is not None:
            self.status = status

    def set_check_in_date_time(self, check_in_date_time):
        self.check_in_date_time = ''
        if check_in_date_time is not None:
            self.check_in_date_time = check_in_date_time

    def set_check_out_date_time(self, check_out_date_time):
        self.check_out_date_time = ''
        if check_out_date_time is not None:
            self.check_out_date_time = check_out_date_time


class PerDayData:
    list_data = ''
    single_data = ''
    first_check_in = ''
    first_check_in_val = ''
    last_check_in = ''
    last_check_in_val = ''
    in_or_out = ''

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_list_data(self, list_data):
        self.list_data = ''
        if list_data is not None:
            self.list_data = list_data

    def set_single_data(self, single_data):
        self.single_data = ''
        if single_data is not None:
            self.single_data = single_data

    def set_first_check_in(self, first_check_in):
        self.first_check_in = ''
        if first_check_in is not None:
            self.first_check_in = first_check_in

    def set_first_check_in_val(self, first_check_in_val):
        self.first_check_in_val = ''
        if first_check_in_val is not None:
            self.first_check_in_val = first_check_in_val

    def set_last_check_in(self, last_check_in):
        self.last_check_in = ''
        if last_check_in is not None:
            self.last_check_in = last_check_in

    def set_last_check_in_val(self, last_check_in_val):
        self.last_check_in_val = ''
        if last_check_in_val is not None:
            self.last_check_in_val = last_check_in_val

    def set_in_or_out(self, in_or_out):
        self.in_or_out = ''
        if in_or_out is not None:
            self.in_or_out = in_or_out
