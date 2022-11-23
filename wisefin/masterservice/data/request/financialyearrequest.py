import json

class FinancialYearRequest:
    fin_year = None
    fin_month = None
    fin_year_from_period = None
    fin_year_to_period = None
    status = None
    id = None


    def __init__(self, fin_obj):
        if 'id' in fin_obj:
            self.id = fin_obj['id']
        if 'fin_year' in fin_obj:
            self.fin_year = fin_obj['fin_year']
        if 'fin_month' in fin_obj:
            self.fin_month = fin_obj['fin_month']
        if 'fin_year_from_period' in fin_obj:
            self.fin_year_from_period = fin_obj['fin_year_from_period']
        if 'fin_year_to_period' in fin_obj:
            self.fin_year_to_period = fin_obj['fin_year_to_period']
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

    def get_fin_year_from_period(self):
        return self.fin_year_from_period

    def get_fin_year_to_period(self):
        return self.fin_year_to_period

    def get_status(self):
        return self.status


