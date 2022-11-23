import json


class ProposerRequest:
    id = None
    code = None
    name = None
    submitted_date = None
    budget = 0
    is_vendor = None

    def __init__(self, header_obj):
        if 'id' in header_obj:
            self.id = header_obj['id']
        if 'code' in header_obj:
            self.code = header_obj['code']
        if 'proposer_code' in header_obj:
            self.proposer_code = header_obj['proposer_code']
        if 'name' in header_obj:
            self.name = header_obj['name']
        if 'submitted_date' in header_obj:
            self.submitted_date = header_obj['submitted_date']
        if 'budget' in header_obj:
            self.budget = header_obj['budget']
        if 'is_vendor' in header_obj:
            self.is_vendor = header_obj['is_vendor']

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def get_id(self):
        return self.id

    def get_code(self):
        return self.code

    def get_proposer_code(self):
        return self.proposer_code

    def get_name(self):
        return self.name

    def get_submitted_date(self):
        return self.submitted_date

    def get_budget(self):
        return self.budget

    def get_is_vendor(self):
        return self.is_vendor
