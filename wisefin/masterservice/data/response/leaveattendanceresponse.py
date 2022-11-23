import json


class OrgIpResponse:
    id = ''
    ip = ''
    status = 1
    org_detail_id = ''

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id_val):
        self.id = ''
        if id_val is not None:
            self.id = id_val

    def set_ip(self, ip):
        self.ip = ''
        if ip is not None:
            self.ip = str(ip)

    def set_status(self, status):
        self.status = 1
        if status is not None:
            self.status = status

    def set_org_detail_id(self, org_detail_id):
        self.org_detail_id = ''
        if org_detail_id is not None:
            self.org_detail_id = org_detail_id


class OrgDetailsResponse:
    id = ''
    latitude = ''
    longitude = ''
    code = ''
    name = ''
    arc_type = ''
    status = 1
    radius = ''

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id_val):
        self.id = ''
        if id_val is not None:
            self.id = id_val

    def set_latitude(self, latitude):
        self.latitude = ''
        if latitude is not None:
            self.latitude = str(latitude)

    def set_longitude(self, longitude):
        self.longitude = ''
        if longitude is not None:
            self.longitude = str(longitude)

    def set_radius(self, radius):
        self.radius = ''
        if radius is not None:
            self.radius = str(radius)

    def set_code(self, code):
        self.code = ''
        if code is not None:
            self.code = code

    def set_name(self, name):
        self.name = ''
        if name is not None:
            self.name = name

    def set_arc_type(self, arc_type):
        self.arc_type = ''
        if arc_type is not None:
            self.arc_type = arc_type

    def set_status(self, status):
        self.status = 1
        if status is not None:
            self.status = status


class AttendanceConfigResponse:
    id = ''
    check_in_mode = ''
    status = 1
    code = ''
    namespace = ''

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id_val):
        self.id = ''
        if id_val is not None:
            self.id = id_val

    def set_check_in_mode(self, check_in_mode):
        self.check_in_mode = ''
        if check_in_mode is not None:
            self.check_in_mode = check_in_mode

    def set_status(self, status):
        self.status = 1
        if status is not None:
            self.status = status

    def set_code(self, code):
        self.code = ''
        if code is not None:
            self.code = code

    def set_namespace(self, namespace):
        self.namespace = ''
        if namespace is not None:
            self.namespace = namespace


class LeaveTypeResponse:
    id = ''
    name = ''
    has_attendance = ''
    has_salary = ''
    status = 1
    code = ''

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id_val):
        self.id = ''
        if id_val is not None:
            self.id = id_val

    def set_name(self, name):
        self.name = ''
        if name is not None:
            self.name = name

    def set_has_attendance(self, has_attendance):
        self.has_attendance = ''
        if has_attendance is not None:
            self.has_attendance = has_attendance

    def set_has_salary(self, has_salary):
        self.has_salary = ''
        if has_salary is not None:
            self.has_salary = has_salary

    def set_status(self, status):
        self.status = 1
        if status is not None:
            self.status = status

    def set_code(self, code):
        self.code = ''
        if code is not None:
            self.code = code


class HolidayResponse:
    id = ''
    name = ''
    holiday_date = ''
    type = ''
    code = ''
    status = 1

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id_val):
        self.id = ''
        if id_val is not None:
            self.id = id_val

    def set_name(self, name):
        self.name = ''
        if name is not None:
            self.name = name

    def set_holiday_date(self, holiday_date):
        self.holiday_date = ''
        if holiday_date is not None:
            self.holiday_date = str(holiday_date)

    def set_type(self, type_val):
        self.type = ''
        if type_val is not None:
            self.type = type_val

    def set_code(self, code):
        self.code = ''
        if code is not None:
            self.code = code

    def set_status(self, status):
        self.status = 1
        if status is not None:
            self.status = status
