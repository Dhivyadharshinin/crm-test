import json

class CommodityProductMapResponse:
    id = None
    product = None
    commodity = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    # def set_product(self, product):
    #     self.product = product
    def set_product(self, product,arr):
        if product != None:
            for i in arr:
                if i['id'] == product:
                    self.product = i
                    break

    def set_commodity(self, commodity):
        self.commodity = commodity