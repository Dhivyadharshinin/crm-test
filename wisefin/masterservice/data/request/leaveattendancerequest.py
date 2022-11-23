from masterservice.util.masterservicevariable import OrgIpVariable, OrgDetailsVariable, AttendanceConfigVariable, \
    LeaveTypeVariable, HolidayVariable


class OrgIpRequest:
    id = None
    ip = None
    status = None
    org_detail_id = None
    ip_arr = []

    def __init__(self, req_obj):
        var = OrgIpVariable()
        if var.ID in req_obj:
            if req_obj[var.ID] != '':
                self.id = req_obj[var.ID]
        if var.IP in req_obj:
            if req_obj[var.IP] != '':
                self.ip = req_obj[var.IP]
        if var.STATUS in req_obj:
            if req_obj[var.STATUS] != '':
                self.status = req_obj[var.STATUS]
        if var.ORG_DETAIL_ID in req_obj:
            if req_obj[var.ORG_DETAIL_ID] != '':
                self.org_detail_id = req_obj[var.ORG_DETAIL_ID]
        if var.IP_ARR in req_obj:
            if req_obj[var.IP_ARR] != '':
                self.ip_arr = req_obj[var.IP_ARR]

    def get_id(self):
        return self.id

    def get_ip(self):
        return self.ip

    def get_status(self):
        return self.status

    def get_org_detail_id(self):
        return self.org_detail_id

    def get_ip_arr(self):
        return self.ip_arr


class OrgDetailsRequest:
    id = None
    latitude = None
    longitude = None
    name = None
    arc_type = None
    status = None
    radius = None

    def __init__(self, req_obj):
        var = OrgDetailsVariable()
        if var.ID in req_obj:
            if req_obj[var.ID] != '':
                self.id = req_obj[var.ID]
        if var.LATITUDE in req_obj:
            if req_obj[var.LATITUDE] != '':
                self.latitude = req_obj[var.LATITUDE]
        if var.LONGITUDE in req_obj:
            if req_obj[var.LONGITUDE] != '':
                self.longitude = req_obj[var.LONGITUDE]
        if var.NAME in req_obj:
            if req_obj[var.NAME] != '':
                self.name = req_obj[var.NAME]
        if var.ARC_TYPE in req_obj:
            if req_obj[var.ARC_TYPE] != '':
                self.arc_type = req_obj[var.ARC_TYPE]
        if var.STATUS in req_obj:
            if req_obj[var.STATUS] != '':
                self.status = req_obj[var.STATUS]
        if var.RADIUS in req_obj:
            if req_obj[var.RADIUS] != '':
                self.radius = req_obj[var.RADIUS]

    def get_id(self):
        return self.id

    def get_latitude(self):
        return self.latitude

    def get_longitude(self):
        return self.longitude

    def get_name(self):
        return self.name
    def get_arc_type(self):
        return self.arc_type
    def get_status(self):
        return self.status

    def get_radius(self):
        return self.radius


class AttendanceConfigRequest:
    id = None
    check_in_mode = None
    status = None
    namespace = None

    def __init__(self, req_obj):
        var = AttendanceConfigVariable()
        if var.ID in req_obj:
            if req_obj[var.ID] != '':
                self.id = req_obj[var.ID]
        if var.CHECK_IN_MODE in req_obj:
            if req_obj[var.CHECK_IN_MODE] != '':
                self.check_in_mode = req_obj[var.CHECK_IN_MODE]
        if var.STATUS in req_obj:
            if req_obj[var.STATUS] != '':
                self.status = req_obj[var.STATUS]
        if var.NAMESPACE in req_obj:
            if req_obj[var.NAMESPACE] != '':
                self.namespace = req_obj[var.NAMESPACE]

    def get_id(self):
        return self.id

    def get_check_in_mode(self):
        return self.check_in_mode

    def get_status(self):
        return self.status

    def get_namespace(self):
        return self.namespace


class LeaveTypeRequest:
    id = None
    name = None
    has_attendance = None
    has_salary = None
    status = None

    def __init__(self, req_obj):
        var = LeaveTypeVariable()
        if var.ID in req_obj:
            if req_obj[var.ID] != '':
                self.id = req_obj[var.ID]
        if var.NAME in req_obj:
            if req_obj[var.NAME] != '':
                self.name = req_obj[var.NAME]
        if var.HAS_ATTENDANCE in req_obj:
            if req_obj[var.HAS_ATTENDANCE] != '':
                self.has_attendance = req_obj[var.HAS_ATTENDANCE]
        if var.HAS_SALARY in req_obj:
            if req_obj[var.HAS_SALARY] != '':
                self.has_salary = req_obj[var.HAS_SALARY]
        if var.STATUS in req_obj:
            if req_obj[var.STATUS] != '':
                self.status = req_obj[var.STATUS]

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_has_attendance(self):
        return self.has_attendance

    def get_has_salary(self):
        return self.has_salary

    def get_status(self):
        return self.status


class HolidayRequest:
    id = None
    name = None
    holiday_date = None
    type = None
    status = 1

    def __init__(self, req_obj):
        var = HolidayVariable()
        if var.ID in req_obj:
            if req_obj[var.ID] != '':
                self.id = req_obj[var.ID]
        if var.NAME in req_obj:
            if req_obj[var.NAME] != '':
                self.name = req_obj[var.NAME]
        if var.HOLIDAY_DATE in req_obj:
            if req_obj[var.HOLIDAY_DATE] != '':
                self.holiday_date = req_obj[var.HOLIDAY_DATE]
        if var.TYPE in req_obj:
            if req_obj[var.TYPE] != '':
                self.type = req_obj[var.TYPE]
        if var.STATUS in req_obj:
            if req_obj[var.STATUS] != '':
                self.status = req_obj[var.STATUS]

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_holiday_date(self):
        return self.holiday_date

    def get_type(self):
        return self.type

    def get_status(self):
        return self.status
