import json
class CostDriverRequest:
    id = None
    code = None
    name = None
    parameter_name = None

    def __init__(self, costdriver_obj):
        if 'id' in costdriver_obj:
            self.id = costdriver_obj['id']
        if 'code' in costdriver_obj:
            self.code = costdriver_obj['code']
        if 'name' in costdriver_obj:
            self.name = costdriver_obj['name']
        if 'parameter_name' in costdriver_obj:
            self.parameter_name = costdriver_obj['parameter_name']

    def get_id(self):
        return self.id
    def get_code(self):
        return self.code
    def get_name(self):
        return self.name
    def get_parameter_name(self):
        return self.parameter_name
