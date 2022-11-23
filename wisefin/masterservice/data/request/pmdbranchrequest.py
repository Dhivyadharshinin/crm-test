import json


class PmdBranchRequest:
    id = None
    branch_code = None
    branch_name = None
    location = None
    gst_number = None
    status = None
    remarks=None

    def __init__(self, city_obj):
        if 'id' in city_obj:
            self.id = city_obj['id']
        if 'branch_code' in city_obj:
            self.branch_code = city_obj['branch_code']
        if 'branch_name' in city_obj:
            self.branch_name = city_obj['branch_name']
        if 'location' in city_obj:
            self.location = city_obj['location']
        if 'gst_number' in city_obj:
            self.gst_number = city_obj['gst_number']
        if 'status' in city_obj:
            self.status = city_obj['status']
        if 'remarks' in city_obj:
            self.remarks=city_obj['remarks']

    def get_id(self):
        return self.id

    def get_branch_code(self):
        return self.branch_code

    def get_branch_name(self):
        return self.branch_name

    def get_location(self):
        return self.location

    def get_gst_number(self):
        return self.gst_number

    def get_status(self):
        return self.status
    def get_remarks(self):
        return self.remarks
