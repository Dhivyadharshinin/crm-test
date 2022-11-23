import json


class PaymodedetailResponse:
    id = None
    glno = None
    name = None
    category = None
    sub_category = None
    paymode = None
    status = None


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_glno(self, glno):
        self.glno = glno

    def set_name(self, name):
        self.name = name

    def set_status(self,status):
        self.status = status

    def set_category(self, category_id):
        self.category_id = category_id

    def set_sub_category(self, sub_category_id):
        self.sub_category_id = sub_category_id

    def set_paymode(self, paymode_id):
        self.paymode_id = paymode_id


