class Cmsquestiontyperequest:
    id = None
    question_type_id = None
    vendor_id = None
    cat_id = None
    subcat_id = None
    group_id = None

    def __init__(self,obj_ans):
        if 'id' in obj_ans:
            self.id=obj_ans['id']
        if 'question_type_id' in obj_ans:
            self.question_type_id=obj_ans['question_type_id']
        if 'vendor_id' in obj_ans:
            self.vendor_id=obj_ans['vendor_id']
        if 'cat_id' in obj_ans:
            self.cat_id=obj_ans['cat_id']
        if 'subcat_id' in obj_ans:
            self.subcat_id=obj_ans['subcat_id']
        if 'group_id' in obj_ans:
            self.group_id=obj_ans['group_id']

    def get_id(self):
        return self.id
    def get_question_type_id(self):
        return self.question_type_id
    def get_vendor_id(self):
        return self.vendor_id
    def get_cat_id(self):
        return self.cat_id
    def get_subcat_id(self):
        return self.subcat_id
    def get_group_id(self):
        return self.group_id

class Cmsquestypemaprequest:
    id = None
    question_id = None
    mapping_id = None

    def __init__(self,obj_ans):
        if 'id' in obj_ans:
            self.id=obj_ans['id']
        if 'question_id' in obj_ans:
            self.question_id=obj_ans['question_id']
        if 'mapping_id' in obj_ans:
            self.mapping_id=obj_ans['mapping_id']

    def get_id(self):
        return self.id
    def get_question_id(self):
        return self.question_id
    def get_mapping_id(self):
        return self.mapping_id