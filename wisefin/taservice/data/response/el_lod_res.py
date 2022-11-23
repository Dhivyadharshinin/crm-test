import json
class El_lod_res:
    elligible_amount= None
    no_of_days= None


    def set_no_of_days(self,no_of_days):
        self.no_of_days=no_of_days
    def set_elligible_amount(self,elligible_amount):
        self.elligible_amount=elligible_amount
    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)