import json


class NWisefinUser:
    id = None
    username = None
    first_name = None
    last_name = None
    email = None
    is_active = None
    full_name = None
    designation = None
    name = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_username(self, username):
        self.username = username

    def set_first_name(self, first_name):
        self.first_name = first_name

    def set_last_name(self, last_name):
        self.last_name = last_name

    def set_email(self, email):
        self.email = email

    def set_is_active(self, is_active):
        self.is_active = is_active

    def set_designation(self,designation):
        self.designation=designation

    def get_id(self):
        return self.id

    def get_username(self):
        return self.username

    def get_first_name(self):
        return self.first_name

    def get_last_name(self):
        return self.last_name

    def get_email(self):
        return self.email

    def get_is_active(self):
        return self.is_active

    def set_full_name(self, full_name):
        self.full_name = full_name

    def get_full_name(self):
        return self.full_name

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def get_designation(self):
        return self.designation
