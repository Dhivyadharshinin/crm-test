class QuestionanswerRequest:
    id, question_id, type_id, vendor_id, answer,approving_level,remarks,question_ans_id,header_id,activity_id = (None,) *10

    def __init__(self,user_obj):
        if 'id' in user_obj:
            self.id = user_obj['id']
        if 'question_id' in user_obj:
            self.question_id = user_obj['question_id']
        if 'type_id' in user_obj:
            self.type_id = user_obj['type_id']
        if 'vendor_id' in user_obj:
            self.vendor_id = user_obj['vendor_id']
        if 'answer' in user_obj:
            self.answer = user_obj['answer']
        if 'approving_level' in user_obj:
            self.approving_level = user_obj['approving_level']
        if 'remarks' in user_obj:
            self.remarks = user_obj['remarks']
        if 'question_ans_id' in user_obj:
            self.question_ans_id = user_obj['question_ans_id']
        if 'header_id' in user_obj:
            self.header_id = user_obj['header_id']
        if 'activity_id' in user_obj:
            self.activity_id = user_obj['activity_id']


    def get_id(self):
        return self.id

    def get_question_id(self):
        return self.question_id

    def get_type_id(self):
        return self.type_id

    def get_vendor_id(self):
        return self.vendor_id

    def get_answer(self):
        return self.answer

    def get_approving_level(self):
        return self.approving_level

    def get_remarks(self):
        return self.remarks

    def get_question_ans_id(self):
        return self.question_ans_id

    def get_header_id(self):
        return self.header_id

    def get_activity_id(self):
        return self.activity_id