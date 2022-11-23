class Quesansrequest:
    id = None
    question_id = None
    question_type = None
    answer = None
    option_type = None
    option_id = None
    ref_type = None
    ref_id = None
    is_user = 1
    classify_id = None

    def __init__(self,obj_ans):
        if 'id' in obj_ans:
            self.id=obj_ans['id']
        if 'question_id' in obj_ans:
            self.question_id = obj_ans['question_id']
        if 'question_type' in obj_ans:
            self.question_type = obj_ans['question_type']
        if 'answer' in obj_ans:
            self.answer = obj_ans['answer']
        if 'option_type' in obj_ans:
            self.option_type = obj_ans['option_type']
        if 'option_id' in obj_ans:
            self.option_id = obj_ans['option_id']
        if 'ref_type' in obj_ans:
            self.ref_type = obj_ans['ref_type']
        if 'ref_id' in obj_ans:
            self.ref_id = obj_ans['ref_id']
        if 'is_user' in obj_ans:
            self.is_user = obj_ans['is_user']
        if 'classify_id' in obj_ans:
            self.classify_id = obj_ans['classify_id']

    def get_id(self):
        return self.id
    def get_question_id(self):
        return self.question_id
    def get_question_type(self):
        return self.question_type
    def get_answer(self):
        return self.answer
    def get_option_type(self):
        return self.option_type
    def get_option_id(self):
        return self.option_id
    def get_ref_type(self):
        return self.ref_type
    def get_ref_id(self):
        return self.ref_id
    def get_is_user(self):
        return self.is_user
    def get_classify_id(self):
        return self.classify_id

class Quesansmaprequest:
    id = None
    answer_id = None
    type_id = None
    subtype_id = None
    reftype_id = None
    ref_id = None
    is_user = 1

    def __init__(self,obj_ans):
        if 'id' in obj_ans:
            self.id=obj_ans['id']
        if 'answer_id' in obj_ans:
            self.answer_id=obj_ans['answer_id']
        if 'type_id' in obj_ans:
            self.type_id=obj_ans['type_id']
        if 'subtype_id' in obj_ans:
            self.subtype_id=obj_ans['subtype_id']
        if 'reftype_id' in obj_ans:
            self.reftype_id=obj_ans['reftype_id']
        if 'ref_id' in obj_ans:
            self.ref_id=obj_ans['ref_id']
        if 'is_user' in obj_ans:
            self.is_user = obj_ans['is_user']

    def get_id(self):
        return self.id
    def get_answer_id(self):
        return self.answer_id
    def get_type_id(self):
        return self.type_id
    def get_subtype_id(self):
        return self.subtype_id
    def get_reftype_id(self):
        return self.reftype_id
    def get_ref_id(self):
        return self.ref_id
    def get_is_user(self):
        return self.is_user

class Answermaprequest:
    id = None
    answer_id = None
    ref_type = None
    ref_id = None
    comments = None
    score = None
    is_user = 1
    red_flag = False

    def __init__(self,obj_ans):
        if 'id' in obj_ans:
            self.id=obj_ans['id']
        if 'answer_id' in obj_ans:
            self.answer_id=obj_ans['answer_id']
        if 'ref_type' in obj_ans:
            self.ref_type = obj_ans['ref_type']
        if 'ref_id' in obj_ans:
            self.ref_id = obj_ans['ref_id']
        if 'comments' in obj_ans:
            self.comments = obj_ans['comments']
        if 'score' in obj_ans:
            self.score = obj_ans['score']
        if 'is_user' in obj_ans:
            self.is_user = obj_ans['is_user']
        if 'red_flag' in obj_ans:
            self.red_flag = obj_ans['red_flag']

    def get_id(self):
        return self.id
    def get_answer_id(self):
        return self.answer_id
    def get_ref_type(self):
        return self.ref_type
    def get_ref_id(self):
        return self.ref_id
    def get_comments(self):
        return self.comments
    def get_score(self):
        return self.score
    def get_is_user(self):
        return self.is_user
    def get_red_flag(self):
        return self.red_flag

class Quesclassifyrequest:
    id = None
    classify_id = None
    classify_type = None
    question_type = None
    is_user = 1

    def __init__(self,obj_ans):
        if 'id' in obj_ans:
            self.id=obj_ans['id']
        if 'classify_id' in obj_ans:
            self.classify_id=obj_ans['classify_id']
        if 'classify_type' in obj_ans:
            self.classify_type = obj_ans['classify_type']
        if 'question_type' in obj_ans:
            self.question_type = obj_ans['question_type']
        if 'is_user' in obj_ans:
            self.is_user = obj_ans['is_user']

    def get_id(self):
        return self.id
    def get_classify_id(self):
        return self.classify_id
    def get_classify_type(self):
        return self.classify_type
    def get_question_type(self):
        return self.question_type
    def get_is_user(self):
        return self.is_user

class Projansmaprequest:
    id = None
    project_id = None
    type_id = None

    def __init__(self,obj_ans):
        if 'id' in obj_ans:
            self.id=obj_ans['id']
        if 'project_id' in obj_ans:
            self.project_id=obj_ans['project_id']
        if 'type_id' in obj_ans:
            self.type_id = obj_ans['type_id']

    def get_id(self):
        return self.id
    def get_project_id(self):
        return self.project_id
    def get_type_id(self):
        return self.type_id
