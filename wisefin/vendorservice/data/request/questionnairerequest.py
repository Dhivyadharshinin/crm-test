class QuestionnaireRequest:
    id = None
    ans_bool = None
    remarks = None
    direction = None
    ques_type = None
    ques_id = None
    status = None
    modify_ref_id = None
    modify_status = None
    question = None
    vendor_id = None
    portal_flag = 0

    def __init__(self, resp_obj):

        if 'id' in resp_obj:
            self.id = resp_obj['id']
        if 'vendor_id' in resp_obj:
            self.vendor_id = resp_obj['vendor_id']
        if 'ans_bool' in resp_obj:
            self.ans_bool = resp_obj['ans_bool']
        if 'remarks' in resp_obj:
            self.remarks = resp_obj['remarks']
        if 'direction' in resp_obj:
            self.direction = resp_obj['direction']
        if 'ques_type' in resp_obj:
            self.ques_type = resp_obj['ques_type']
        if 'ques_id' in resp_obj:
            self.ques_id = resp_obj['ques_id']
        if 'status' in resp_obj:
            self.status = resp_obj['status']
        if 'modify_ref_id' in resp_obj:
            self.modify_ref_id = resp_obj['modify_ref_id']
        if 'modify_status' in resp_obj:
            self.modify_status = resp_obj['modify_status']
        if 'portal_flag' in resp_obj:
            self.portal_flag = resp_obj['portal_flag']

    def get_id(self):
        return self.id

    def get_vendor_id(self):
        return self.vendor_id

    def get_ans_bool(self):
        return self.ans_bool

    def get_remarks(self):
        return self.remarks

    def get_direction(self):
        return self.direction

    def get_ques_type(self):
        return self.ques_type

    def get_ques_id(self):
        return self.ques_id

    def get_status(self):
        return self.status

    def get_modify_ref_id(self):
        return self.modify_ref_id

    def get_modify_status(self):
        return self.modify_status

    def get_question(self):
        return self.question

    def get_portal_flag(self):
        return self.portal_flag
