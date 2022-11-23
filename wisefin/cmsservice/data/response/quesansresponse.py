import json


class Quesansresponse:
    id = None
    question_id = None
    question_type = None
    ans = None
    option_type = None
    option_id = None
    ref_type = None
    ref_id = None
    is_user = None
    classify_id = None
    file = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_question_id(self, question_id):
        self.question_id = question_id

    def set_question_type(self, question_type):
        self.question_type = question_type

    def set_answer(self, answer):
        self.ans = answer

    def set_option_type(self, option_type):
        self.option_type = option_type

    def set_option_id(self, option_id):
        self.option_id = option_id

    def set_ref_type(self, ref_type):
        self.ref_type = ref_type

    def set_ref_id(self, ref_id):
        self.ref_id = ref_id

    def set_is_user(self, is_user):
        self.is_user = is_user

    def set_classify_id(self, classify_id):
        self.classify_id = classify_id

    def set_file(self, file):
        self.file = file


class Quesansmapresponse:
    id = None
    answer_id = None
    type_id = None
    subtype_id = None
    reftype_id = None
    ref_id = None
    is_user = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_answer_id(self, answer_id):
        self.answer_id = answer_id

    def set_type_id(self, type_id):
        self.type_id = type_id

    def set_subtype_id(self, subtype_id):
        self.subtype_id = subtype_id

    def set_reftype_id(self, reftype_id):
        self.reftype_id = reftype_id

    def set_ref_id(self, ref_id):
        self.ref_id = ref_id

    def set_is_user(self, is_user):
        self.is_user = is_user


class Answermapresponse:
    id = None
    answer_id = None
    ref_type = None
    ref_id = None
    comments = None
    score = None
    is_user = None
    red_flag = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_answer_id(self, answer_id):
        self.answer_id = answer_id

    def set_ref_type(self, ref_type):
        self.ref_type = ref_type

    def set_ref_id(self, ref_id):
        self.ref_id = ref_id

    def set_comments(self, comments):
        self.comments = comments

    def set_score(self, score):
        self.score = score

    def set_is_user(self, is_user):
        self.is_user = is_user
    def set_red_flag(self,red_flag):
        self.red_flag = red_flag


class Quesclassifyresponse:
    id = None
    classify_id = None
    classify_type = None
    question_type = None
    is_user = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_classify_id(self, classify_id):
        self.classify_id = classify_id

    def set_classify(self, classify):
        self.classify = classify

    def set_classify_type(self, classify_type):
        self.classify_type = classify_type

    def set_question_type(self, question_type):
        self.question_type = question_type

    def set_is_user(self, is_user):
        self.is_user = is_user


class Projansmapresponse:
    id = None
    project_id = None
    type_id = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_project_id(self, project_id):
        self.project_id = project_id

    def set_type_id(self, type_id):
        self.type_id = type_id


class Questionansmapresponse:
    id = None
    text = None
    input_type = None
    order = None
    sub_option=None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id
    def set_is_answer(self, is_answer):
        self.is_answer = is_answer

    def set_text(self, text):
        self.text = text

    def set_input_type(self, input_type):
        self.input_type = input_type

    def set_order(self,order):
        self.order = order

    def set_sub_option(self,q_id,obj):
        arr=[{"id":i.id,"order":i.order,"options":i.options }for i in obj if i.question_id==q_id]
        self.sub_option =arr


class AnswerEvaluatorresponse:
    id = None
    question_id,answer,option_type,option_id = None,None,None,None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_id(self,id):
        self.id = id
    def set_question_id(self,question_id):
        self.question_id = question_id
    def set_answer(self,answer):
        self.answer = answer
    def set_option_type(self,option_type):
        self.option_type = option_type
    def set_option_id(self,option_id):
        self.option_id = option_id
