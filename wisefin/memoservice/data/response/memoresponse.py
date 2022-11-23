import json


class MemoResponse:
    id = None
    subject = None
    req_date = None
    category = None
    sub_category = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_subject(self, subject):
        self.subject = subject

    def set_req_date(self, req_date):
        self.req_date = str(req_date)

    def set_category(self, category):
        self.category = category

    def set_sub_category(self, sub_category):
        self.sub_category = sub_category
