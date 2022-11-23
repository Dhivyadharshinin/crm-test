import json


class APInvoicemapResponse:
    id = None
    apinvoiceheader_id = None
    apinvoicedetail_id = None
    apinvoiceheader = None
    apinvoicedetail = None
    invoiceno = None
    pono = None
    podetailno = None
    grninwardno = None
    productcode = None
    invoicepo_qty = None
    invoicepo_capitalised = None

    def get(self):
      return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id


    def set_apinvoiceheader_id(self, apinvoiceheader_id):
        self.apinvoiceheader_id = apinvoiceheader_id
    def set_apinvoicedetail_id(self, apinvoicedetail_id):
        self.apinvoicedetail_id = apinvoicedetail_id
    def set_invoiceno(self, invoiceno):
        self.invoiceno = invoiceno
    def set_pono(self, pono):
        self.pono = pono
    def set_podetailno(self, podetailno):
        self.podetailno = podetailno
    def set_grninwardno(self, grninwardno):
        self.grninwardno = grninwardno
    def set_productcode(self, productcode):
        self.productcode = productcode
    def set_invoicepo_qty(self, invoicepo_qty):
        self.invoicepo_qty = invoicepo_qty
    def set_invoicepo_capitalised(self, invoicepo_capitalised):
        self.invoicepo_capitalised = invoicepo_capitalised

    def set_apinvoiceheader(self, apinvoiceheader):
        self.apinvoiceheader = apinvoiceheader
    def set_apinvoicedetail(self, apinvoicedetail):
        self.apinvoicedetail = apinvoicedetail

