import json

class ProjectRequest:
    id = None
    type = None
    code = None
    title = None
    submission_start_date = None
    submission_end_date = None
    project_start_date = None
    project_end_date = None
    budget = None
    parent_id = None
    approval_status = None
    is_closed = None
    is_user = None
    commodity_id = None
    subcommodity = None
    onbehalf_group = None
    view_type = None
    description = None
    parallel_approval = 0
    project_identification = None
    estimate_currentspent = None
    estimate_save = None
    is_draft = None
    rel_cat = None
    criticality = None
    vendor_type = None

    def __init__(self, header_obj):
        if 'id' in header_obj:
            self.id = header_obj['id']
        if 'type' in header_obj:
            self.type = header_obj['type']
        if 'is_draft' in header_obj:
            self.is_draft = header_obj['is_draft']
        if 'code' in header_obj:
            self.code = header_obj['code']
        if 'title' in header_obj:
            self.title = header_obj['title']
        if 'submission_start_date' in header_obj:
            self.submission_start_date = header_obj['submission_start_date']
        if 'submission_end_date' in header_obj:
            self.submission_end_date = header_obj['submission_end_date']
        if 'project_start_date' in header_obj:
            self.project_start_date = header_obj['project_start_date']
        if 'project_end_date' in header_obj:
            self.project_end_date = header_obj['project_end_date']
        if 'budget' in header_obj:
            self.budget = header_obj['budget']
        if 'parent_id' in header_obj:
            self.parent_id = header_obj['parent_id']
        if 'approval_status' in header_obj:
            self.approval_status = header_obj['approval_status']
        if 'is_closed' in header_obj:
            self.is_closed = header_obj['is_closed']
        if 'is_user' in header_obj:
            self.is_user = header_obj['is_user']
        if 'commodity_id' in header_obj:
            self.commodity_id = header_obj['commodity_id']
        if 'subcommodity' in header_obj:
            self.subcommodity = header_obj['subcommodity']
        if 'onbehalf_group' in header_obj:
            self.onbehalf_group = header_obj['onbehalf_group']
        if 'view_type' in header_obj:
            self.view_type = header_obj['view_type']
        if 'description' in header_obj:
            self.description = header_obj['description']
        if 'parallel_approval' in header_obj:
            self.parallel_approval = header_obj['parallel_approval']
        if 'project_identification' in header_obj:
            self.project_identification = header_obj['project_identification']
        if 'estimate_currentspent' in header_obj:
            self.estimate_currentspent = header_obj['estimate_currentspent']
        if 'estimate_save' in header_obj:
            self.estimate_save = header_obj['estimate_save']
        if 'rel_cat' in header_obj:
            self.rel_cat = header_obj['rel_cat']
        if 'criticality' in header_obj:
            self.criticality = header_obj['criticality']
        if 'vendor_type' in header_obj:
            self.vendor_type = header_obj['vendor_type']

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def get_id(self):
        return self.id

    def get_code(self):
        return self.code

    def get_title(self):
        return self.title

    def get_type(self):
        return self.type
    def get_is_draft(self):
        return self.is_draft

    def get_submission_start_date(self):
        return self.submission_start_date

    def get_submission_end_date(self):
        return self.submission_end_date

    def get_project_start_date(self):
        return self.project_start_date

    def get_project_end_date(self):
        return self.project_end_date

    def get_parallel_approval(self):
        return self.parallel_approval

    def get_parent(self):
        return self.parent_id

    def get_budget(self):
        return self.budget

    def get_approval_status(self):
        return self.approval_status

    def get_is_closed(self):
        return self.is_closed

    def get_is_user(self):
        return self.is_user

    def get_commodity_id(self):
        return self.commodity_id

    def get_subcommodity(self):
        return self.subcommodity

    def get_onbehalf_group(self):
        return self.onbehalf_group

    def get_view_type(self):
        return self.view_type

    def get_description(self):
        return self.description

    def get_project_identification(self):
        return self.project_identification

    def get_estimate_currentspent(self):
        return self.estimate_currentspent

    def get_estimate_save(self):
        return self.estimate_save

    def get_rel_cat(self):
        return self.rel_cat

    def get_criticality(self):
        return self.criticality

    def get_vendor_type(self):
        return self.vendor_type
