import json

class ProductcategoryRequest:
    id = None
    code = None
    name = None
    client_id = None
    isprodservice = None
    stockimpact = None
    status = None

    def __init__(self, productcat_obj):
        if 'id' in productcat_obj:
            self.id = productcat_obj['id']
        if 'code' in productcat_obj:
            self.code = productcat_obj['code']
        if 'name' in productcat_obj:
            self.name = productcat_obj['name']
        if 'client_id' in productcat_obj:
            self.client_id = productcat_obj['client_id']
        if 'isprodservice' in productcat_obj:
            self.isprodservice = productcat_obj['isprodservice']
        if 'stockimpact' in productcat_obj:
            self.stockimpact = productcat_obj['stockimpact']

        if 'status' in productcat_obj:
            self.status = productcat_obj['status']



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

    def get_id(self):
        return self.id
    def get_code(self):
        return self.code
    def get_name(self):
        return self.name

    def get_client_id(self):
        return self.client_id
    def get_isprodservice(self):
        return self.isprodservice

    def get_stockimpact(self):
        return self.stockimpact

    def get_status(self):
        return self.status




