import json

class Invoiceheaderrequest:
    id =None
    ecfheader_id = None
    file_id = None
    invoiceno = None
    dedupinvoiceno = None
    invoicedate = None
    suppliergst = None
    raisorbranchgst = None
    invoiceamount = None
    taxamount = None
    totalamount = None
    otheramount = None
    roundoffamt = None
    deductionamt = None
    captalisedflag = None
    patmentinstrctn = None
    invoicenetting = None
    invoicegst = None
    created_by = None
    invtotalamt=None
    supplier_id = None
    supplierstate_id = None

    def __init__(self,obj_invhdr):
        print("1123",obj_invhdr)
        print("'ecfheader_id' in obj_invhdr",'invoiceno' in obj_invhdr)
        if 'id' in obj_invhdr:
            self.id=obj_invhdr['id']
        if 'ecfheader_id' in obj_invhdr:
            print("request",obj_invhdr['ecfheader_id'])
            self.ecfheader_id=obj_invhdr['ecfheader_id']
        if 'file_id' in obj_invhdr:
            self.file_id=obj_invhdr['file_id']
        if 'invoiceno' in obj_invhdr:
            self.invoiceno=obj_invhdr['invoiceno']
        if 'dedupinvoiceno' in obj_invhdr:
            self.dedupinvoiceno=obj_invhdr['dedupinvoiceno']
        if 'invoicedate' in obj_invhdr:
            self.invoicedate=obj_invhdr['invoicedate']
        if 'suppliergst' in obj_invhdr:
            self.suppliergst=obj_invhdr['suppliergst']
        if 'raisorbranchgst' in obj_invhdr:
            self.raisorbranchgst=obj_invhdr['raisorbranchgst']
        if 'invoiceamount' in obj_invhdr:
            self.invoiceamount=obj_invhdr['invoiceamount']
        if 'taxamount' in obj_invhdr:
            self.taxamount=obj_invhdr['taxamount']
        if 'totalamount' in obj_invhdr:
            self.totalamount=obj_invhdr['totalamount']
        if 'otheramount' in obj_invhdr:
            self.otheramount=obj_invhdr['otheramount']
        if 'roundoffamt' in obj_invhdr:
            self.roundoffamt=obj_invhdr['roundoffamt']
        if 'deductionamt' in obj_invhdr:
            self.deductionamt=obj_invhdr['deductionamt']
        if 'captalisedflag' in obj_invhdr:
            self.captalisedflag=obj_invhdr['captalisedflag']
        if 'patmentinstrctn' in obj_invhdr:
            self.patmentinstrctn=obj_invhdr['patmentinstrctn']
        if 'invoicenetting' in obj_invhdr:
            self.invoicenetting=obj_invhdr['invoicenetting']
        if 'invoicegst' in obj_invhdr:
            self.invoicegst=obj_invhdr['invoicegst']
        if 'created_by' in obj_invhdr:
            self.created_by = obj_invhdr['created_by']
        if 'invtotalamt' in obj_invhdr:
            self.invtotalamt = obj_invhdr['invtotalamt']
        if 'supplier_id' in obj_invhdr:
            self.supplier = obj_invhdr['supplier_id']
        if 'supplierstate_id' in obj_invhdr:
            self.supplierstate=obj_invhdr['supplierstate_id']

    def get_id(self):
        return self.id
    def get_ecfheader_id(self):
        return self.ecfheader_id
    def get_file_id(self):
        return self.file_id
    def get_invoiceno(self):
        return self.invoiceno
    def get_dedupinvoiceno(self):
        return self.dedupinvoiceno
    def get_invoicedate(self):
        return self.invoicedate
    def get_suppliergst(self):
        return self.suppliergst
    def get_raisorbranchgst(self):
        return self.raisorbranchgst
    def get_invoiceamount(self):
        return self.invoiceamount
    def get_taxamount(self):
        return self.taxamount
    def get_totalamount(self):
        return self.totalamount
    def get_otheramount(self):
        return self.otheramount
    def get_roundoffamt(self):
        return self.roundoffamt
    def get_deductionamt(self):
        return self.deductionamt
    def get_captalisedflag(self):
        return self.captalisedflag
    def get_patmentinstrctn(self):
        return self.patmentinstrctn
    def get_invoicenetting(self):
        return self.invoicenetting
    def get_invoicegst(self):
        return self.invoicegst
    def get_created_by(self):
        return self.created_by
    def get_invtotalamt(self):
        return self.invtotalamt
    def get_supplier_id(self):
        return self.supplier
    def get_supplierstate_id(self):
        return self.supplierstate