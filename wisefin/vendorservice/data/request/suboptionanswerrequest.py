class SuboptionsanswerRequest:
    id, question_ans_id, option_id, answer = (None,)*4

    def __init__(self, user_obj):
        if 'id' in user_obj:
            self.id = user_obj['id']
        if 'question_ans_id' in user_obj:
            self.question_ans_id = user_obj['question_ans_id']
        if 'option_id' in user_obj:
            self.option_id = user_obj['option_id']
        if 'answer' in user_obj:
            self.answer = user_obj['answer']

    def get_id(self):
        return self.id

    def get_question_ans_id(self):
        return self.question_ans_id

    def get_option_id(self):
        return self.option_id

    def get_answer(self):
        return self.answer