import json


class UserData:
    id = None
    username = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def get_id(self):
        return self.id

    def set_username(self, username):
        self.username = username

    def get_username(self):
        return self.username