import json


class SalaryComponentResponse:
    id = None
    code = None
    name = None
    type = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
    def set_id(self, id):
        self.id = id

    def set_code(self, code):
        self.code = code

    def set_name(self, name):
        self.name = str(name)

    def set_type(self, type):
        self.type = type

class SalaryLabelResponse:
    id = None
    code = None
    name = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_code(self, code):
        self.code = code

    def set_name(self, name):
        self.name = str(name)

class SalarystructureMappingResponse:
    id = None
    name = None
    salarycomponent = None
    salarylabel = None
    is_amount = None
    amount_value = None
    type = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_name(self, name):
        self.name = name

    def set_salarycomponent(self, salarycomponent):
        self.salarycomponent = salarycomponent

    def set_salarylabel(self, salarylabel):
        self.salarylabel = salarylabel

    def set_is_amount(self,is_amount):
        self.is_amount=is_amount

    def set_amount_value(self,amount_value):
        self.amount_value=str(amount_value)

    def set_type(self,type):
        self.type=type

class DetectionInfoResponse:
    id = None
    salarymapping = None
    from_month = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_salarymapping(self, salarymapping):
        self.salarymapping = salarymapping

    def set_from_month(self, from_month):
        self.from_month = from_month
