import json

class InwardTranResponse:
    id = None
    ref_id = None
    ref_type = None
    from_user_id = None
    to_user_id = None
    created_date = None
    comments = None
    remarks=None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_ref_id(self, ref_id):
        self.ref_id = ref_id

    def set_ref_type(self, ref_type):
        self.ref_type = ref_type

    def set_from_user_id(self, from_user_id):
        self.from_user_id = from_user_id

    def set_to_user_id(self, to_user_id):
        self.to_user_id = to_user_id

    def set_created_date(self, created_date):
        created_date = str(created_date)
        self.created_date = created_date

    def set_comments(self, comments):
        self.comments = comments

    def set_remarks(self, remarks):
        self.remarks = remarks