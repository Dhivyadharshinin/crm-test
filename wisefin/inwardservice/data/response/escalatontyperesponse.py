import json


class EscalationTypeResponse:
    id = None
    name = None
    code = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_name(self, name):
        self.name = name

    def set_code(self, code):
        self.code = code

class EscalationSubTypeResponse:
    id = None
    name = None
    code = None
    escalationtype=None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id
    def set_name(self, name):
        self.name = name
    def set_code(self, code):
        self.code = code
    def set_escalationtype(self, escalationtype):
        self.escalationtype = escalationtype

