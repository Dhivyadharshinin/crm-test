import json


class AppVersionResponse:
    id = None
    code = None
    no = None
    name = None
    ref_no = None
    remarks = None
    created_by = None
    updated_by = None
    status = None

    def __init__(self, app_obj):
        if 'no' in app_obj:
            self.no = app_obj['no']
        if 'ref_no' in app_obj:
            self.ref_no = app_obj['ref_no']
        if 'remarks' in app_obj:
            self.remarks = app_obj['remarks']
        if 'status' in app_obj:
            self.status = app_obj['status']

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_no(self, no):
        self.no = no

    def set_name(self, name):
        self.name = name

    def set_ref_no(self, ref_no):
        self.ref_no = ref_no

    def set_remarks(self, remarks):
        self.remarks = remarks

    def set_status(self, status):
        self.status = status

    def set_created_by(self, created_by):
        self.created_by = created_by

    def set_updated_by(self, updated_by):
        self.updated_by = updated_by

    def get_id(self):
        return self.id

    def get_no(self):
        return self.no

    def get_ref_no(self):
        return self.ref_no

    def get_remarks(self):
        return self.remarks

    def get_status(self):
        return self.status

    def get_created_by(self):
        return self.created_by

    def get_updated_by(self):
        return self.updated_by