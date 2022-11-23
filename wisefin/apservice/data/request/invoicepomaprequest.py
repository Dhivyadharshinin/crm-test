import json

class InvoicePOMAPRequest:
    id = None
    apinvoiceheader_id = None
    apinvoicedetail_id = None
    invoiceno = None
    pono = None
    podetailno = None
    grninwardno = None
    productcode = None
    invoicepo_qty = None
    invoicepo_capitalised = None

    def __init__(self,obj_apinv):
        if 'id' in obj_apinv:
            self.id=obj_apinv['id']
        if 'apinvoiceheader_id' in obj_apinv:
            self.apinvoiceheader_id = obj_apinv['apinvoiceheader_id']
        if 'apinvoicedetail_id' in obj_apinv:
            self.apinvoicedetail_id = obj_apinv['apinvoicedetail_id']
        if 'invoiceno' in obj_apinv:
            self.invoiceno = obj_apinv['invoiceno']
        if 'pono' in obj_apinv:
            self.pono = obj_apinv['pono']
        if 'podetailno' in obj_apinv:
            self.podetailno = obj_apinv['podetailno']
        if 'podetailno' in obj_apinv:
            self.podetailno = obj_apinv['podetailno']
        if 'grninwardno' in obj_apinv:
            self.grninwardno = obj_apinv['grninwardno']
        if 'productcode' in obj_apinv:
            self.productcode = obj_apinv['productcode']
        if 'invoicepo_qty' in obj_apinv:
            self.invoicepo_qty = obj_apinv['invoicepo_qty']
        if 'invoicepo_capitalised' in obj_apinv:
            self.invoicepo_capitalised = obj_apinv['invoicepo_capitalised']


    def get_id(self):
        return self.id
    def get_apinvoiceheader_id(self):
        return self.apinvoiceheader_id
    def get_apinvoicedetail_id(self):
        return self.apinvoicedetail_id
    def get_invoiceno(self):
        return self.invoiceno
    def get_pono(self):
        return self.pono
    def get_podetailno(self):
        return self.podetailno
    def get_grninwardno(self):
        return self.grninwardno
    def get_productcode(self):
        return self.productcode
    def get_invoicepo_qty(self):
        return self.invoicepo_qty
    def get_invoicepo_capitalised(self):
        return self.invoicepo_capitalised







