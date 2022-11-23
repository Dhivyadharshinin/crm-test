import json

class Invoiceheaderresponse:
    id=None
    ecfheader = None
    fileid = None
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
    created_by =None
    invtotalamt=None
    invoicepo = None
    invoicedtl=None
    credit = None
    debit = None
    invoiceheader = []
    supplier_id = None
    supplierstate_id = None
    gsttype = None
    supgstno = None
    file_data = None
    inv_crno = None
    Branchgst= None
    Gsttype = None
    Supgstno = None
    Branchname = None

    def get(self):
        return json.dumps(self, default=lambda o:o.__dict__, sort_keys=True, indent=4)

    def set_id(self,id):
        self.id = id
    def set_ecfheader(self,ecfheader_id):
        self.ecfheader_id = ecfheader_id
    def set_inv_crno(self,inv_crno):
        self.inv_crno= inv_crno
    def set_file_id(self,file_id):
        self.file_id = file_id
    def set_invoiceno(self,invoiceno):
        self.invoiceno = invoiceno
    def set_dedupinvoiceno(self,dedupinvoiceno):
        self.dedupinvoiceno = dedupinvoiceno
    def set_invoicedate(self,invoicedate):
        invoicedate = str(invoicedate)
        self.invoicedate = invoicedate
    def set_suppliergst(self,suppliergst):
        self.suppliergst = suppliergst
    def set_raisorbranchgst(self,raisorbranchgst):
        self.raisorbranchgst = raisorbranchgst
    def set_invoiceamount(self,invoiceamount):
        self.invoiceamount = invoiceamount
    def set_taxamount(self,taxamount):
        self.taxamount = taxamount
    def set_totalamount(self,totalamount):
        self.totalamount = totalamount
    def set_otheramount(self,otheramount):
        self.otheramount = otheramount
    def set_roundoffamt(self,roundoffamt):
        roundoffamt= str(roundoffamt)
        self.roundoffamt = roundoffamt
    def set_deductionamt(self,deductionamt):
        self.deductionamt = deductionamt
    def set_captalisedflag(self,captalisedflag):
        self.captalisedflag = captalisedflag
    def set_patmentinstrctn(self,patmentinstrctn):
        self.patmentinstrctn = patmentinstrctn
    def set_invoicenetting(self,invoicenetting):
        self.invoicenetting = invoicenetting
    def set_invoicegst(self,invoicegst):
        self.invoicegst = invoicegst
    def set_created_by(self, created_by):
        self.created_by = created_by
    def set_invtotalamt(self, invtotalamt):
        self.invtotalamt = invtotalamt
    def set_invoicepo(self, invoicepo):
        self.invoicepo = invoicepo
    def set_invoicedtl(self, invoicedtl):
        self.invoicedtl = invoicedtl
    def set_credit(self, credit):
        self.credit = credit
    def set_file_data(self, file_data):
        self.file_data = file_data
    def set_debit(self, debit):
        self.debit = debit
    def set_invoiceheader(self, invoiceheader):
        self.invoiceheader = invoiceheader
    def set_supplier(self,supplier_id):
        self.supplier_id=supplier_id
    def set_supplier_id(self, supplier_id, arr):
        if supplier_id != None:
            for i in arr:
                if i['id'] == supplier_id:
                    self.supplier_id = i
                    break
    def set_supplierstate(self,supplierstate_id):
        self.supplierstate_id =supplierstate_id
    def set_supplierstate_id(self, supplierstate_id, arr):
        if supplierstate_id != None:
            for i in arr:
                if i['id'] == supplierstate_id:
                    self.supplierstate_id = i
                    break
    def set_gsttype(self, gsttype):
        self.gsttype = gsttype
    def set_supgstno(self, supgstno):
        self.supgstno = supgstno
    def set_Branchgst(self, Branchgst):
        self.Branchgst = Branchgst
    def set_Gsttype(self, Gsttype):
        self.Gsttype = Gsttype
    def set_Supgstno(self, Supgstno):
        self.Supgstno = Supgstno
    def set_Branchname(self, Branchname):
        self.Branchname = Branchname

