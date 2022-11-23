import json

class Invoiceporesponse:
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
    product_code = None
    invoicedqty = None
    invoiceqty = None
    invoicepo = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_id(self,id):
        self.id = id
    def set_invoiceheader(self,invoiceheader_id):
        self.invoiceheader = invoiceheader_id
    def set_invoicedetail(self,invoicedetail_id):
        self.invoicedetail = invoicedetail_id
    def set_ponumber(self,ponumber):
        self.ponumber = ponumber
    def set_grnnumber(self,grnnumber):
        self.grnnumber = grnnumber
    def set_grndate(self,grndate):
        grndate = str(grndate)
        self.grndate = grndate
    def set_poquantity(self,poquantity):
        self.poquantity = poquantity
    def set_receivedqty(self,receivedqty):
        self.receivedqty = receivedqty
    def set_balanceqty(self,balanceqty):
        self.balanceqty = balanceqty
    def set_receiveddate(self,receiveddate):
        receiveddate = str(receiveddate)
        self.receiveddate = receiveddate
    def set_created_by(self, created_by):
        self.created_by = created_by
    def set_product_code(self,product_code):
        self.product_code= product_code
    def set_invoicedqty(self,invoicedqty):
        self.invoicedqty = invoicedqty
    def set_invoiceqty(self, invoiceqty):
        self.invoiceqty = invoiceqty
    def set_invoicepo(self, invoicepo):
        self.invoicepo = invoicepo