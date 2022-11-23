
import json

from masterservice.util.masterutil import input_type_val


class QuestionsubResponse:
    id, options, question_id, order, input_type = (None,)*5

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


    def set_id(self,id):
        self.id = str(id)

    def set_options(self, options):
        self.options = options

    def set_question_id(self, question_id):
        # question_serv = QuestionService(scope)
        # question_type = question_serv.get_question(question_id)
        self.question_id = question_id

    def set_order(self, order):
        self.order = order

    def set_input_type(self, input_type):
        input_type = input_type_val(input_type)
        self.input_type = input_type

    def set_input_value(self, input_value):
        self.input_type = input_value

