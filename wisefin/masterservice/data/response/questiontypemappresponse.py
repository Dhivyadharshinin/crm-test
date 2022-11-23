import json

class QuestiontypemappResponse:
    id, type_id, header, question_id,is_checked = (None,)*5


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_type_id(self, type_id, arr):
        self.type_id = None
        for i in arr:
            if i.id == type_id:
                self.type_id = i
                break


    def set_header(self, header, arr):
        self.header = None
        for i in arr:
            if i.id == header:
                self.header = i
                break

    def set_question_id(self, question_id, arr):
        self.question_id = None
        for i in arr:
            if i.id == question_id:
                self.question_id = i
                break
        # self.question_id = question_id
    def set_header_info(self,header):
        self.header = header
    def set_type(self,type_id):
        self.type_id = type_id
    def set_question_info(self,question_id):
        self.question_id = question_id

    def set_is_checked(self, is_checked):
        self.is_checked = is_checked


class QuestionflagResponse:
    id = None
    questionmapping_id = None
    ref_type = None
    ref_id = None
    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)


    def set_id(self, id):
        self.id = id

    def set_questionmapping_id(self, questionmapping_id):
        self.questionmapping_id = questionmapping_id

    def set_ref_type(self, ref_type):
        self.ref_type = ref_type

    def set_ref_id(self, ref_id):
        self.ref_id = ref_id
