import json
class Approverequest:
    id= None
    employeeid = None
    branchid = None
    tourapprove = None
    advanceapprove = None
    expenseapprove = None
    status = 1

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)

    def __init__(self, get_obj):

        if 'id' in get_obj:
            self.id = get_obj['id']
        if 'employeeid' in get_obj:
            self.employeeid = get_obj['employeeid']
        if 'branchid' in get_obj:
            self.branchid = get_obj['branchid']
        if 'tourapprove' in get_obj:
            self.tourapprove = get_obj['tourapprove']
        if 'advanceapprove' in get_obj:
            self.advanceapprove = get_obj['advanceapprove']
        if 'status' in get_obj:
            self.status = get_obj['status']
        if 'expenseapprove' in get_obj:
            self.expenseapprove = get_obj['expenseapprove']

    def get_id(self):
        return self.id
    def get_employeeid(self):
        return self.employeeid
    def get_branchid(self):
        return self.branchid
    def get_tourapprove(self):
        return self.tourapprove
    def get_advanceapprove(self):
        return self.advanceapprove
    def get_status(self):
        return self.status
    def get_expenseapprove(self):
        return self.expenseapprove
