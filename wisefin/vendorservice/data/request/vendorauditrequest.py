import json

class VendorAuditRequest:

    id = None
    ref_id = None
    ref_type = None
    data = None
    user_id = None
    date = None
    req_status = None
    rel_refid = None
    rel_reftype = None
    action = None
    portal_flag = 0


    def __init__(self, audit_data):
        if 'id' in audit_data:
            self.id = audit_data['id']
        if 'ref_id' in audit_data:
            self.ref_id = audit_data['ref_id']
        if 'ref_type' in audit_data:
            self.ref_type = audit_data['ref_type']
        if 'data' in audit_data:
            self.data = audit_data['data']
        if 'user_id' in audit_data:
            self.user_id = audit_data['user_id']
        if 'date' in audit_data:
            self.date = audit_data['date']
        if 'req_status' in audit_data:
            self.req_status = audit_data['req_status']
        if 'rel_refid' in audit_data:
            self.rel_refid = audit_data['rel_refid']
        if 'rel_reftype' in audit_data:
            self.rel_reftype = audit_data['rel_reftype']
        if 'action' in audit_data:
            self.action = audit_data['action']
        if 'portal_flag' in audit_data:
            self.portal_flag = audit_data['portal_flag']


    def get_id(self):
        return self.id
    def get_refid(self):
        return self.ref_id
    def get_reftype(self):
        return self.ref_type
    def get_data(self):
        return self.data
    def get_userid(self):
        return self.user_id
    def get_date(self):
        return self.date
    def get_reqstatus(self):
        return self.req_status
    def get_relrefid(self):
        return self.rel_refid
    def get_relreftype(self):
        return self.rel_reftype
    def get_action(self):
        return self.action


    def set_id(self, id):
        self.id = id

    def set_ref_id(self,ref_id):
        self.ref_id = ref_id

    def set_ref_type(self, ref_type):
        self.ref_type = ref_type

    def set_date(self, date):
        self.date = date

    def set_req_status(self, req_status):
        self.req_status = req_status

    def set_rel_refid(self, rel_refid):
        self.rel_refid = rel_refid

    def set_rel_reftype(self, rel_reftype):
        self.rel_reftype = rel_reftype

    def set_action(self, action):
        self.action = action

    def get_portal_flag(self):
        return self.portal_flag

    def set_portal_flag(self, portal_flag):
        self.portal_flag = portal_flag
