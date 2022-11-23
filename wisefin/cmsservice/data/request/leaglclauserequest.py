import json

class LegalRequest:
    id = None
    name = None
    clauses = None
    description = None
    type = None
    approval_status = None
    approval_by=None
    agreement=None
    start_date=None
    end_date=None
    is_issued=None
    is_accepted=None
    proposal_id=None

    def __init__(self, header_obj):
        if 'id' in header_obj:
            self.id = header_obj['id']
        if 'name' in header_obj:
            self.name = header_obj['name']
        if 'clauses' in header_obj:
            self.clauses = header_obj['clauses']
        if 'description' in header_obj:
            self.description = header_obj['description']
        if 'type' in header_obj:
            self.type = header_obj['type']
        if 'approval_status' in header_obj:
            self.approval_status = header_obj['approval_status']
        if 'approval_by' in header_obj:
            self.approval_by = header_obj['approval_by']
        if 'agreement' in header_obj:
            self.agreement = header_obj['agreement']
        if 'start_date' in header_obj:
            self.start_date = header_obj['start_date']
        if 'end_date' in header_obj:
            self.end_date = header_obj['end_date']
        if 'is_issued' in header_obj:
            self.is_issued = header_obj['is_issued']
        if 'is_accepted' in header_obj:
            self.is_accepted = header_obj['is_accepted']
        if 'proposal_id' in header_obj:
            self.proposal_id = header_obj['proposal_id']



    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def get_id(self):
        return self.id
    def get_name(self):
        return self.name
    def get_clauses(self):
        return self.clauses
    def get_description(self):
        return self.description
    def get_type(self):
        return self.type
    def get_approval_status(self):
        return self.approval_status
    def get_approval_by(self):
        return self.approval_by
    def get_agreement(self):
        return self.agreement
    def get_start_date(self):
        return self.start_date
    def get_end_date(self):
        return self.end_date
    def get_is_issued(self):
        return self.is_issued
    def get_is_accepted(self):
        return self.is_accepted
    def get_proposal_id(self):
        return self.proposal_id
