import json

class ApExpenseGrouprequest:
    id = None
    name = None
    description = None
    status=None

    def __init__(self,sector_obj):
        if 'id' in sector_obj:
            self.id = sector_obj['id']
        if 'name' in sector_obj:
            self.name = sector_obj['name']
        if 'status' in sector_obj:
            self.status = sector_obj['status']
        if 'description' in sector_obj:
            self.description = sector_obj['description']


    def get_id(self):
        return self.id
    def get_name(self):
        return self.name
    def get_description(self):
        return self.description