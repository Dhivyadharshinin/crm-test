import json
class BusinessSubCategoryRequest:
    id = None
    code = None
    name = None
    businesscategory = None

    def __init__(self, subcategeory_obj):
        if 'id' in subcategeory_obj:
            self.id = subcategeory_obj['id']
        if 'code' in subcategeory_obj:
            self.code = subcategeory_obj['code']
        if 'name' in subcategeory_obj:
            self.name = subcategeory_obj['name']
        if 'businesscategory' in subcategeory_obj:
            self.businesscategory = subcategeory_obj['businesscategory']

    def get_id(self):
        return self.id
    def get_code(self):
        return self.code
    def get_name(self):
        return self.name
    def get_businesscategory(self):
        return self.businesscategory
