import json

from vendorservice.util.vendorutil import get_approving_level


class QuestionanswerResponse:
    id, question_id, type_id, vendor_id, answer, approving_level,header_id,activity_id = (None,) * 8

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_question_id(self, question_id):
        self.question_id = question_id

    def set_type_id(self, type_id):
        self.type_id = type_id

    def set_vendor_id(self, vendor_id):
        self.vendor_id = vendor_id

    def set_answer(self, answer):
        self.answer = answer

    def set_approving_level(self, approving_level):
        approval_level = get_approving_level(approving_level)
        self.approving_level = approval_level

    def set_header_id(self, header_id):
        self.header_id = header_id

    def set_activity_id(self, activity_id):
        self.activity_id = activity_id

    def set_answer_id(self, answer_id):
        self.answer_id = answer_id
    def set_mapping(self, mapping):
        self.mapping = mapping
    def set_file_data(self, file_data):
        self.file_data = file_data

class QuestionsfilesResponse:
    id, question_ans_id, file_name = (None,) * 3

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id
    def set_question_ans_id(self, question_ans_id):
        self.question_ans_id = question_ans_id
    def set_file_name(self, file_name):
        self.name = file_name
    def set_file_id(self, file_id):
        self.file_id = file_id


