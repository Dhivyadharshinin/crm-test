import json


class ActivityRequest:
    id = None
    type = None
    name = None
    description = None
    branch = None
    start_date = None
    end_date = None
    contract_spend = None
    rm = None
    fidelity = None
    bidding = None
    reason = None
    activity_status=None
    portal_flag = 0
    rel_type=None
    activity_id=None


    def __init__(self, activity_obj):
        if 'id' in activity_obj:
            self.id = activity_obj['id']
        if 'type' in activity_obj:
            self.type = activity_obj['type']
        if 'name' in activity_obj:
            self.name = activity_obj['name']
        if 'description' in activity_obj:
            self.description = activity_obj['description']
        if 'branch' in activity_obj:
            self.branch = activity_obj['branch']
        if 'start_date' in activity_obj:
            self.start_date = activity_obj['start_date']
        if 'end_date' in activity_obj:
            self.end_date = activity_obj['end_date']
        if 'contract_spend' in activity_obj:
            self.contract_spend = activity_obj['contract_spend']
        if 'rm' in activity_obj:
            self.rm = activity_obj['rm']
        if 'fidelity' in activity_obj:
            self.fidelity = activity_obj['fidelity']
        if 'bidding' in activity_obj:
            self.bidding = activity_obj['bidding']
        if 'reason' in activity_obj:
            self.reason = activity_obj['reason']
        if 'contact_id' in activity_obj:
            self.contact_id = activity_obj['contact_id']
        if 'activity_status' in activity_obj:
            self.activity_status = activity_obj['activity_status']
        if 'portal_flag' in activity_obj:
            self.portal_flag = activity_obj['portal_flag']
        if 'rel_type' in activity_obj:
            self.rel_type = activity_obj['rel_type']
        if 'activity_id' in activity_obj:
            self.activity_id = activity_obj['activity_id']

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    # def set_id(self, id):
    #     self.id = id
    #
    # def set_type(self, type):
    #     self.type = type
    #
    # def set_name(self, name):
    #     self.name = name
    #
    # def set_description(self, description):
    #     self.description = description
    #
    # def set_branch(self, branch):
    #     self.branch = branch
    #
    # def set_end_date(self, end_date):
    #     self.end_date = end_date
    #
    # def set_start_date(self, start_date):
    #     self.start_date = start_date
    #
    # def set_contract_spend(self, contract_spend):
    #     self.contract_spend = contract_spend
    #
    # def set_rm(self, rm):
    #     self.rm = rm
    #
    # def set_fidelity(self, fidelity):
    #     self.fidelity = fidelity
    #
    # def set_bidding(self, bidding):
    #     self.bidding = bidding
    #
    # def set_reason(self, reason):
    #     self.type = reason
    #
    # def set_status(self, status):
    #     self.status = status
    #
    # def set_contact(self,contact_id):
    #     self.contact_id=contact_id


    def get_id(self):
        return self.id
    def get_rel_type(self):
        return self.rel_type
    def get_activity_id(self):
        return self.activity_id

    def get_type(self):
        return self.type

    def get_name(self):
        return self.name

    def get_description(self):
        return self.description

    def get_branch(self):
        return self.branch

    def get_startdate(self):
        return self.start_date

    def get_enddate(self):
        return self.end_date

    def get_contractspend(self):
        return self.contract_spend

    def get_rm(self):
        return self.rm

    def get_fidelity(self):
        return self.fidelity

    def get_bidding(self):
        return self.bidding

    def get_reason(self):
        return self.reason

    def get_activity_status(self):
        return self.activity_status

    def get_contact(self):
        return self.contact_id

    def get_portal_flag(self):
        return self.portal_flag


class VendorActivityDetailsRequest:
    id = None
    activity_id = None
    name = None
    detailname = None
    raisor = None
    approver = None
    remarks = None

    def __init__(self, activitydetails_obj):
        if 'id' in activitydetails_obj:
            self.id = activitydetails_obj['id']
        if 'activity_id_id' in activitydetails_obj:
            self.activity_id_id = activitydetails_obj['activity_id_id']
        if 'name' in activitydetails_obj:
            self.name = activitydetails_obj['name']
        if 'detailname' in activitydetails_obj:
            self.detailname = activitydetails_obj['detailname']
        if 'raisor' in activitydetails_obj:
            self.raisor = activitydetails_obj['raisor']
        if 'approver' in activitydetails_obj:
            self.approver = activitydetails_obj['approver']
        if 'remarks' in activitydetails_obj:
            self.remarks = activitydetails_obj['remarks']

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_activity_id(self, activity_id):
        self.activity_id = activity_id

    def set_name(self, name):
        self.name = name

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

    def get_activity_id_id(self):
        return self.activity_id_id

    def get_name(self):
        return self.name

    def get_detailname(self):
        return self.detailname

    def get_raisor(self):
        return self.raisor

    def get_approver(self):
        return self.approver

    def get_remarks(self):
        return self.remarks
