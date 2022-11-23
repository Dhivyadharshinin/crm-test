import json

class ProductsubcategoryRequest:
    id = None
    product_id = None
    code = None
    name = None
    remarks = None
    status = None
    is_sys = False

    def __init__(self, prosubcat_obj):
        if 'id' in prosubcat_obj:
            self.id = prosubcat_obj['id']
        if 'product_id' in prosubcat_obj:
            self.product_id = prosubcat_obj['product_id']
        if 'code' in prosubcat_obj:
            self.code = prosubcat_obj['code']
        if 'name' in prosubcat_obj:
            self.name = prosubcat_obj['name']
        if 'remarks' in prosubcat_obj:
            self.remarks = prosubcat_obj['remarks']
        if 'status' in prosubcat_obj:
            self.status = prosubcat_obj['status']
        if 'is_sys' in prosubcat_obj:
            self.is_sys = prosubcat_obj['is_sys']

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_product_id(self, product_id):
        self.product_id = product_id

    def set_code(self, code):
        self.code = code

    def set_name(self, name):
        self.name = name

    def set_remarks(self, remarks):
        self.remarks = remarks

    def set_status(self, status):
        self.status = status

    def set_is_sys(self, is_sys):
        self.is_sys = is_sys

    # product,code,name,remarks,status,is_sys
    def get_id(self):
        return self.id

    def get_product_id(self):
        return self.product_id

    def get_code(self):
        return self.code

    def get_name(self):
        return self.name

    def get_remarks(self):
        return self.remarks

    def get_status(self):
        return self.status

    def get_is_sys(self):
        return self.is_sys