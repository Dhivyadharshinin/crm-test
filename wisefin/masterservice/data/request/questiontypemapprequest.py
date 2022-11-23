class QuestiontypemappRequest:
    id, type_id, header, question_id, is_checked = (None,)*5

    def __init__(self,user_obj):
        if 'id' in user_obj:
            self.id = user_obj['id']
        if 'type_id' in user_obj:
            self.type_id = user_obj['type_id']
        if 'header' in user_obj:
            self.header = user_obj['header']
        if 'question_id' in user_obj:
            self.question_id = user_obj['question_id']
        if 'is_checked' in user_obj:
            self.is_checked = user_obj['is_checked']

    def get_id(self):
        return self.id

    def get_type_id(self):
        return self.type_id

    def get_header(self):
        return self.header

    def get_question_id(self):
        return self.question_id

    def get_is_checked(self):
        return self.is_checked


class QuestionflagRequest:
    id, questionmapping_id, ref_type, ref_id = (None,)*4

    def __init__(self, user_obj):
        if 'id' in user_obj:
            self.id = user_obj['id']
        if 'questionmapping_id' in user_obj:
            self.questionmapping_id = user_obj['questionmapping_id']
        if 'ref_type' in user_obj:
            self.ref_type = user_obj['ref_type']
        if 'ref_id' in user_obj:
            self.ref_id = user_obj['ref_id']



    def get_id(self):
        return self.id

    def get_questionmapping_id(self):
        return self.questionmapping_id

    def get_ref_type(self):
        return self.ref_type

    def get_ref_id(self):
        return self.ref_id



































































































































