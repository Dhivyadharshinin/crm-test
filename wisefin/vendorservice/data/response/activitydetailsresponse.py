import json


class ActivityDetailsResponse:
    id = None
    activity_id= None
    code = None
    detailname = None
    raisor = None
    approver = None
    remarks = None
    modify_ref_id = None
    modify_status = None
    portal_flag = 0

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_activity_id(self, activity_id):
        self.activity_id = activity_id

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

    def set_created_by(self,created_by):
        self.created_by=created_by

    def set_modify_ref_id(self, modify_ref_id):
        self.modify_ref_id = modify_ref_id

    def set_modify_status(self, modify_status):
        self.modify_status = modify_status



    def get_id(self):
        return self.id

    def get_activity_id(self):
        return self.activity_id

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

    def set_portal_flag(self, portal_flag):
        self.portal_flag = portal_flag

    def get_portal_flag(self):
        return self.portal_flag
