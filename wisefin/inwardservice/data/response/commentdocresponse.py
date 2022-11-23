import json

class CommentDocResponse:
    id = None
    inwarddetails = None
    employee = None
    branch = None
    comment = None
    created_by = None
    created_date = None
    updated_by = None
    updated_date = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_inwarddetails(self, inwarddetails):
        self.inwarddetails = inwarddetails

    def set_employee(self, employee):
        self.employee = employee

    def set_branch(self, branch):
        self.branch = branch

    def set_comment(self, comment):
        self.comment = comment

    def get_id(self):
        return self.id

    def get_employee(self):
        return self.employee

    def get_branch(self):
        return self.branch

    def get_comment(self):
        return self.comment