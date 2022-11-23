import json
from taservice.util.ta_util import Status
class Onbehalfrequest:
    id = None
    employeegid = None
    branchgid = None
    onbehalf_employeegid = None
    status = Status.REQUESTED
    onbehalfof = 0

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)

    def __init__(self, get_obj):

        if 'id' in get_obj:
            self.id = get_obj['id']
        if 'employeegid' in get_obj:
            self.employeegid = get_obj['employeegid']
        if 'branchgid' in get_obj:
            self.branchgid = get_obj['branchgid']
        if 'onbehalf_employeegid' in get_obj:
            self.onbehalf_employeegid = get_obj['onbehalf_employeegid']
        if 'status' in get_obj:
            self.status = get_obj['status']
        if 'onbehalfof' in get_obj:
            self.onbehalfof = get_obj['onbehalfof']
        if 'tourgid' in get_obj:
            self.tourgid = get_obj['tourgid']
        if 'approvedby' in get_obj:
            self.approvedby = get_obj['approvedby']
        if 'appcomment' in get_obj:
            self.appcomment = get_obj['appcomment']


    def get_id(self):
        return self.id
    def get_employeegid(self):
        return self.employeegid
    def get_branchgid(self):
        return self.branchgid
    def get_onbehalf_employeegid(self):
        return self.onbehalf_employeegid
    def get_status(self):
        return self.status
    def get_onbehalfof(self):
        if self.onbehalfof >0:
            return self.onbehalfof
        else:
            return 0
