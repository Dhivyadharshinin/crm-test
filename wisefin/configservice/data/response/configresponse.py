import json


class SchemaResponse:
    id = None
    name = None

    def __init__(self, schema):
        self.id = schema.id
        self.name = schema.name

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                              sort_keys=True, indent=4)