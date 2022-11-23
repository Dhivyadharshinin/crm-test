import json


class ProductcategoryResponse:
        id = None
        code = None
        name = None
        client_id = None
        isprodservice = None
        stockimpact = None


        def get(self):
            return json.dumps(self, default=lambda o: o.__dict__,
                              sort_keys=True, indent=4)

        def set_id(self, id):
            self.id = id

        def set_code(self, code):
            self.code = code

        def set_name(self, name):
            self.name = name

        def set_client_id(self, client_id):
            self.client_id = client_id

        def set_isprodservice(self, isprodservice):
            self.isprodservice = isprodservice

        def set_stockimpact(self, stockimpact):
            self.stockimpact = stockimpact
