import json

class APInwardInvoiceRequest:

    id = None
    crno = None
    inwarddetails_id = None
    invoicetype_id = None
    supplier_id = None
    supplierstate_id = None
    gst = None
    invoice_date = None
    invoice_no = None
    dedupeinvoice_no = None
    invoice_amount = None
    branch_id = None
    dueadjustment = 0
    ppx = 1
    remarks = None
    commodity_id = None



    def __init__(self,obj_apinv):
        if 'id' in obj_apinv:
            self.id=obj_apinv['id']
        if 'invoicetype_id' in obj_apinv:
            self.invoicetype_id = obj_apinv['invoicetype_id']
        if 'supplier_id' in obj_apinv:
            self.supplier_id = obj_apinv['supplier_id']
        if 'supplierstate_id' in obj_apinv:
            self.supplierstate_id = obj_apinv['supplierstate_id']
        if 'gst' in obj_apinv:
            self.gst = obj_apinv['gst']
        if 'invoice_date' in obj_apinv:
            self.invoice_date = obj_apinv['invoice_date']
        if 'invoice_no' in obj_apinv:
            self.invoice_no = obj_apinv['invoice_no']
        if 'dedupeinvoice_no' in obj_apinv:
            self.dedupeinvoice_no = obj_apinv['dedupeinvoice_no']
        if 'invoice_amount' in obj_apinv:
            self.invoice_amount = obj_apinv['invoice_amount']
        if 'branch_id' in obj_apinv:
            self.branch_id = obj_apinv['branch_id']
        if 'dueadjustment' in obj_apinv:
            self.dueadjustment = obj_apinv['dueadjustment']
        if 'ppx' in obj_apinv:
            self.ppx = obj_apinv['ppx']
        if 'remarks' in obj_apinv:
            self.remarks = obj_apinv['remarks']
        if 'commodity_id' in obj_apinv:
            self.commodity_id = obj_apinv['commodity_id']

        if 'inwarddetails_id' in obj_apinv:
            self.inwarddetails_id = obj_apinv['inwarddetails_id']


        if 'crno' in obj_apinv:
            self.crno = obj_apinv['crno']




    def get_id(self):
        return self.id
    def get_invoicetype_id(self):
        return self.invoicetype_id
    def get_supplier_id(self):
        return self.supplier_id
    def get_supplierstate_id(self):
        return self.supplierstate_id
    def get_gst(self):
        return self.gst
    def get_invoice_date(self):
        return self.invoice_date
    def get_invoice_no(self):
        return self.invoice_no
    def get_dedupeinvoice_no(self):
        return self.dedupeinvoice_no
    def get_invoice_amount(self):
        return self.invoice_amount
    def get_branch_id(self):
        return self.branch_id
    def get_dueadjustment(self):
        return self.dueadjustment
    def get_ppx(self):
        return self.ppx
    def get_remarks(self):
        return self.remarks
    def get_commodity_id(self):
        return self.commodity_id

    def get_inwarddetails_id(self):
        return self.inwarddetails_id
    def get_crno(self):
        return self.crno




