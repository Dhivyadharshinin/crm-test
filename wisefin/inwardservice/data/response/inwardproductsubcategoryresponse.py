import json

from inwardservice.data.response.inwardproductcatresponse import ProductcategoryResponse


class ProductsubcategoryResponse:
        id = None
        code = None
        name = None
        remarks = None
        is_sys = None
        product = None

        def get(self):
            return json.dumps(self, default=lambda o: o.__dict__,
                              sort_keys=True, indent=4)

        def set_id(self, id):
            self.id = id

        def set_code(self, code):
            self.code = code

        def set_name(self, name):
            self.name = name

        def set_product(self, pdtcat):
            productcat_res = ProductcategoryResponse()
            productcat_res.set_id(pdtcat.id)
            productcat_res.set_code(pdtcat.code)
            productcat_res.set_name(pdtcat.name)
            productcat_res.set_remarks(pdtcat.remarks)
            productcat_res.set_is_sys(pdtcat.is_sys)
            self.product=productcat_res

        def set_remarks(self, remarks):
            self.remarks = remarks

        def set_is_sys(self, is_sys):
            self.is_sys = is_sys