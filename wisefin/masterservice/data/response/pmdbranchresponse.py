import json


class PmdBranchResponse:
    id = None
    branch_code = None
    branch_name = None
    location = None
    gst_number = None
    remarks = None
    status = None

    ACTIVE_VAL = 'ACTIVE'
    IN_ACTIVE_VAL = 'IN ACTIVE'

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_branch_code(self, branch_code):
        self.branch_code = branch_code

    def set_branch_name(self, branch_name):
        self.branch_name = branch_name

    def set_location(self, location):
        self.location = location

    def set_gst_number(self, gst_number):
        self.gst_number = gst_number

    def set_remarks(self, remarks):
        self.remarks = remarks

    def set_status(self, status):
        self.status=status
        # if status == 1:
        #     self.status= self.ACTIVE_VAL
        # else:
        #     self.status=self.IN_ACTIVE_VAL
        # self.status = status
