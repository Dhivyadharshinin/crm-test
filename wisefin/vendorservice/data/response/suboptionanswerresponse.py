import json


class SuboptionanswerResponse:
    id, question_ans_id, option_id, answer = (None,) * 4

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_question_ans_id(self, question_ans_id):
        self.question_ans_id = question_ans_id

    def set_option_id(self, option_id):
        self.option_id = option_id

    def set_answer(self, answer):
        self.answer = answer

