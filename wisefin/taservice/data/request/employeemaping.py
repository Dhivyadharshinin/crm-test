import json
from taservice.util.ta_util import Status


class EmployeemappingRequest:
    gid = None
    designation = None
    grade = None
    orderno = None
    status = Status.REQUESTED

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def __init__(self, get_obj):

        if 'gid' in get_obj:
            self.gid = get_obj['gid']
        if 'designation' in get_obj:
            self.designation = get_obj['designation']
        if 'grade' in get_obj:
            self.grade = get_obj['grade']
        if 'orderno' in get_obj:
            self.orderno = get_obj['orderno']
        if 'status' in get_obj:
            self.status = get_obj['status']

    def get_gid(self):
        return self.gid

    def get_designation(self):
        return self.designation

    def get_grade(self):
        return self.grade

    def get_orderno(self):
        return self.orderno

    def get_status(self):
        return self.status

