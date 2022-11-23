import json
class Holidaydeim_resp:
    id= None
    salarygrade= None
    city= None
    amount= None
    applicableto=None
    status=None
    entity=1
    created_by=None
    created_date=None
    updated_by=None
    updated_date=None

    def set_id(self,id):
        self.id=id
    def set_salarygrade(self,salarygrade):
        self.salarygrade=salarygrade
    def set_city(self,city):
        self.city=city
    def set_amount(self,amount):
        self.amount=amount
    def set_applicableto(self,applicableto):
        self.applicableto=applicableto
    def set_status(self,status):
        self.status=status
    def set_entity(self,entity):
        self.entity=entity
    def set_created_by(self,created_by):
        self.created_by=created_by
    def set_updated_by(self,updated_by):
        self.updated_by=updated_by

    def set_created_date(self,created_date):
        self.created_date=created_date.strftime("%d-%b-%Y")
        self.created_date_ms =round(created_date.timestamp() * 1000)
    def set_updated_date(self,updated_date):
        self.updated_date=updated_date.strftime("%d-%b-%Y")
        self.updated_date_ms =round(updated_date.timestamp() * 1000)

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)


