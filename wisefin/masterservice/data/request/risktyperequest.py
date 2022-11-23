class RiskTypeRequest:
    id = None
    code = None
    name = None
    status = 1

    def __init__(self, risk_type_obj):
        if 'id' in risk_type_obj:
            self.id = risk_type_obj['id']
        if 'code' in risk_type_obj:
            self.code = risk_type_obj['code']
        if 'name' in risk_type_obj:
            self.name = risk_type_obj['name']
        if 'status' in risk_type_obj:
            self.status = risk_type_obj['status']

    def get_id(self):
        return self.id

    def get_code(self):
        return self.code

    def get_name(self):
        return self.name

    def get_status(self):
        return self.status
