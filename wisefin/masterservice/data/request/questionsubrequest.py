class QuestionsubRequest:
    id, options, question_id, input_type, order = (None,)*5

    def __init__(self, user_obj):
        if 'id' in user_obj:
            self.id = user_obj['id']
        if 'options' in user_obj:
            self.options = user_obj['options']
        if 'question_id' in user_obj:
            self.question_id = user_obj['question_id']
        if 'order' in user_obj:
            self.order = user_obj['order']
        if 'input_type' in user_obj:
            self.input_type = user_obj['input_type']

    def get_id(self):
        return self.id

    def get_options(self):
        return self.options

    def get_question_id(self):
        return self.question_id

    def get_order(self):
        return self.order

    def get_input_type(self):
        return self.input_type

