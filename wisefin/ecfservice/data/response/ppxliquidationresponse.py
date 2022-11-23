
import json

class ppxliquidationresponse:
    id = None
    credit = None
    ppx_number = None
    ppx_amount = None
    amount = None
    ecf_number = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_id(self,id):
        self.id = id
    def set_credit_id(self,credit_id):
        self.credit = credit_id
    def set_ppx_number(self,ppx_number):
        self.ppx_number = ppx_number
    def set_ppx_amount(self,ppx_amount):
        self.ppx_amount = ppx_amount
    def set_amount(self,amount):
        self.amount = amount
    def set_ecf_number(self,ecf_number):
        self.ecf_number = ecf_number
