import json


class CommentDocRequest:
    id = None
    inwardetails = None
    employee = None
    branch = None
    comment = None
    created_by = None
    created_date = None
    updated_by = None
    updated_date = None



    def __init__(self, comment_obj):

        if 'id' in comment_obj:
            self.id = comment_obj['id']
        if 'employee_id' in comment_obj:
            self.employee = comment_obj['employee_id']
        if 'branch_id' in comment_obj:
            self.branch = comment_obj['branch_id']
        if 'comment' in comment_obj:
            self.comment = comment_obj['comment']

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
    def get_id(self):
        return self.id

    def get_employee(self):
        return self.employee

    def get_branch(self):
        return self.branch

    def get_comment(self):
        return self.comment