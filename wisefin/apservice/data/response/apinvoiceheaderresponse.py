import json

class APInvoiceheaderresponse:
    id=None
    apheader_id = None
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
    apinvoicedetails=None
    credit = None
    debit = None
    invoiceheader = []
    supplier_id = None
    supplier = None
    supplierstate_id = None
    gsttype = None
    supgstno = None
    apdebit = None
    apcredit = None
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
    invoicetype_id = None
    invoicetype = None
    raiser_employeename = None
    apamount = None
    paymod = None
    apdate=None
    raisername=None
    approvername=None
    updated_date=None
    invoicehdr_crno=None
    createdby_data=None
    is_originalinvoice=None
    employee_accountdtls=None
    pay_to=None
    supplierpayment_details=None
    entry_flag=None

    def get(self):
        return json.dumps(self, default=lambda o:o.__dict__, sort_keys=True, indent=4)

    def set_id(self,id):
        self.id = id
    def set_apheader(self,apheader_id):
        self.apheader_id = apheader_id
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
    def set_debit(self, debit):
        self.debit = debit
    def set_invoiceheader(self, invoiceheader):
        self.invoiceheader = invoiceheader
    def set_supplier(self,supplier_id):
        self.supplier=supplier_id
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
    def set_apinvoicedetails(self, apinvoicedetails):
        self.apinvoicedetails = apinvoicedetails
    def set_apdebit(self, apdebit):
        self.apdebit = apdebit
    def set_apcredit(self, apcredit):
        self.apcredit = apcredit
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
    def set_invoicetype_id(self,invoicetype_id):
        self.invoicetype_id = invoicetype_id
    def set_invoicetype(self,invoicetype):
        self.invoicetype = invoicetype
    def set_raiser_employeename(self,raiser_employeename):
        self.raiser_employeename = raiser_employeename
    def set_apheader_id(self,apheader_id):
        self.apheader_id = apheader_id
    def set_apamount(self,apamount):
        self.apamount = apamount
    def set_paymod(self,paymod):
        self.paymod = paymod
    def set_apdate(self,apdate):
        self.apdate = apdate
    def set_raisername(self,raisername):
        self.raisername = raisername
    def set_approvername(self,approvername):
        self.approvername = approvername
    def set_updated_date(self,updated_date):
        self.updated_date = updated_date
    def set_invoicehdr_crno(self,invoicehdr_crno):
        self.invoicehdr_crno = invoicehdr_crno
    def set_createdby_data(self,createdby_data):
        self.createdby_data = createdby_data
    def set_is_originalinvoice(self,is_originalinvoice):
        self.is_originalinvoice = is_originalinvoice

    def set_employee_account_dtls(self,employee_account_dtls):
        self.employee_accountdtls = employee_account_dtls

    def set_pay_to(self,pay_to):
        self.pay_to = pay_to

    def set_supplierpayment_details(self,supplierpayment_details):
        self.supplierpayment_details = supplierpayment_details


    def set_entry_flag(self,entry_flag):
        self.entry_flag = entry_flag



#***********---------APInvoiceheaderresponse-----END-----**********


class APppxHeaderResponse:
    id=None
    apinvoiceheader_id = None
    crno = None
    ppxheader_date = None
    ppxheader_amount = None
    ppxheader_balance = None
    process_amount = None
    ap_amount = None
    ecf_amount = None



    def get(self):
        return json.dumps(self, default=lambda o:o.__dict__, sort_keys=True, indent=4)

    def set_id(self,id):
        self.id = id
    def set_apinvoiceheader_id(self,apinvoiceheader_id):
        self.apinvoiceheader_id = apinvoiceheader_id
    def set_crno(self,crno):
        self.crno = crno
    def set_ppxheader_date(self,ppxheader_date):
        self.ppxheader_date = str(ppxheader_date)
    def set_ppxheader_amount(self,ppxheader_amount):
        self.ppxheader_amount = ppxheader_amount
    def set_ppxheader_balance(self,ppxheader_balance):
        self.ppxheader_balance = ppxheader_balance

    def set_process_amount(self,process_amount):
        self.process_amount = process_amount

    def set_ap_amount(self,ap_amount):
        self.ap_amount = ap_amount

    def set_ecf_amount(self,ecf_amount):
        self.ecf_amount = ecf_amount



    # ***********---------APppxHeaderResponse-----END-----**********


class APppxDetailsResponse:
    id=None
    apppxheader_id = None
    apinvoiceheader_id = None
    apcredit_id = None
    ppxdetails_amount = None
    ppxdetails_adjusted = None
    ppxdetails_balance = None
    process_amount = None
    ap_amount = None
    ecf_amount = None
    ecfheader_id = None



    def get(self):
        return json.dumps(self, default=lambda o:o.__dict__, sort_keys=True, indent=4)

    def set_id(self,id):
        self.id = id
    def set_apppxheader_id(self,apppxheader_id):
        self.apppxheader_id = apppxheader_id
    def set_apinvoiceheader_id(self,apinvoiceheader_id):
        self.apinvoiceheader_id = apinvoiceheader_id
    def set_apcredit_id(self,apcredit_id):
        self.apcredit_id = str(apcredit_id)
    def set_ppxdetails_amount(self,ppxdetails_amount):
        self.ppxdetails_amount = ppxdetails_amount
    def set_ppxdetails_adjusted(self,ppxdetails_adjusted):
        self.ppxdetails_adjusted = ppxdetails_adjusted
    def set_ppxdetails_balance(self,ppxdetails_balance):
        self.ppxdetails_balance = ppxdetails_balance

    def set_process_amount(self,process_amount):
        self.process_amount = process_amount
    def set_ap_amount(self,ap_amount):
        self.ap_amount = ap_amount
    def set_ecf_amount(self,ecf_amount):
        self.ecf_amount = ecf_amount
    def set_ecfheader_id(self,ecfheader_id):
        self.ecfheader_id = ecfheader_id




    # ***********---------APppxDetailsResponse-----END-----**********

