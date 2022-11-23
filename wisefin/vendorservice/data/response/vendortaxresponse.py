import json


class TaxResponse:
    id = None
    branch_id = None
    branch = None
    msme = None
    type = None
    panno = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_branch_id(self, branch_id):
        self.branch_id = branch_id

    def set_branch(self, branch):
        self.branch = branch

    def set_msme(self, msme):
        self.msme = msme

    def set_type(self, type):
        self.type = type

    def set_panno(self, panno):
        self.panno = panno

    def get_id(self):
        return self.id

    def get_branch_id(self):
        return self.branch_id

    def get_branch(self):
        return self.branch

    def get_msme(self):
        return self.msme

    def get_type(self):
        return self.type

    def get_panno(self):
        return self.panno


