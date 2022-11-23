
import json

class ppxliquidationrequest:
    id = None
    credit = None
    ppx_number = None
    ppx_amount = None
    amount = None
    ecf_number = None

    def __init__(self,obj_liquid):
        if 'id' in obj_liquid:
            self.id=obj_liquid['id']
        if 'credit_id' in obj_liquid:
            self.credit=obj_liquid['credit_id']
        if 'ppx_number' in obj_liquid:
            self.ppx_number=obj_liquid['ppx_number']
        if 'ppx_amount' in obj_liquid:
            self.ppx_amount=obj_liquid['ppx_amount']
        if 'amount' in obj_liquid:
            self.amount=obj_liquid['amount']
        if 'ecf_number' in obj_liquid:
            self.ecf_number=obj_liquid['ecf_number']

    def get_id(self):
        return self.id
    def get_credit_id(self):
        return self.credit
    def get_ppx_number(self):
        return self.ppx_number
    def get_ppx_amount(self):
        return self.ppx_amount
    def get_amount(self):
        return self.amount
    def get_ecf_number(self):
        return self.ecf_number