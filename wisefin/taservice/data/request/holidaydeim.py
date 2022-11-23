class Holidaydeim_req:
    id= None
    salarygrade= None
    city= None
    amount= None
    applicableto=None
    entity=1



    def __init__(self,hol_obj):
        if 'id' in hol_obj:
            self.id=hol_obj['id']
        if 'salarygrade' in hol_obj:
            self.salarygrade=hol_obj['salarygrade']
        if 'city' in hol_obj:
            self.city=hol_obj['city']
        if 'amount' in hol_obj:
            self.amount=hol_obj['amount']
        if 'applicableto' in hol_obj:
            self.applicableto=hol_obj['applicableto']
        if 'entity' in hol_obj:
            self.entity=hol_obj['entity']


    def get_id(self):
        return self.id
    def get_salarygrade(self):
        return self.salarygrade
    def get_city(self):
        return self.city
    def get_amount(self):
        return self.amount
    def get_applicableto(self):
        return self.applicableto
    def get_entity(self):
        return self.entity

