import json


class TaxResponse:
    id = None
    payable = None
    code = None
    name = None
    receivable = None
    status = None
    glno =None


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_code(self, code):
        self.code = code

    def set_name(self, name):
        self.name = name
        
    def set_payable(self, payable):
        self.payable = payable
        
    def set_receivable(self, receivable):
        self.receivable = receivable

    def set_glno(self,glno):
        self.glno = glno
