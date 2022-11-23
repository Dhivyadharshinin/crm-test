import json


class TaxRequest:
    id = None
    payable = None
    code = None
    name = None
    receivable = None
    glno = None
    

    def __init__(self, tax_obj):
        if 'id' in tax_obj:
            self.id = tax_obj['id']
        if 'payable' in tax_obj:
            self.payable = tax_obj['payable']
        if 'code' in tax_obj:
            self.code = tax_obj['code']
        if 'name' in tax_obj:
            self.name = tax_obj['name']
        if 'receivable' in tax_obj:
            self.receivable = tax_obj['receivable']
        if 'glno' in tax_obj:
            self.glno = tax_obj['glno']

    def get_id(self):
        return self.id

    def get_code(self):
        return self.code

    def get_name(self):
        return self.name
    
    def get_payable(self):
        return self.payable
    
    def get_receivable(self):
        return self.receivable
    
    def get_glno(self):
        return self.glno

