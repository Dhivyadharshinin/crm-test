import json


class ModificationDataResponse:
    id = None
    type_name= None
    action = None
    old_data = None
    new_data = None
    data = None


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_type_name(self, type_name):
        self.type_name = type_name

    def set_action(self, action):
        self.action = action

    def set_old_data(self, old_data):
        self.old_data = old_data

    def set_new_data(self, new_data):
        self.new_data = new_data

    def set_data(self, data):
        self.data = data



