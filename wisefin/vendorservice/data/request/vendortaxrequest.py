import json


class TaxRequest:
    id = None
    branch_id = None
    msme = None
    type = None
    panno = None

    def __init__(self, tax_obj):
        if 'id' in tax_obj:
            self.id = tax_obj['id']
        if 'branch_id' in tax_obj:
            self.branch_id = tax_obj['branch_id']
        if 'msme' in tax_obj:
            self.msme = tax_obj['msme']
        if 'type' in tax_obj:
            self.type = tax_obj['type']
        if 'panno' in tax_obj:
            self.panno = tax_obj['panno']

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_branch_id(self, branch_id):
        self.branch_id = branch_id

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

    def get_msme(self):
        return self.msme

    def get_type(self):
        return self.type

    def get_panno(self):
        return self.panno



