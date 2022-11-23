import json

# from masterservice.service.questionheaderservice import QuestionheaderService
# from masterservice.service.questiontypeservice import QuestiontypeService
from masterservice.util.masterutil import input_type_val


class QuestionResponse:
    id, text, header_id, type_id, input_type, order, is_subtext, sub_options, group_id, ref_id, is_score, min, max ,question_mapping_id= (None,) * 14

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_question_mapping_id(self, id):
        self.question_mapping_id = id

    def set_text(self, text):
        self.text = text

    def set_header_id(self, header_id, arr):
        self.header_id = None
        for i in arr:
            if i.id == header_id:
                self.header_id = i
                break
        # question_header_serv = QuestionheaderService(scope)
        # type_obj = question_header_serv.get_question_header(header_id)
        # self.header_id = type_obj

    def set_type_id(self, type_id,arr):
        self.type_id = None
        for i in arr:
            if i.id == type_id:
                self.type_id = i
                break
        # questiontype_serv = QuestiontypeService(scope)
        # type_obj = questiontype_serv.get_question_type(type_id)
        # self.type_id = type_obj

    def set_input_type(self, input_type):
        input_type = input_type_val(input_type)
        self.input_type = input_type

    def set_order(self, order):
        self.order = order


    def set_sub_options(self, sub_options):
        self.sub_question = sub_options


    def set_type(self,type):
        self.type_id = type
        
    def set_header(self,header):
        self.header_id = header
        
    def set_group_id(self,group_id):
        self.group_id=group_id

    def set_ref_id(self, ref_id):
        self.ref_id = ref_id
    def set_input_value(self, input_value):
        self.Input_value = input_value

    def set_is_score(self, is_score):
        self.is_score = is_score

    def set_min(self, min):
        self.min = min

    def set_max(self, max):
        self.max = max

class ActivityResponse:
    id, name, code, description= (None,) * 4

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_name(self, text):
        self.name = text
    def set_code(self, text):
        self.code = text
    def set_description(self, text):
        self.description = text


