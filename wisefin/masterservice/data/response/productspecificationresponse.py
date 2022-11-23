import json

class ProductSpecificationResponse:
    id = None
    productcategory = None
    templatename = None

    def get(self):
      return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)
    def set_id(self, id):
        self.id = id
    def set_productcategory_id(self,productcategory_id):
        self.productcategory = productcategory_id
    def set_templatename(self,templatename):
        self.templatename = templatename
class ProductSpecificationRes:
    product_cat_id=None
    template_name=None
    id=None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


    def set_id(self, id):
        self.id = id

    def set_product_cat_id(self, product_cat_id):
        self.product_cat_id = product_cat_id

    def set_template_name(self, template_name):
        self.template_name = template_name
