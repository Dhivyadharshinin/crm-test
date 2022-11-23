import json


class QuestionnaireResponse:
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
    old_remarks = None
    old_ans_bool = None
    old_direction = None
    portal_flag = 0


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_ans_bool(self, ans_bool):
        self.ans_bool = ans_bool

    def set_remarks(self, remarks):
        self.remarks = remarks

    def set_direction(self, direction):
        self.direction = direction

    def set_ques_type(self, ques_type):
        self.ques_type = ques_type

    def set_ques_id(self, ques_id):
        self.ques_id = ques_id

    def set_status(self, status):
        self.status = status

    def set_question(self, question):
        self.question = question

    def set_modify_status(self, modify_status):
        self.modify_status = modify_status

    def set_modify_ref_id(self, modify_ref_id):
        self.modify_ref_id = modify_ref_id

    def set_old_remarks(self,old_remarks):
        self.old_remarks = old_remarks

    def set_old_ans_bool(self,old_ans_bool):
        self.old_ans_bool = old_ans_bool

    def set_old_direction(self, old_direction):
        self.old_direction = old_direction

    def set_portal_flag(self,portal_flag):
        self.portal_flag = portal_flag
