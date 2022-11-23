import json

class FinancialQuartersResponse:
    fin_year = None
    fin_month = None
    fin_quarter_from_period = None
    fin_quarter_to_period = None
    status = None
    id = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id
    def set_status(self, status):
        self.status = status
    def set_fin_year(self, fin_year):
        self.fin_year = fin_year
    def set_fin_month(self, fin_month):
        self.fin_month = fin_month

    def set_fin_quarter_from_period(self, fin_quarter_from_period):
        self.fin_quarter_from_period = fin_quarter_from_period

    def set_fin_quarter_to_period(self, fin_quarter_to_period):
        self.fin_quarter_to_period = fin_quarter_to_period



