import json


class DocumentRequest:
    id = None
    partner_id = None
    docgroup_id = None
    period = None
    remarks = None
    file_id = None
    branch_id = None
    gen_file_name = None
    attachment = None
    portal_flag = 0


    def __init__(self, docu_ocj):
        if 'id' in docu_ocj:
            self.id = docu_ocj['id']
        if 'partner_id' in docu_ocj:
            self.partner_id = docu_ocj['partner_id']
        if 'docgroup_id' in docu_ocj:
            self.docgroup_id = docu_ocj['docgroup_id']
        if 'period' in docu_ocj:
            self.period = docu_ocj['period']
        if 'remarks' in docu_ocj:
            self.remarks = docu_ocj['remarks']
        if 'file_id' in docu_ocj:
            self.file_id = docu_ocj['file_id']
        if 'branch_id' in docu_ocj:
            self.branch_id = docu_ocj['branch_id']
        if 'gen_file_name' in docu_ocj:
            self.gen_file_name = docu_ocj['gen_file_name']
        if 'attachment' in docu_ocj:
            self.attachment = docu_ocj['attachment']
        if 'portal_flag' in docu_ocj:
            self.portal_flag = docu_ocj['portal_flag']



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

    def get_gen_file_name(self):
        return self.gen_file_name

    def get_attachment(self):
        return self.attachment

    def get_portal_flag(self):
        return self.portal_flag
