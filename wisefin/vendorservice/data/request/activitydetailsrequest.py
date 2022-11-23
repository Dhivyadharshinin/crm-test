import json


class ActivityDetailsRequest:
    id = None
    activity_id = None
    code = None
    detailname = None
    raisor = None
    approver = None
    remarks = None
    portal_flag = 0

    def __init__(self, activitydetails_obj):
        if 'id' in activitydetails_obj:
            self.id = activitydetails_obj['id']
        # if 'activity_id' in activitydetails_obj:
        #     self.activity_id = activitydetails_obj['activity_id']
        if 'code' in activitydetails_obj:
            self.code = activitydetails_obj['code']
        if 'detailname' in activitydetails_obj:
            self.detailname = activitydetails_obj['detailname']
        if 'raisor' in activitydetails_obj:
            self.raisor = activitydetails_obj['raisor']
        if 'approver' in activitydetails_obj:
            self.approver = activitydetails_obj['approver']
        if 'remarks' in activitydetails_obj:
            self.remarks = activitydetails_obj['remarks']
        if 'portal_flag' in activitydetails_obj:
            self.portal_flag = activitydetails_obj['portal_flag']

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    # def set_activity_id(self, activity_id):
    #     self.activity_id = activity_id

    def set_code(self, code):
        self.code = code

    def set_detailname(self, detailname):
        self.detailname = detailname

    def set_raisor(self, raisor):
        self.raisor = raisor

    def set_approver(self, approver):
        self.approver = approver

    def set_remarks(self,remarks):
        self.remarks=remarks

    def get_id(self):
        return self.id

    # def get_activity_id(self):
    #     return self.activity_id

    def get_code(self):
        return self.code

    def get_detailname(self):
        return self.detailname

    def get_raisor(self):
        return self.raisor

    def get_approver(self):
        return self.approver

    def get_remarks(self):
        return self.remarks

    def get_portal_flag(self):
        return self.portal_flag

    def set_portal_flag(self, portal_flag):
        self.portal_flag = portal_flag

