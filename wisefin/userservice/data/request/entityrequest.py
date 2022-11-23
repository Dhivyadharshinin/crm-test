import json

class EntityRequest:
    id = None
    name=None
    namespace=None
    status=None
    def __init__(self, entity_obj):
        if 'id' in entity_obj:
            self.id = entity_obj['id']
        if 'name' in entity_obj:
            self.name = entity_obj['name']
        if 'namespace' in entity_obj:
            self.namespace = entity_obj['namespace']
        if 'status' in entity_obj:
            self.status = entity_obj['status']

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def get_id(self):
        return self.id
    def get_name(self):
        return self.name
    def get_namespace(self):
        return self.namespace
    def get_status(self):
        return self.status


