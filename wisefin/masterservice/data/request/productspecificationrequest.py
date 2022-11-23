import json
class ProductSpecificationRequest:
    id = None
    productcategory = None
    templatename = None
    productcategory_code = None


    def __init__(self, productspec_obj):
        if 'id' in productspec_obj:
            self.id = productspec_obj['id']
        if 'productcategory_id' in  productspec_obj:
            self.productcategory = productspec_obj['productcategory_id']
        if 'templatename' in productspec_obj:
            self.templatename = productspec_obj['templatename']
        if 'productcategory_code' in productspec_obj:
            self.productcategory_code = productspec_obj['productcategory_code']



    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
    def get_id(self):
        return self.id
    def get_productcategory_id(self):
        return self.productcategory
    def get_templatename(self):
        return self.templatename
    def get_productcategory_code(self):
        return self.productcategory_code