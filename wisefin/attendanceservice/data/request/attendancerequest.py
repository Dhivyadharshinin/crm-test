from attendanceservice.util.attendancevariables import CheckInLogVariable
import datetime
now = datetime.datetime.now()


class CheckInLogRequest:
    id = None
    user_id = None
    log_date = None
    log_time = None
    log_type = None
    check_in_mode = None
    status = None
    org_detail_id = None
    latitude = None
    longitude = None
    ip = None

    def __init__(self, req_obj):
        var = CheckInLogVariable()
        if var.ID in req_obj:
            if req_obj[var.ID] != '':
                self.id = req_obj[var.ID]
        if var.STATUS in req_obj:
            if req_obj[var.STATUS] != '':
                self.status = req_obj[var.STATUS]
        if var.USER_ID in req_obj:
            if req_obj[var.USER_ID] != '':
                self.user_id = req_obj[var.USER_ID]
        if var.LOG_DATE in req_obj:
            if req_obj[var.LOG_DATE] != '':
                self.log_date = req_obj[var.LOG_DATE]
        if var.LOG_TIME in req_obj:
            if req_obj[var.LOG_TIME] != '':
                self.log_time = req_obj[var.LOG_TIME]
        if var.LOG_TYPE in req_obj:
            if req_obj[var.LOG_TYPE] != '':
                self.log_type = req_obj[var.LOG_TYPE]
        if var.CHECK_IN_MODE in req_obj:
            if req_obj[var.CHECK_IN_MODE] != '':
                self.check_in_mode = req_obj[var.CHECK_IN_MODE]
        if var.ORG_DETAIL_ID in req_obj:
            if req_obj[var.ORG_DETAIL_ID] != '':
                self.org_detail_id = req_obj[var.ORG_DETAIL_ID]
        if var.LATITUDE in req_obj:
            if req_obj[var.LATITUDE] != '':
                self.latitude = req_obj[var.LATITUDE]
        if var.LONGITUDE in req_obj:
            if req_obj[var.LONGITUDE] != '':
                self.longitude = req_obj[var.LONGITUDE]
        if var.IP in req_obj:
            if req_obj[var.IP] != '':
                self.ip = req_obj[var.IP]

    def get_id(self):
        return self.id

    def get_status(self):
        return self.status

    def get_user_id(self):
        return self.user_id

    def get_log_date(self):
        return self.log_date

    def get_log_time(self):
        return self.log_time

    def get_log_type(self):
        return self.log_type

    def get_check_in_mode(self):
        return self.check_in_mode

    def get_org_detail_id(self):
        return self.org_detail_id

    def get_latitude(self):
        return self.latitude

    def get_longitude(self):
        return self.longitude

    def get_ip(self):
        return self.ip
