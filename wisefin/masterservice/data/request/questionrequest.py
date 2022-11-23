class QuestionRequest:
    id, text, header_id, type_id, input_type, order, is_subtext, ref_id, min, max, is_score = (None,) *11

    def __init__(self, user_obj):
        if 'id' in user_obj:
            self.id = user_obj['id']
        if 'text' in user_obj:
            self.text = user_obj['text']
        if 'header_id' in user_obj:
            self.header_id = user_obj['header_id']
        if 'type_id' in user_obj:
            self.type_id = user_obj['type_id']
        if 'input_type' in user_obj:
            self.input_type = user_obj['input_type']
        if 'order' in user_obj:
            self.order = user_obj['order']
        if 'is_subtext' in user_obj:
            self.is_subtext = user_obj['is_subtext']
        if 'is_score' in user_obj:
            if user_obj['is_score'] != '':
                self.is_score = user_obj['is_score']
        if 'min' in user_obj:
            self.min = user_obj['min']
        if 'max' in user_obj:
            self.max = user_obj['max']



    def get_id(self):
        return self.id

    def get_text(self):
        return self.text

    def get_header_id(self):
        return self.header_id

    def get_type_id(self):
        return self.type_id

    def get_input_type(self):
        return self.input_type

    def get_order(self):
        return self.order

    def get_is_subtext(self):
        return self.is_subtext

    def get_ref_id(self):
        return self.ref_id

    def get_is_score(self):
        return self.is_score

    def get_min(self):
        return self.min

    def get_max(self):
        return self.max

class ActivityRequest:
    id, name, code,description = (None,) * 4

    def __init__(self, user_obj):
        if 'id' in user_obj:
            self.id = user_obj['id']
        if 'name' in user_obj:
            self.name = user_obj['name']
        if 'code' in user_obj:
            self.code = user_obj['code']
        if 'description' in user_obj:
            self.description = user_obj['description']


    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_code(self):
        return self.code

    def get_description(self):
        return self.description


