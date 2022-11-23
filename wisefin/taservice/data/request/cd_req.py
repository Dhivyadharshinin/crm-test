class Cd_req:
    name= None
    entity = 1
    code=None
    id=None
    status=1


    def __init__(self,obj):
        if 'id' in obj:
            self.id=obj['id']
        if 'name' in obj:
            self.name=obj['name']
        if 'entity' in obj:
            self.entity=obj['entity']
        if 'code' in obj:
            self.code=obj['code']
        if 'status' in obj:
            self.status=obj['status']


    def get_id(self):
        return self.id
    def get_name(self):
        return self.name
    def get_entity(self):
        return self.entity
    def get_code(self):
        return self.code

class Cd_del_req:
    name= None
    entity = 1
    common_drop_down_id = None
    value = None
    code=None
    id=None
    status=1


    def __init__(self,obj):
        if 'id' in obj:
            self.id=obj['id']
        if 'name' in obj:
            self.name=obj['name']
        if 'new_name' in obj:
            self.new_name=obj['new_name']
        if 'common_drop_down_id' in obj:
            self.common_drop_down_id=obj['common_drop_down_id']
        if 'reason' in obj:
            self.reason=obj['reason']
        if 'entity' in obj:
            self.entity=obj['entity']
        if 'code' in obj:
            self.code=obj['code']
        if 'value' in obj:
            self.value=obj['value']
        if 'status' in obj:
            self.status=obj['status']


    def get_id(self):
        return self.id
    def get_name(self):
        return self.name
    def get_new_name(self):
        return self.new_name
    def get_common_drop_down_id(self):
        return self.common_drop_down_id
    def get_value(self):
        return self.value
    def get_entity(self):
        return self.entity
    def get_code(self):
        return self.code


