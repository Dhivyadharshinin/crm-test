import json


class PprAuditResponse:
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

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_refid(self, ref_id):
        self.ref_id = ref_id

    def set_reftype(self, ref_type):
        self.ref_type = ref_type

    def set_data(self, data):
        self.data = data

    def set_userid(self, user_id):
        self.user_id = user_id

    def set_date(self, date):
        date = str(date)
        self.date = date

    def set_reqstatus(self, req_status):
        self.req_status = req_status

    def set_relrefid(self, rel_refid):
        self.rel_refid = rel_refid

    def set_relreftype(self, rel_reftype):
        self.rel_reftype = rel_reftype

    def set_action(self, action):
        self.action = action