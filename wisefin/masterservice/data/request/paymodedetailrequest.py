import json

class PaymodedetailRequest:
    id = None
    glno = None
    name = None
    category = None
    sub_category = None
    paymode = None
    status=None

    def __init__(self, paymodedetail_obj):
        if 'id' in paymodedetail_obj:
            self.id = paymodedetail_obj['id']
        if 'status' in paymodedetail_obj:
            self.status = paymodedetail_obj['status']
        if 'glno' in paymodedetail_obj:
            self.glno = paymodedetail_obj['glno']
        if 'name' in paymodedetail_obj:
            self.name = paymodedetail_obj['name']
        if 'category_id' in paymodedetail_obj:
            self.category_id = paymodedetail_obj['category_id']
        if 'sub_category_id' in paymodedetail_obj:
            self.sub_category_id = paymodedetail_obj['sub_category_id']
        if 'paymode_id' in paymodedetail_obj:
            self.paymode_id = paymodedetail_obj['paymode_id']

    def get_id(self):
        return self.id
    def get_glno(self):
        return self.glno
    def get_name(self):
        return self.name
    def get_category_id(self):
        return self.category_id
    def get_sub_category_id(self):
        return self.sub_category_id
    def get_paymode_id(self):
        return self.paymode_id
    def get_paymode_status(self):
        return self.status