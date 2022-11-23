import json

class Invoiceporequest:
    id = None
    invoiceheader = None
    invoicedetail = None
    ponumber = None
    grnnumber = None
    grndate = None
    poquantity = None
    receivedqty = None
    balanceqty = None
    receiveddate = None
    created_by = None
    pototalamt=None
    product_code = None
    invoicedqty = None
    invoiceqty = None

    def __init__(self,obj_invpo):
        if 'id' in obj_invpo:
            self.id=obj_invpo['id']
        if 'invoiceheader_id' in obj_invpo:
            self.invoiceheader=obj_invpo['invoiceheader_id']
        if 'invoicedetail_id' in obj_invpo:
            self.invoicedetail=obj_invpo['invoicedetail_id']
        if 'ponumber' in obj_invpo:
            self.ponumber=obj_invpo['ponumber']
        if 'poquantity' in obj_invpo:
            self.poquantity=obj_invpo['poquantity']
        if 'grndate' in obj_invpo:
            self.grndate=obj_invpo['grndate']
        if 'grnnumber' in obj_invpo:
            self.grnnumber=obj_invpo['grnnumber']
        if 'receivedqty' in obj_invpo:
            self.receivedqty=obj_invpo['receivedqty']
        if 'balanceqty' in obj_invpo:
            self.balanceqty=obj_invpo['balanceqty']
        if 'receiveddate' in obj_invpo:
            self.receiveddate=obj_invpo['receiveddate']
        if 'created_by' in obj_invpo:
            self.created_by = obj_invpo['created_by']
        if 'pototalamt' in obj_invpo:
            self.pototalamt = obj_invpo['pototalamt']
        if 'product_code' in obj_invpo:
            self.product_code = obj_invpo['product_code']
        if 'invoicedqty' in obj_invpo:
            self.invoicedqty = obj_invpo['invoicedqty']
        if 'invoiceqty' in obj_invpo:
            self.invoiceqty = obj_invpo['invoiceqty']

    def get_id(self):
        return self.id
    def get_invoiceheader_id(self):
        return self.invoiceheader
    def get_invoicedetail_id(self):
        return self.invoicedetail
    def get_ponumber(self):
        return self.ponumber
    def get_grnnumber(self):
        return self.grnnumber
    def get_grndate(self):
        return self.grndate
    def get_poquantity(self):
        return self.poquantity
    def get_receivedqty(self):
        return self.receivedqty
    def get_balanceqty(self):
        return self.balanceqty
    def get_receiveddate(self):
        return self.receiveddate
    def get_created_by(self):
        return self.created_by
    def get_pototalamt(self):
        return self.pototalamt
    def get_product_code(self):
        return self.product_code
    def get_invoicedqty(self):
        return self.invoicedqty
    def get_invoiceqty(self):
        return self.invoiceqty
