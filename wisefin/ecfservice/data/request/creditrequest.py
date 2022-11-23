import json

class Creditrequest:
    id = None
    invoiceheader = None
    paymode_id = None
    creditbank_id = None
    suppliertax_id = None
    creditglno = None
    creditrefno = None
    suppliertaxtype = None
    suppliertaxrate = None
    taxexcempted = None
    amount = None
    taxableamount = None
    ddtranbranch = None
    ddpaybranch = None
    category_code = None
    subcategory_code = None
    credittotal = None

    def __init__(self,obj_crd):
        if 'id' in obj_crd:
            self.id=obj_crd['id']
        if 'invoiceheader_id' in obj_crd:
            self.invoiceheader=obj_crd['invoiceheader_id']
        if 'paymode_id' in obj_crd:
            self.paymode_id=obj_crd['paymode_id']
        if 'creditbank_id' in obj_crd:
            self.creditbank_id=obj_crd['creditbank_id']
        if 'suppliertax_id' in obj_crd:
            self.suppliertax_id=obj_crd['suppliertax_id']
        if 'creditglno' in obj_crd:
            self.creditglno=obj_crd['creditglno']
        if 'creditrefno' in obj_crd:
            self.creditrefno=obj_crd['creditrefno']
        if 'suppliertaxtype' in obj_crd:
            self.suppliertaxtype=obj_crd['suppliertaxtype']
        if 'suppliertaxrate' in obj_crd:
            self.suppliertaxrate=obj_crd['suppliertaxrate']
        if 'taxexcempted' in obj_crd:
            self.taxexcempted=obj_crd['taxexcempted']
        if 'amount' in obj_crd:
            self.amount=obj_crd['amount']
        if 'taxableamount' in obj_crd:
            self.taxableamount=obj_crd['taxableamount']
        if 'ddtranbranch' in obj_crd:
            self.ddtranbranch=obj_crd['ddtranbranch']
        if 'ddpaybranch' in obj_crd:
            self.ddpaybranch=obj_crd['ddpaybranch']
        if 'subcategory_code' in obj_crd:
            self.subcategory_code=obj_crd['subcategory_code']
        if 'category_code' in obj_crd:
            self.category_code=obj_crd['category_code']
        if 'credittotal' in obj_crd:
            self.credittotal=obj_crd['credittotal']


    def get_id(self):
        return self.id
    def get_invoiceheader_id(self):
        return self.invoiceheader
    def get_paymode_id(self):
        return self.paymode_id
    def get_creditbank_id(self):
        return self.creditbank_id
    def get_suppliertax_id(self):
        return self.suppliertax_id
    def get_creditglno(self):
        return self.creditglno
    def get_creditrefno(self):
        return self.creditrefno
    def get_suppliertaxtype(self):
        return self.suppliertaxtype
    def get_suppliertaxrate(self):
        return self.suppliertaxrate
    def get_taxexcempted(self):
        return self.taxexcempted
    def get_amount(self):
        return self.amount
    def get_taxableamount(self):
        return self.taxableamount
    def get_ddtranbranch(self):
        return self.ddtranbranch
    def get_ddpaybranch(self):
        return self.ddpaybranch
    def get_category_code(self):
        return self.category_code
    def get_subcategory_code(self):
        return self.subcategory_code
    def get_credittotal(self):
        return self.credittotal
