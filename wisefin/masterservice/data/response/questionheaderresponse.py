import json

from masterservice.service.questiontypeservice import QuestiontypeService
from masterservice.util.masterutil import input_type_val
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


class QuestionheaderResponse:
    id, name, type_id, slno, order, is_input, input_type,question= (None,)* 8


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_name(self, name):
        self.name = name

    def set_slno(self, slno):
        self.slno = slno

    def set_order(self, order):
        self.order = order

    def set_is_input(self, is_input):
        self.is_input = is_input

    def set_input_type(self, input_type):
        input_type = input_type_val(input_type)
        self.input_type = input_type

    def set_type_id(self, type_id,arr):
        self.type_id = None
        for i in arr:
            if i.id == type_id:
                self.type_id = i
                break
        # type_serv = QuestiontypeService(scope)
        # type_obj = type_serv.get_question_type(type_id)
        # self.type_id = type_id

    def set_question(self, question):
        self.question = question

    def set_type(self,type):
        self.type = type