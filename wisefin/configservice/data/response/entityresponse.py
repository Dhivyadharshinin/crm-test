import json


class EntityResponse:
    id = None
    name = None

    def __init__(self, entity_obj):
        self.id = entity_obj.id
        self.name = entity_obj.name

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
