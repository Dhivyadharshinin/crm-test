from django.db import models
from django.utils.timezone import now
from db.vsolvmodels import VsolvModels

class APAudit(VsolvModels):
    ref_id = models.IntegerField()
    ref_type = models.CharField(max_length=28, null=True, blank=True)
    data = models.TextField( null=True, blank=True)
    user_id = models.IntegerField()
    date = models.DateTimeField(null=True, blank=True)
    req_status = models.SmallIntegerField()
    rel_refid = models.SmallIntegerField()
    rel_reftype = models.CharField(max_length=28, null=True, blank=True)
    action = models.CharField(max_length=28, null=True, blank=True)
    # class Meta:
    #     db_table = 'APAudit'


class APHeader(VsolvModels):
    inwarddetails_id = models.IntegerField(null=True)
    commodity_id = models.IntegerField(null=True)
    crno = models.CharField(max_length=16,null=True)
    aptype = models.SmallIntegerField()
    apdate = models.DateField()
    apamount = models.FloatField(default=0.00)
    apstatus = models.SmallIntegerField(default=1)
    ppx = models.CharField(max_length=1, null=True)
    dueadjustment = models.CharField(max_length=16,default='N')
    notename = models.CharField(max_length=128,null=True)
    remark = models.CharField(max_length=128,null=True)
    payto = models.CharField(max_length=1,default='S')
    raisedby= models.IntegerField(null=True)
    raiserbranch = models.IntegerField(null=True)
    raisername = models.CharField(max_length=64)
    approvedby= models.IntegerField(null=True)
    approvername = models.CharField(max_length=64,null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField()
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    supplier_type = models.IntegerField(null=True)
    is_delete = models.BooleanField(default=False)
    rmubarcode=models.CharField(max_length=16,null=True)
    branch = models.CharField(max_length=64, null=True)
    approver_branch = models.CharField(max_length=64, null=True)
    tds = models.IntegerField(default=0, null=True)
    is_originalinvoice = models.BooleanField(default=True)
    rmcode = models.CharField(max_length=16,null=True)
    client_code = models.CharField(max_length=16,null=True)



class APInvoiceHeader(VsolvModels):
    apheader = models.ForeignKey(APHeader, on_delete=models.CASCADE)
    invoiceno = models.CharField(max_length=16)
    dedupinvoiceno = models.CharField(max_length=16)
    invoicedate = models.DateField()
    suppliergst=models.CharField(max_length=16,null=True)
    raisorbranchgst=models.CharField(max_length=16)
    invoiceamount=models.FloatField()
    taxamount=models.FloatField(default=0.00)
    totalamount=models.FloatField()
    otheramount =models.FloatField(default=0.00)
    roundoffamt=models.FloatField(default=0)
    deductionamt=models.FloatField(default=0)
    captalisedflag=models.CharField(max_length=1,default='N')
    paymentinstrctn=models.CharField(max_length=128,null=True)
    invoicenetting=models.CharField(max_length=1,default='N')
    invoicegst=models.CharField(max_length=1,default='N')
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    supplier_id = models.IntegerField(null=True)
    supplierstate_id = models.IntegerField(null=True)
    apinvoiceheaderstatus = models.SmallIntegerField(null=True)
    is_delete = models.BooleanField(default=False)
    bankdetails_id = models.IntegerField(null=True)
    barcode = models.CharField(max_length=16,null=True)
    apinvoiceheader_crno = models.CharField(max_length=16, null=True)
    entry_flag = models.BooleanField(default=False)


class APInvoicedetail(VsolvModels):
    apinvoiceheader =models.ForeignKey(APInvoiceHeader,on_delete=models.CASCADE)
    apinvoice_po = models.IntegerField(null=True)
    mepno = models.CharField(max_length=16,null=True)
    productcode = models.CharField(max_length=16)
    productname = models.CharField(max_length=128,null=True)
    description = models.CharField(max_length=128,null=True)
    hsn = models.CharField(max_length=16,null=True)
    hsn_percentage = models.IntegerField(default=0)
    uom = models.CharField(max_length=16,null=True)
    unitprice = models.FloatField()
    quantity = models.IntegerField()
    amount = models.FloatField()
    discount = models.FloatField(default=0)
    sgst = models.FloatField(default=0)
    cgst = models.FloatField(default=0)
    igst = models.FloatField(default=0)
    taxamount = models.FloatField(default=0)
    totalamount = models.FloatField()
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    is_delete = models.BooleanField(default=False)
    otheramount = models.FloatField(default=0.00)
    roundoffamt = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    is_entry = models.BooleanField(default=False)
    entry_flag = models.BooleanField(default=False)
    is_capitalized = models.BooleanField(default=False)


class APDebit(VsolvModels):
    apinvoiceheader = models.ForeignKey(APInvoiceHeader,on_delete=models.CASCADE)
    apinvoicedetail = models.ForeignKey(APInvoicedetail,on_delete=models.CASCADE,null=True)
    category_code = models.CharField(max_length=16,null=True)
    subcategory_code = models.CharField(max_length=16,null=True)
    debitglno = models.CharField(max_length=64,null=True)
    amount = models.FloatField(default=0.00)
    deductionamount = models.FloatField(default=0)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    is_delete = models.BooleanField(default=False)
    bsproduct = models.CharField(max_length=16,null=True)
    is_entry = models.BooleanField(default=False)
    vendor_type = models.CharField(max_length=32, null=True)


class APCredit(VsolvModels):
    apinvoiceheader = models.ForeignKey(APInvoiceHeader,on_delete=models.CASCADE)
    paymode_id = models.IntegerField(null=True)
    creditbank_id = models.IntegerField(null=True)
    suppliertax_id = models.IntegerField(null=True)
    creditglno = models.IntegerField(default=0)
    creditrefno = models.CharField(max_length=64,null=True)
    suppliertaxtype = models.CharField(max_length=32,null=True)
    suppliertaxrate = models.FloatField(default=0)
    taxexcempted = models.CharField(max_length=1,default='N')
    amount = models.FloatField()
    taxableamount = models.FloatField(default=0)
    ddtranbranch = models.IntegerField(default=0)
    ddpaybranch = models.IntegerField(default=0)
    category_code = models.CharField(max_length=16, null=True)
    subcategory_code = models.CharField(max_length=16, null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    is_delete = models.BooleanField(default=False)
    is_entry = models.BooleanField(default=False)
    vendor_type = models.CharField(max_length=32, null=True)



class APCCBSDetails(VsolvModels):
    apdebit = models.ForeignKey(APDebit,on_delete=models.CASCADE)
    cc_code = models.CharField(max_length=16,null=True)
    bs_code = models.CharField(max_length=16,null=True)
    code = models.IntegerField()
    ccbspercentage = models.FloatField()
    glno = models.CharField(max_length=64,null=True)
    amount = models.FloatField()
    remarks = models.CharField(max_length=128,null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    is_delete = models.BooleanField(default=False)

class APQueue(VsolvModels):
    ref_id = models.IntegerField(default=6)
    ref_type = models.IntegerField(default=6)
    from_user_id = models.IntegerField(null=False)
    to_user_id = models.IntegerField(null=False)
    created_date = models.DateTimeField(default=now)
    comments = models.CharField(null=False, max_length=2048)
    remarks = models.CharField(max_length=128, null=True, blank=True)
    status = models.SmallIntegerField(default=1)
    is_sys = models.BooleanField(default=False)



class APAuditChecklist(VsolvModels):
    type = models.IntegerField()
    group = models.CharField(max_length=64)
    code = models.CharField(max_length=32)
    question = models.CharField(max_length=512)
    solution = models.CharField(max_length=512)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    is_delete = models.BooleanField(default=False)


class APAuditChecklistMapping(VsolvModels):
    apauditchecklist = models.ForeignKey(APAuditChecklist,on_delete=models.CASCADE)
    apinvoiceheader_id = models.IntegerField()
    value = models.IntegerField()
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)




class APBounce(VsolvModels):
    apinvoiceheader =models.ForeignKey(APInvoiceHeader,on_delete=models.CASCADE)
    invoicedate = models.DateField()
    mailto = models.CharField(max_length=128,null=True)
    mailcc = models.CharField(max_length=128,null=True)
    content = models.CharField(max_length=1024,null=True)
    is_mailsent = models.BooleanField(default=False,null=True)
    maildate = models.DateField(null=True)
    is_reprocess = models.BooleanField(default=False,null=True)
    reprocessdate = models.DateField(null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    is_delete = models.BooleanField(default=False)



class PaymentHeader(VsolvModels):
    pvno = models.CharField(max_length=32, unique=True)
    paymentheader_date = models.DateField()
    paymentheader_amount = models.FloatField(default=0)
    pay_to = models.CharField(max_length=32,null=True)
    beneficiary_code = models.CharField(max_length=32,null=True)
    #paymode_id = models.IntegerField()
    paymode = models.CharField(max_length=8)
    bankdetails_id = models.IntegerField(null=True)
    dispatch_id = models.IntegerField(null=True)
    beneficiaryname = models.CharField(max_length=128)
    chqno = models.CharField(max_length=8)
    chqdate = models.DateField(null=True)
    bankname = models.CharField(max_length=128)
    IFSCcode = models.CharField(max_length=16,null=True)
    accno = models.CharField(max_length=45,null=True)
    #debitbankacc = models.CharField(max_length=45,null=True)
    stalechq_id = models.IntegerField(null=True)
    refno = models.CharField(max_length=45, null=True)
    callbackrefno = models.CharField(max_length=45, null=True)
    remarks = models.CharField(max_length=128, null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    is_delete = models.BooleanField(default=False)


class PaymentDetails(VsolvModels):
    paymentheader = models.ForeignKey(PaymentHeader, on_delete=models.CASCADE)
    apinvoiceheader =models.ForeignKey(APInvoiceHeader,on_delete=models.CASCADE)
    apcredit =models.ForeignKey(APCredit,on_delete=models.CASCADE)
    paymentdetails_amount = models.FloatField(default=0)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    is_delete = models.BooleanField(default=False)


class APFiles(VsolvModels):
    file_id = models.CharField(max_length=100,default=-1)
    filename = models.CharField(max_length=512,null=True)
    gen_filename = models.CharField(max_length=64,null=True)
    ref_id = models.IntegerField()
    ref_type = models.IntegerField()
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    is_delete = models.BooleanField(default=False)

class APMapInvoicePO(VsolvModels):
    apinvoiceheader = models.ForeignKey(APInvoiceHeader, on_delete=models.CASCADE)
    apinvoicedetail = models.ForeignKey(APInvoicedetail, on_delete=models.CASCADE)
    invoiceno = models.CharField(max_length=32)
    pono = models.CharField(max_length=32)
    podetailno = models.CharField(max_length=32)
    grninwardno = models.CharField(max_length=32)
    productcode = models.CharField(max_length=32)
    invoicepo_qty = models.FloatField()
    invoicepo_capitalised = models.BooleanField(default=False)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    is_delete = models.BooleanField(default=False)

class APppxHeader(VsolvModels):
    apinvoiceheader = models.ForeignKey(APInvoiceHeader, on_delete=models.CASCADE)
    crno = models.CharField(max_length=16, null=True)
    ppxheader_date = models.DateTimeField(default=now)
    ppxheader_amount = models.FloatField()
    ppxheader_balance = models.FloatField()
    is_closed = models.BooleanField(default=False)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    is_delete = models.BooleanField(default=False)
    process_amount = models.FloatField(default=0)
    ap_amount = models.FloatField(default=0)
    ecf_amount = models.FloatField(default=0)


class APppxDetails(VsolvModels):
    apppxheader = models.ForeignKey(APppxHeader, on_delete=models.CASCADE)
    apinvoiceheader = models.ForeignKey(APInvoiceHeader, on_delete=models.CASCADE)
    apcredit = models.ForeignKey(APCredit, on_delete=models.CASCADE)
    ppxdetails_amount = models.FloatField()
    ppxdetails_adjusted = models.FloatField()
    ppxdetails_balance = models.FloatField()
    is_closed = models.BooleanField(default=False)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    is_delete = models.BooleanField(default=False)
    process_amount = models.FloatField(default=0)
    ap_amount = models.FloatField(default=0)
    ecf_amount = models.FloatField(default=0)
    ecfheader_id = models.IntegerField(null=True)
    ppxlique_crno = models.CharField(max_length=16, null=True)


class APSegment_Vendor_Identifier(VsolvModels):
    supplierbranch_code = models.CharField(max_length=128)
    glno = models.CharField(max_length=64, null=True)
    vendor_type = models.CharField(max_length=32, null=True)
    status = models.SmallIntegerField(default=1)
    created_by = models.IntegerField(null=True, blank=True)
    created_date = models.DateTimeField(default=now)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_date = models.DateTimeField(null=True, blank=True)
    is_delete = models.BooleanField(default=False)