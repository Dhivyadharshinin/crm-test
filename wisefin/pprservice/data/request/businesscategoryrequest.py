import json
class BusinessCategoryRequest:
    id = None
    code = None
    name = None
    sector_id = None

    def __init__(self, categeory_obj):
        if 'id' in categeory_obj:
            self.id = categeory_obj['id']
        if 'code' in categeory_obj:
            self.code = categeory_obj['code']
        if 'name' in categeory_obj:
            self.name = categeory_obj['name']
        if 'sector_id' in categeory_obj:
            self.sector_id = categeory_obj['sector_id']

    def get_id(self):
        return self.id
    def get_code(self):
        return self.code
    def get_name(self):
        return self.name
    def get_sector_id(self):
        return self.sector_id
