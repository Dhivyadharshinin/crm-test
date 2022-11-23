import json


class VendorHistoryResponse:
    from_id = None
    to_id = None
    created_date = None
    comments = None
    status = None

    def get(self):
      return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)

    def set_from_id(self, from_id):
        self.from_id = from_id

    def set_to_id(self, to_id):
        self.to_id = to_id

    def set_created_date(self, created_date):
        self.set_created_date = str(created_date)

    def set_comments(self, comments):
        self.comments = comments

    def set_status(self, status):
        self.status = status
