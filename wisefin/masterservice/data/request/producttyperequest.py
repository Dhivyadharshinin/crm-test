import json

from masterservice.data.response.productcategoryresponse import ProductcategoryResponse

class ProductypeRequest:
    id = None
    code = None
    name = None
    status = None
    productcategory_id = None
    productcategory_code = None


    def __init__(self, prosubcat_obj):
        if 'id' in prosubcat_obj:
            self.id = prosubcat_obj['id']
        if 'code' in prosubcat_obj:
            self.code = prosubcat_obj['code']
        if 'name' in prosubcat_obj:
            self.name = prosubcat_obj['name']
        if 'status' in prosubcat_obj:
            self.status = prosubcat_obj['status']
        if 'productcategory_id' in prosubcat_obj:
            self.productcategory_id = prosubcat_obj['productcategory_id']
        if 'productcategory_code' in prosubcat_obj:
            self.productcategory_code = prosubcat_obj['productcategory_code']


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_code(self, code):
        self.code = code

    def set_name(self, name):
        self.name = name



    def set_productcategory_id(self, productcategory_id):
        self.productcategory_id = productcategory_id


    def get_id(self):
        return self.id

    def get_code(self):
        return self.code

    def get_name(self):
        return self.name

    def get_productcategory_id(self):
        return self.productcategory_id

    def get_productcategory_code(self):
        return self.productcategory_code


    def get_status(self):
        return self.status

