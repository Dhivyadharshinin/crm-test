import json
from cmsservice.util.cmsutil import get_approvalstatus


class ProposerResponse:
    id = None
    code = None
    name = None
    submitted_date = None
    budget = None
    approval_status = None
    proposer_code = None
    project_id = None
    is_shortlisted = None
    is_finalized = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_code(self, code):
        self.code = code

    def set_name(self, name):
        self.name = name

    def set_submitted_date(self, submitted_date):
        submitted_date = str(submitted_date)
        self.submitted_date = submitted_date

    def set_budget(self, budget):
        self.budget = budget

    def set_approval_status(self, approval_status):
        self.approval_status = get_approvalstatus(approval_status)

    def set_proposer_code(self, proposer_code):
        self.proposer_code = proposer_code

    def set_project_id(self, project_id):
        self.project_id = project_id

    def set_is_shortlisted(self, is_shortlisted):
        self.is_shortlisted = is_shortlisted

    def set_is_finalized(self, is_finalized):
        self.is_finalized = is_finalized
