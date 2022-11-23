import json

class FinancialQuartersRequest:
    fin_year = None
    fin_month = None
    finquarter_from_period = None
    finquarter_to_period = None
    status = None
    id = None


    def __init__(self, fin_obj):
        if 'id' in fin_obj:
            self.id = fin_obj['id']
        if 'fin_year' in fin_obj:
            self.fin_year = fin_obj['fin_year']
        if 'fin_month' in fin_obj:
            self.fin_month = fin_obj['fin_month']
        if 'finquarter_from_period' in fin_obj:
            self.finquarter_from_period = fin_obj['finquarter_from_period']
        if 'finquarter_to_period' in fin_obj:
            self.finyear_period = fin_obj['finquarter_to_period']
        if 'status' in fin_obj:
            self.status = fin_obj['status']


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def get_id(self):
        return self.id

    def get_fin_year(self):
        return self.fin_year

    def get_fin_month(self):
        return self.fin_month

    def get_finquarter_from_period(self):
        return self.finquarter_from_period

    def get_finquarter_to_period(self):
        return self.finquarter_to_period
