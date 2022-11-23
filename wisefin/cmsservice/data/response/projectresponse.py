import json
from cmsservice.util.cmsutil import get_approvalstatus


class ProjectResponse:
    id = None
    type = None
    code = None
    title = None
    submission_start_date = None
    submission_end_date = None
    project_start_date = None
    project_end_date = None
    budget = None
    parent = None
    approval_status = None
    is_closed = None
    is_user = None
    commodity_id = None
    subcommodity = None
    onbehalf_group = None
    view_type = None
    description = None
    estimate_currentspent = None
    estimate_save = None
    rel_cat = None
    criticality = None
    vendor_type = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_type(self, type):
        self.type = type

    def set_projecttype(self, type, arr):
        self.type = None
        for i in arr:
            if i.id == type:
                self.type = i
                break

    def set_code(self, code):
        self.code = code

    def set_title(self, title):
        self.title = title

    def set_description(self, description):
        self.description = description

    def set_submission_start_date(self, submission_start_date):
        submission_start_date = str(submission_start_date)
        self.submission_start_date = submission_start_date

    def set_submission_end_date(self, submission_end_date):
        submission_end_date = str(submission_end_date)
        self.submission_end_date = submission_end_date

    def set_project_start_date(self, project_start_date):
        project_start_date = str(project_start_date)
        self.project_start_date = project_start_date

    def set_project_end_date(self, project_end_date):
        project_end_date = str(project_end_date)
        self.project_end_date = project_end_date

    def set_budget(self, budget):
        self.budget = budget

    def set_parent(self, parent):
        self.parent = parent

    def set_approval_status(self, approval_status):
        self.approval_status = get_approvalstatus(approval_status)

    def set_is_closed(self, is_closed):
        self.is_closed = is_closed

    def set_is_user(self, is_user):
        self.is_user = is_user

    def set_commodity_id(self, commodity_id):
        self.commodity_id = commodity_id

    def set_subcommodity(self, subcommodity):
        self.subcommodity = subcommodity

    def set_onbehalf_group(self, onbehalf_group):
        self.onbehalf_group = onbehalf_group

    def set_view_type(self, view_type):
        self.view_type = view_type

    def set_estimate_currentspent(self, estimate_currentspent):
        self.estimate_currentspent = estimate_currentspent

    def set_estimate_save(self, estimate_save):
        self.estimate_save = estimate_save

    def set_rel_cat(self, rel_cat):
        self.rel_cat = rel_cat

    def set_criticality(self, criticality):
        self.criticality = criticality

    def set_vendor_type(self, vendor_type):
        self.vendor_type = vendor_type


class ProjectInvitationResponse:
    id = None
    email_id = None
    v_code = None
    v_name = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_email_id(self, email_id):
        self.email_id = email_id

    def set_v_code(self, v_code):
        self.v_code = v_code
    def set_v_name(self, v_name):
        self.v_name = v_name


class VersionHistoryResponse:
    id = None
    ref_type = None
    ref_id = None
    data_type = None
    version = None
    data = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_ref_id(self, ref_id):
        self.ref_id = ref_id

    def set_ref_type(self, ref_type):
        self.ref_type = ref_type

    def set_data_type(self, data_type):
        self.data_type = data_type

    def set_version(self, version):
        self.version = version

    def set_data(self, data):
        self.data = data
