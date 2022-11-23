import json


class AssetDebitResponse:

    id = assetdetails_id =  category_id =  subcategory_id =  glno =  amount = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id
    def set_assetdetails_id(self, assetdetails_id):
        self.assetdetails_id = assetdetails_id
    def set_category_id(self, category_id):
        self.category_id = category_id
    def set_subcategory_id(self, subcategory_id):
        self.subcategory_id =subcategory_id
    def set_glno(self, glno):
        self.glno = glno
    def set_amount(self, amount):
        self.amount =str(amount)


