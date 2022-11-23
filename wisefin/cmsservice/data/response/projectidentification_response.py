import json

from cmsservice.util.cmsutil import get_approvalstatus


class ProjectIdentification_Response:
    title = None
    onbehalf_group = None
    approval_status = None
    parallel_approval = None
    project_identification = None
    budget = None
    tran_type = None
    to=None
    to_type = None
    is_user = None
    tran_status = None
    order = None
    type = None
    status=None
    approver=None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_approver(self, approver):
        self.approver = approver

    def set_type(self, type):
        self.type = type

    def set_projecttype(self, type, arr):
        self.type = None
        for i in arr:
            if i.id == type:
                self.type = i
                break

    def set_onbehalf_group(self, onbehalf_group):
        self.onbehalf_group = onbehalf_group

    def set_code(self, code):
        self.code = code

    def set_title(self, title):
        self.title = title

    def set_approval_status(self, approval_status):
        self.approval_status = get_approvalstatus(approval_status)

    def set_submission_start_date(self, submission_start_date):
        submission_start_date = str(submission_start_date)
        self.submission_start_date = submission_start_date

    def set_updated_date(self, updated_date):
        if updated_date!=None:
            updated_date = str(updated_date)
        self.updated_date = updated_date

    def set_created_date(self, created_date):
        created_date = str(created_date)
        self.created_date = created_date

    def set_project_end_date(self, project_end_date):
        project_end_date = str(project_end_date)
        self.project_end_date = project_end_date

    def set_tran_type(self, tran_type):
        self.tran_type = tran_type
    def set_to(self, to):
        self.to = to
    def set_to_type(self, to_type):
        self.to_type = to_type
    def set_tran_status(self, tran_status):
        self.tran_status = tran_status
    def set_order(self, order):
        self.order = order
    def set_updated_by(self, updated_by):
        self.updated_by = updated_by

    def set_parent(self, parent):
        self.parent = parent

    def set_parallel_approval(self, parallel_approval):
        self.parallel_approval = parallel_approval
    def set_status(self, status):
        self.status = status

    def set_project_identification(self, project_identification):
        self.project_identification = project_identification

    def set_is_user(self, is_user):
        self.is_user = is_user
    def set_created_by(self, created_by):
        self.created_by = created_by

    def set_cat_id(self, cat_id):
        self.cat_id = cat_id

    def set_subcat_id(self, subcat_id):
        self.subcat_id = subcat_id

    def set_budget(self, budget):
        self.budget = budget

    def set_view_type(self, view_type):
        self.view_type = view_type