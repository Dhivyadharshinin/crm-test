import json


class NWisefinError:
    code = None
    description = None
    errorcode = None

    def __init__(self):
        pass

    def set_code(self, code):
        self.code = code

    def error_code(self, errorcode):
        self.errorcode = errorcode

    def set_description(self, description):
        self.description = description

    def get_code(self):
        return self.code

    def get_description(self):
        return self.description

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


