import json


class NwisefinSearch:
    id = None
    name = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def __init__(self):
        pass

    def __int__(self, id, name):
        self.id = id
        self.name = name

    def set_id(self, id):
        self.id = id

    def set_name(self, name):
        self.name = name

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name