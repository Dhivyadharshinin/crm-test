import json


class AuthData:
    token: None
    user_id: None
    name: None
    code: None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_token(self, token):
        self.token = token

    def set_user_id(self, user_id):
        self.user_id = user_id

    def get_token(self):
        return self.token

    def get_user_id(self):
        return self.user_id

    def set_name(self, name):
        self.name = name

    def set_code(self, code):
        self.code = code

    def get_name(self):
        return self.name

    def get_code(self):
        return self.code


class MSAuthData:
    token: None
    user_id: None
    name : None
    code : None
    first_name : None
    is_active : None
    email : None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_token(self, token):
        self.token = token

    def set_user_id(self, user_id):
        self.user_id = user_id

    def set_first_name(self,first_name):
        self.first_name = first_name

    def set_date_joined(self, date_joined):
        date_joined = str(date_joined)
        self.date_joined = date_joined

    def set_is_active(self, is_active):
        self.is_active = is_active

    def set_email(self, email):
        self.email = email

    def get_token(self):
        return self.token

    def get_user_id(self):
        return self.user_id

    def set_name(self, name):
        self.name = name

    def set_code(self, code):
        self.code = code

    def get_name(self):
        return self.name

    def get_code(self):
        return self.code
