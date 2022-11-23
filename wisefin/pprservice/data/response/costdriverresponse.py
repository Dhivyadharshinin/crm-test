import json


class CostDriverResponse:
    id = None
    code = None
    name = None
    parameter_name = None
    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_code(self, code):
        self.code = code

    def set_name(self, name):
        self.name = name

    def set_parameter_name(self, parameter_name):
        self.sector = parameter_name