class EntityRequest:
    id = None
    name = None

    def __init__(self, entity_req):
        if 'id' in entity_req:
            self.id = entity_req['id']
        if 'name' in entity_req:
            self.name = entity_req['name']

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name
