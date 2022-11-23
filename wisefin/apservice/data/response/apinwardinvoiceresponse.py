import json

class APInwardInvoiceResponse:

    id = None
    invoicetype_id = None
    invoicetype = None
    inwarddetails_id = None
    supplier_id = None
    supplier = None
    supplierstate_id = None
    gst = None
    invoice_date = None
    invoice_no = None
    dedupeinvoice_no = None
    invoice_amount = None
    branch_id = None
    branch = None
    dueadjustment = None
    ppx = None
    remarks = None
    commodity_id = None
    document_id = None
    crno = None
    rmubarcode = None
    barcode = None
    status = None

    def get(self):
        return json.dumps(self, default=lambda o:o.__dict__, sort_keys=True, indent=4)

    def set_id(self,id):
        self.id = id
    def set_invoicetype_id(self,invoicetype_id):
        self.invoicetype_id = invoicetype_id
    def set_supplier_id(self,supplier_id):
        self.supplier_id = supplier_id
    def set_supplier(self,supplier):
        self.supplier = supplier
    def set_supplierstate_id(self,supplierstate_id):
        self.supplierstate_id = supplierstate_id
    def set_gst(self,gst):
        self.gst = gst
    def set_invoice_date(self,invoice_date):
        self.invoice_date = str(invoice_date)
    def set_invoice_no(self,invoice_no):
        self.invoice_no = invoice_no
    def set_dedupeinvoice_no(self,dedupeinvoice_no):
        self.dedupeinvoice_no = dedupeinvoice_no
    def set_invoice_amount(self,invoice_amount):
        self.invoice_amount = str(invoice_amount)
    def set_branch_id(self,branch_id):
        self.branch_id = branch_id
    def set_dueadjustment(self,dueadjustment):
        self.dueadjustment = dueadjustment
    def set_ppx(self,ppx):
        self.ppx = ppx
    def set_remarks(self,remarks):
        self.remarks = remarks
    def set_commodity_id(self,commodity_id):
        self.commodity_id = commodity_id
    def set_document_id(self,document_id):
        self.document_id = document_id
    def set_crno(self,crno):
        self.crno = crno
    def set_barcode(self,barcode):
        self.barcode = barcode
    def set_rmubarcode(self,rmubarcode):
        self.rmubarcode = rmubarcode

    def set_inwarddetails_id(self,inwarddetails_id):
        self.inwarddetails_id = inwarddetails_id


    def set_branch(self,branch):
        self.branch = branch

    def set_status(self,status):
        self.status = status


    def set_invoicetype(self,invoicetype):
        self.invoicetype = invoicetype

