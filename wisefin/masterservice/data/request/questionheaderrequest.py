class QuestionheaderRequest:
    id, name, type_id, slno, order, is_input, input_type = (None,) * 7

    def __init__(self,user_obj):
        if 'id' in user_obj:
            self.id = user_obj['id']
        if 'name' in user_obj:
            self.name = user_obj['name']
        if 'type_id' in user_obj:
            self.type_id = user_obj['type_id']
        if 'slno' in user_obj:
            self.slno = user_obj['slno']
        if 'order' in user_obj:
            self.order = user_obj['order']
        if 'is_input' in user_obj:
            self.is_input = user_obj['is_input']
        if 'input_type' in user_obj:
            if user_obj['input_type']!='':
                self.input_type = user_obj['input_type']


    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_type_id(self):
        return self.type_id

    def get_slno(self):
        return self.slno

    def get_order(self):
        return self.order

    def get_is_input(self):
        return self.is_input

    def get_input_type(self):
        return self.input_type