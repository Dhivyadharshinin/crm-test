import json

class ProjectIndentification_Request:
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
    id=None

    def __init__(self, header_obj):
        if 'id' in header_obj:
            self.id = header_obj['id']
        if 'type' in header_obj:
            self.type = header_obj['type']
        if 'code' in header_obj:
            self.code = header_obj['code']
        if 'title' in header_obj:
            self.title = header_obj['title']
        if 'onbehalf_group' in header_obj:
            self.onbehalf_group = header_obj['onbehalf_group']
        if 'approval_status' in header_obj:
            self.approval_status = header_obj['approval_status']
        if 'parallel_approval' in header_obj:
            self.parallel_approval = header_obj['parallel_approval']
        if 'status' in header_obj:
            self.status = header_obj['status']
        if 'project_identification' in header_obj:
            self.project_identification = header_obj['project_identification']
        if 'to_type' in header_obj:
            self.to_type = header_obj['to_type']
        if 'approval_status' in header_obj:
            self.approval_status = header_obj['approval_status']
        if 'tran_type' in header_obj:
            self.tran_type = header_obj['tran_type']
        if 'is_user' in header_obj:
            self.is_user = header_obj['is_user']
        if 'to' in header_obj:
            self.to = header_obj['to']
        if 'tran_status' in header_obj:
            self.tran_status = header_obj['tran_status']
        if 'onbehalf_group' in header_obj:
            self.onbehalf_group = header_obj['onbehalf_group']
        # if 'view_type' in header_obj:
        #     self.view_type = header_obj['view_type']
        if 'order' in header_obj:
            self.order = header_obj['order']

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

    def get_onbehalf_group(self):
        return self.onbehalf_group

    def get_approval_status(self):
        return self.approval_status

    def get_parallel_approval(self):
        return self.parallel_approval

    def get_project_identification(self):
        return self.project_identification

    def get_tran_type(self):
        return self.tran_type

    def get_order(self):
        return self.order

    def get_status(self):
        return self.status

    def get_to_type(self):
        return self.to_type

    def get_is_user(self):
        return self.is_user

    def get_to(self):
        return self.to

    def get_subcat_id(self):
        return self.subcat_id

    def get_onbehalf_group(self):
        return self.onbehalf_group

    def get_tran_status(self):
        return self.tran_status
