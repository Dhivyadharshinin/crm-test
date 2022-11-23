import json


class CommodityRequest:
    id = None
    code = None
    name = None
    description = None
    status = None


    def __init__(self, commodity_obj):
        if 'id' in commodity_obj:
            self.id = commodity_obj['id']
        if 'code' in commodity_obj:
            self.code = commodity_obj['code']
        if 'name' in commodity_obj:
            self.name = commodity_obj['name']
        if 'description' in commodity_obj:
            self.description = commodity_obj['description']
        if 'status' in commodity_obj:
            self.status = commodity_obj['status']

    def get_id(self):
        return self.id
    def get_code(self):
        return self.code
    def get_name(self):
        return self.name
    def get_description(self):
        return self.description
    def get_status(self):
        return self.status
