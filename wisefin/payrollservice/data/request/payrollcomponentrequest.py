class SalaryComponentRequest:
    id = None
    code = None
    name = None
    type = None

    def __init__(self, payroll_data):
        if 'id' in payroll_data:
            self.id = payroll_data['id']
        if 'code' in payroll_data:
            self.code = payroll_data['code']
        if 'name' in payroll_data:
            self.name = payroll_data['name']
        if 'type' in payroll_data:
            self.type = payroll_data['type']


    def get_id(self):
        return self.id

    def get_code(self):
        return self.code

    def get_name(self):
        return self.name

    def get_type(self):
        return self.type


class SalaryLabelRequest:
    id = None
    code = None
    name = None
    def __init__(self, payroll_data):
        if 'id' in payroll_data:
            self.id = payroll_data['id']
        if 'code' in payroll_data:
            self.code = payroll_data['code']
        if 'name' in payroll_data:
            self.name = payroll_data['name']

    def get_id(self):
        return self.id

    def get_code(self):
        return self.code

    def get_name(self):
        return self.name


class SalarystructureMappingRequest:
    id = None
    name = None
    salarycomponent = None
    salarylabel = None
    is_amount = None
    amount_value = None
    type = None

    def __init__(self, payroll_data):
        if 'id' in payroll_data:
            self.id = payroll_data['id']
        if 'name' in payroll_data:
            self.name = payroll_data['name']
        if 'salarycomponent' in payroll_data:
            self.salarycomponent = payroll_data['salarycomponent']
        if 'salarylabel' in payroll_data:
            self.salarylabel = payroll_data['salarylabel']
        if 'is_amount' in payroll_data:
            self.is_amount = payroll_data['is_amount']
        if 'amount_value' in payroll_data:
            self.amount_value = payroll_data['amount_value']
        if 'type' in payroll_data:
            self.type = payroll_data['type']

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_salarycomponent(self):
        return self.salarycomponent

    def get_salarylabel(self):
        return self.salarylabel

    def get_is_amount(self):
        return self.is_amount

    def get_amount_value(self):
        return self.amount_value

    def get_type(self):
        return self.type

class DetectionInfoRequest:
    id = None
    salarymapping = None
    from_month = None
    def __init__(self, payroll_data):
        if 'id' in payroll_data:
            self.id = payroll_data['id']
        if 'salarymapping' in payroll_data:
            self.salarymapping = payroll_data['salarymapping']
        if 'from_month' in payroll_data:
            self.from_month = payroll_data['from_month']

    def get_id(self):
        return self.id

    def get_salarymapping(self):
        return self.salarymapping

    def get_from_month(self):
        return self.from_month

