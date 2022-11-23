import json
import datetime


class DocumentResponse:
    partner_id = None
    docgroup_id = None
    period = None
    remarks = None
    file_id = None
    id = None
    branch_id =None
    created_by=None
    modify_ref_id = None
    modify_status = None
    attachment = None
    portal_flag = 0

    def get(self):
      return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_partner_id(self, partner_id):
        self.partner_id = partner_id

    def set_docgroup_id(self, docgroup_id):
        self.docgroup_id = docgroup_id

    def set_remarks(self, remarks):
        self.remarks = remarks

    def set_period(self, period):
        self.period = period

    def set_file_id(self, file_id):
        self.file_id = file_id

    def set_modify_ref_id(self, modify_ref_id):
        self.modify_ref_id = modify_ref_id

    def set_modify_status(self, modify_status):
        self.modify_status = modify_status


    # def set_branch_id(self, branch_id):
    #     self.branch_id = branch_id

    def set_created_by(self, created_by):
        self.created_by = created_by

    def set_attachment(self, attachment):
        self.attachment = attachment

    def get_id(self):
        return self.id

    def get_partner_id(self):
        return self.partner_id

    def get_docgroup_id(self):
        return self.docgroup_id

    def get_period(self):
        return self.period

    def get_remarks(self):
        return self.remarks

    def get_file_id(self):
        return self.file_id

    def get_branch_id(self):
        return self.branch_id

    def get_attachment(self):
        return self.attachment

    def set_portal_flag(self, portal_flag):
        self.portal_flag = portal_flag

    def get_portal_flag(self):
        return self.portal_flag

class AwsResponse:
    id=None
    file_name = None
    gen_file_name = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_file_name(self, file_name):
        self.file_name = file_name

    def set_gen_file_name(self, gen_file_name):
        self.gen_file_name = gen_file_name
