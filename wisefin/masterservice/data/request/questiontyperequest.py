class QuestiontypeRequest:
    id, name, remarks,display_name,module_id = (None,)*5

    def __init__(self,user_obj):
        if 'id' in user_obj:
            self.id=user_obj['id']
        if 'name' in user_obj:
            self.name = user_obj['name']
        if 'remarks' in user_obj:
            self.remarks = user_obj['remarks']
        if 'display_name' in user_obj:
            self.display_name = user_obj['display_name']
        if 'module_id' in user_obj:
            self.module_id = user_obj['module_id']

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_remarks(self):
        return self.remarks

    def get_display_name(self):
        return self.display_name

    def get_module_id(self):
        return self.module_id