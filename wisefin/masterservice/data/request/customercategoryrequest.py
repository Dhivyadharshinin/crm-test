import json


class CustomerCategoryRequest:
    id = None
    code = None
    name = None

    def __init__(self, country_obj):
        if 'id' in country_obj:
            self.id = country_obj['id']
        if 'code' in country_obj:
            self.code = country_obj['code']
        if 'name' in country_obj:
            self.name = country_obj['name']

    def get_id(self):
        return self.id

    def get_code(self):
        return self.code

    def get_name(self):
        return self.name
