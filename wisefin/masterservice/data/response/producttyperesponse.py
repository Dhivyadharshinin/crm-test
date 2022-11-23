import json

from masterservice.data.response.productcategoryresponse import ProductcategoryResponse


class ProducttypeResponse:
        id = None
        code = None
        name = None
        productcategory = None


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

        def set_productcategory(self, pdtcat):
            productcat_res = ProductcategoryResponse()
            productcat_res.set_id(pdtcat.id)
            productcat_res.set_code(pdtcat.code)
            productcat_res.set_name(pdtcat.name)
            # productcat_res.set_client_id(pdtcat.client_id)
            productcat_res.set_isprodservice(pdtcat.isprodservice)
            productcat_res.set_stockimpact(pdtcat.stockimpact)
            self.productcategory=productcat_res

