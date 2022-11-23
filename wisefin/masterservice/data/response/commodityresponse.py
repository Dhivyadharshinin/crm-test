import json


class CommodityResponse:
    id = None
    code = None
    name = None
    description = None
    status = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_code(self, code):
        self.code = code

    def set_name(self, name):
        self.name = name

    def set_description(self, description):
        self.description = description

    def set_status(self, status):
        self.status = status


class CommodityProductMapResponse:
    id = None
    product = None
    commodity = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id
    def set_product(self, product ):
         self.product= product
    def set_commodity(self, commodity):
        self.commodity = commodity