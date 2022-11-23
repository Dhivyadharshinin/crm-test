import json


class RcnResponse:
    Params = None
    Classification = None
    commodity_id = None
    ecfamount = None
    ecfdate = None
    ecftype = None
    notename = None
    payto = None
    ppx = None
    remarks = None
    supplier_type = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True, indent=4)

    def set_Params(self, Params):
        self.Params = Params
    def set_InvoiceHeaders(self, InvoiceHeaders):
        self.InvoiceHeaders = InvoiceHeaders

    def set_Classification(self, Classification):
        self.Classification = Classification
    def set_commodity_id(self, commodity_id):
        self.commodity_id = commodity_id
    def set_ecfamount(self, ecfamount):
        self.ecfamount = ecfamount
    def set_ecfdate(self, ecfdate):
        self.ecfdate = ecfdate
    def set_ecftype(self, ecftype):
        self.ecftype = ecftype
    def set_notename(self, notename):
        self.notename = notename
    def set_payto(self, payto):
        self.payto = payto
    def set_ppx(self, ppx):
        self.ppx = ppx
    def set_remark(self, remark):
        self.remark = remark
    def set_supplier_type(self, supplier_type):
        self.supplier_type = supplier_type
    def set_branch(self, branch):
        self.branch = branch
    def set_client_code(self, client_code):
        self.client_code = client_code
    def set_rmcode(self, rmcode):
        self.rmcode = rmcode
    def set_raisedby(self, raisedby):
        self.raisedby = raisedby
    def set_approvedby_id(self, approvedby_id):
        self.approvedby_id = approvedby_id


class EcfResponse:
    InvoiceHeader_Gid = None
    employee_gid = None
    CREDIT_JSON = None
    DEBIT_JSON = None
    HEADER_DETAIL_JSON = None
    invoicedate = None
    dedupeinvoiceno = None
    invoiceamount = None
    invoicegst = None
    invoiceno = None
    invtotalamt = None
    otheramount = None
    raisorbranchgst = None
    roundoffamt = None
    supplier_id = None
    suppliergst = None
    supplierstate_id=None
    taxamount = None
    totalamount = None
    Credit = None

    def set_employee_gid(self, employee_gid):
        self.employee_gid = employee_gid
    def set_InvoiceHeader_Gid(self, InvoiceHeader_Gid):
        self.InvoiceHeader_Gid = InvoiceHeader_Gid
    def set_CREDIT_JSON(self, CREDIT_JSON):
        self.CREDIT_JSON = CREDIT_JSON
    def set_DEBIT_JSON(self, DEBIT_JSON):
        self.DEBIT_JSON = DEBIT_JSON
    def set_HEADER_DETAIL_JSON(self, HEADER_DETAIL_JSON):
        self.HEADER_DETAIL_JSON = HEADER_DETAIL_JSON
    def set_Credit(self, Credit):
        self.Credit = Credit


    def set_invoicedate(self, invoicedate):
        self.invoicedate = invoicedate
    def set_dedupinvoiceno(self, dedupinvoiceno):
        self.dedupinvoiceno = dedupinvoiceno
    def set_invoiceamount(self, invoiceamount):
        self.invoiceamount = invoiceamount
    def set_invoicegst(self, invoicegst):
        self.invoicegst = invoicegst
    def set_invoiceno(self, invoiceno):
        self.invoiceno = invoiceno
    def set_invtotalamt(self, invtotalamt):
        self.invtotalamt = invtotalamt
    def set_otheramount(self, otheramount):
        self.otheramount = otheramount
    def set_raisorbranchgst(self, raisorbranchgst):
        self.raisorbranchgst = raisorbranchgst
    def set_roundoffamt(self, roundoffamt):
        self.roundoffamt = roundoffamt
    def set_supplier_id(self, supplier_id):
        self.supplier_id = supplier_id
    def set_suppliergst(self, suppliergst):
        self.suppliergst = suppliergst
    def set_supplierstate_id(self, supplierstate_id):
        self.supplierstate_id = supplierstate_id
    def set_taxamount(self, taxamount):
        self.taxamount = taxamount
    def set_totalamount(self, totalamount):
        self.totalamount = totalamount
    def set_Invoicedetails(self, Invoicedetails):
        self.Invoicedetails = Invoicedetails


class CreditResponse:
    CREDIT = []

    def __init__(self):
        self.CREDIT = []

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_list(self, list):
        self.CREDIT = list

    def get_list(self):
        return self.CREDIT

    def append(self, obj):
        self.CREDIT.append(obj)


class DebitResponse:
    DEBIT = []

    def __init__(self):
        self.DEBIT = []

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_list(self, list):
        self.DEBIT = list

    def get_list(self):
        return self.DEBIT

    def append(self, obj):
        self.DEBIT.append(obj)

class CcbsResponse:
    Ccbs = []

    def __init__(self):
        self.Ccbs = []

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_list(self, list):
        self.Ccbs = list

    def get_list(self):
        return self.Ccbs

    def append(self, obj):
        self.Ccbs.append(obj)

class HeaderDetailResponse:
    HEADERDETAIL = []
    INWARD_DETAILS = []
    Invoice_Type = None
    Supplier_gid = None
    Sup_state_gid = None
    Is_GST = None
    Invoice_Date = None
    Invoice_No = None
    Invoice_Tot_Amount = None
    Supplier_GST_No = None
    Header_Status = None
    Reprocessed = None
    Remark = None
    Employee_gid = None
    GROUP = None
    branch_gid = None
    IS_ECF = None
    ECF_NO = None
    BAR_CODE = None
    RMU_CODE = None
    Due_Adjustment = None
    Advance_incr = None
    Is_onward = None
    Is_amort = None
    Is_captalized = None
    Is_rcm = None
    invoicetaxamount = None
    Pono = None
    Advance_type = None
    location = None
    invoiceheader_commoditygid = None
    notepad = None
    Commodity_gid = None
    Inwarddetails_gid = None
    In_date = None
    Channel = None
    Courier_gid = None
    AWB_no = None
    No_Of_Packets = None
    Inward_From = None
    Received_by = None
    Header_gid = None
    Is_Edit = None
    File_Key = None
    Vendor_Type=None
    Supplier_code = None
    Sup_state_code = None
    branch_code = None
    invoicedate = None
    dedupeinvoiceno = None
    invoiceamount = None
    invoicegst = None
    invoiceno = None
    invtotalamt = None
    otheramount = None
    raisorbranchgst = None
    roundoffamt = None
    supplier_id = None
    suppliergst = None
    supplierstate_id=None
    taxamount = None
    totalamount = None

    def set_Invoice_Type(self, Invoice_Type):
        self.Invoice_Type = Invoice_Type
    def set_Supplier_gid(self, Supplier_gid):
        self.Supplier_gid = Supplier_gid
    def set_Sup_state_gid(self, Sup_state_gid):
        self.Sup_state_gid = Sup_state_gid
    def set_Is_GST(self, Is_GST):
        self.Is_GST = Is_GST
    def set_Invoice_Date(self, Invoice_Date):
        Invoice_Date = str(Invoice_Date)
        self.Invoice_Date = Invoice_Date
    def set_Invoice_No(self, Invoice_No):
        self.Invoice_No = Invoice_No
    def set_Invoice_Tot_Amount(self, Invoice_Tot_Amount):
        self.Invoice_Tot_Amount = Invoice_Tot_Amount
    def set_Supplier_GST_No(self, Supplier_GST_No):
        self.Supplier_GST_No = Supplier_GST_No
    def set_Header_Status(self, Header_Status):
        self.Header_Status = Header_Status
    def set_Reprocessed(self, Reprocessed):
        self.Reprocessed = Reprocessed
    def set_Remark(self, Remark):
        self.Remark = Remark
    def set_Employee_gid(self, Employee_gid):
        self.Employee_gid = Employee_gid
    def set_GROUP(self, GROUP):
        self.GROUP = GROUP
    def set_branch_gid(self, branch_gid):
        self.branch_gid = branch_gid
    def set_IS_ECF(self, IS_ECF):
        self.IS_ECF = IS_ECF
    def set_Is_Edit(self, Is_Edit):
        self.Is_Edit=Is_Edit
    def set_ECF_NO(self, ECF_NO):
        self.ECF_NO = ECF_NO
    def set_BAR_CODE(self, BAR_CODE):
        self.BAR_CODE = BAR_CODE
    def set_RMU_CODE(self, RMU_CODE):
        self.RMU_CODE = RMU_CODE
    def set_Due_Adjustment(self, Due_Adjustment):
        self.Due_Adjustment = Due_Adjustment
    def set_Advance_incr(self, Advance_incr):
        self.Advance_incr = Advance_incr
    def set_Is_onward(self, Is_onward):
        self.Is_onward = Is_onward
    def set_Is_amort(self, Is_amort):
        self.Is_amort = Is_amort
    def set_Is_captalized(self, Is_captalized):
        self.Is_captalized = Is_captalized
    def set_Is_rcm(self, Is_rcm):
        self.Is_rcm = Is_rcm
    def set_invoicetaxamount(self, invoicetaxamount):
        self.invoicetaxamount = invoicetaxamount
    def set_Pono(self, Pono):
        self.Pono = Pono
    def set_Vendor_Type(self, Vendor_Type):
        self.Vendor_Type = Vendor_Type
    def set_Advance_type(self, Advance_type):
        self.Advance_type = Advance_type
    def set_location(self, location):
        self.location = location
    def set_notepad(self, notepad):
        self.notepad = notepad
    def set_invoiceheader_commoditygid(self, invoiceheader_commoditygid):
        self.invoiceheader_commoditygid = invoiceheader_commoditygid
    def set_Commodity_gid(self, Commodity_gid):
        self.Commodity_gid = Commodity_gid
    def set_commodity_code(self, commodity_code):
        self.commodity_code = commodity_code
    def set_Inwarddetails_gid(self, Inwarddetails_gid):
        self.Inwarddetails_gid = Inwarddetails_gid
    def set_In_date(self, In_date):
        In_date = str(In_date)
        self.In_date = In_date
    def set_Channel(self, Channel):
        self.Channel = Channel
    def set_Courier_gid(self, Courier_gid):
        self.Courier_gid = Courier_gid
    def set_AWB_no(self, AWB_no):
        self.AWB_no = AWB_no
    def set_No_Of_Packets(self, No_Of_Packets):
        self.No_Of_Packets = No_Of_Packets
    def set_Inward_From(self, Inward_From):
        self.Inward_From = Inward_From
    def set_Received_by(self, Received_by):
        self.Received_by = Received_by
    def set_Header_gid(self, Header_gid):
        self.Header_gid = Header_gid
    def set_File_Key(self, File_Key):
        self.File_Key = File_Key
    def set_branch_code(self, branch_code):
        self.branch_code = branch_code
    def set_Supplier_code(self, Supplier_code):
        self.Supplier_code = Supplier_code
    def set_Sup_state_code(self, Sup_state_code):
        self.Sup_state_code = Sup_state_code
    def set_Is_TA(self, Is_TA):
        self.Is_TA = Is_TA
    def set_Module(self, Module):
        self.Module = Module
    def set_invoicedate(self, invoicedate):
        self.invoicedate = invoicedate
    def set_dedupeinvoiceno(self, dedupeinvoiceno):
        self.dedupeinvoiceno = dedupeinvoiceno
    def set_invoiceamount(self, invoiceamount):
        self.invoiceamount = invoiceamount
    def set_invoicegst(self, invoicegst):
        self.invoicegst = invoicegst
    def set_invoiceno(self, invoiceno):
        self.invoiceno = invoiceno
    def set_invtotalamt(self, invtotalamt):
        self.invtotalamt = invtotalamt
    def set_otheramount(self, otheramount):
        self.otheramount = otheramount
    def set_raisorbranchgst(self, raisorbranchgst):
        self.raisorbranchgst = raisorbranchgst
    def set_roundoffamt(self, roundoffamt):
        self.roundoffamt = roundoffamt
    def set_supplier_id(self, supplier_id):
        self.supplier_id = supplier_id
    def set_suppliergst(self, suppliergst):
        self.suppliergst = suppliergst
    def set_supplierstate_id(self, supplierstate_id):
        self.supplierstate_id = supplierstate_id
    def set_taxamount(self, taxamount):
        self.taxamount = taxamount
    def set_totalamount(self, totalamount):
        self.totalamount = totalamount

    def __init__(self):
        self.HEADERDETAIL = []

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_list(self, list):
        self.HEADERDETAIL = list

    def get_list(self):
        return self.HEADERDETAIL

    def append(self, obj):
        self.HEADERDETAIL.append(obj)

    def set_INWARD_DETAILS(self, INWARD_DETAILS):
        self.INWARD_DETAILS = INWARD_DETAILS

class ApHeaderDetailsResponse:
    Item_Name = None
    Description = None
    HSN_Code = None
    Unit_Price = None
    Quantity = None
    Amount = None
    DetailProduct_name = None
    DetailProduct_gid = None
    DetailProduct_code = None
    Discount = None
    IGST = None
    CGST = None
    SGST = None
    Total_Amount = None
    PO_Header_Gid = None
    PO_Detail_Gid = None
    GRN_Header_Gid = None
    GRN_Detail_Gid = None
    Invoice_Sno = None
    Invoice_Other_Amount = None
    _invoicedate = None
    Invoice_Header_Gid = None
    DEBIT = None
    CREDIT = None
    Invoice_Header_gid = None
    dtltotalamt = None
    invoice_po = None
    productcode = None
    productname = None
    description = None
    hsn = None
    hsn_percentage = None
    uom = None
    unitprice = None
    quantity = None
    amount = None
    discount = None
    sgst = None
    cgst = None
    igst = None
    taxamount = None
    totalamount = None

    def set_Item_Name(self, Item_Name):
        self.Item_Name = Item_Name
    def set_Description(self, Description):
        self.Description = Description
    def set_HSN_Code(self, HSN_Code):
        self.HSN_Code = HSN_Code
    def set_Unit_Price(self, Unit_Price):
        self.Unit_Price = Unit_Price
    def set_Quantity(self, Quantity):
        self.Quantity= Quantity
    def set_Amount(self, Amount):
        self.Amount = Amount
    def set_Discount(self, Discount):
        self.Discount = Discount
    def set_IGST(self, IGST):
        self.IGST = IGST
    def set_CGST(self, CGST):
        self.CGST= CGST
    def set_SGST(self, SGST):
        self.SGST = SGST
    def set_Total_Amount(self, Total_Amount):
        self.Total_Amount = Total_Amount
    def set_PO_Header_Gid(self, PO_Header_Gid):
        self.PO_Header_Gid = PO_Header_Gid
    def set_PO_Detail_Gid(self, PO_Detail_Gid):
        self.PO_Detail_Gid = PO_Detail_Gid
    def set_GRN_Header_Gid(self, GRN_Header_Gid):
        self.GRN_Header_Gid = GRN_Header_Gid
    def set_GRN_Detail_Gid(self, GRN_Detail_Gid):
        self.GRN_Detail_Gid = GRN_Detail_Gid
    def set_Invoice_Sno(self, Invoice_Sno):
        self.Invoice_Sno = Invoice_Sno
    def set_Invoice_Other_Amount(self, Invoice_Other_Amount):
        self.Invoice_Other_Amount = Invoice_Other_Amount
    def set__invoicedate(self, _invoicedate):
        self._invoicedate = _invoicedate
    def set_Invoice_Header_Gid(self, Invoice_Header_Gid):
        self.Invoice_Header_Gid = Invoice_Header_Gid
    def set_DetailProduct_name(self, DetailProduct_name):
        self.DetailProduct_name = DetailProduct_name
    def set_DetailProduct_gid(self, DetailProduct_gid):
        self.DetailProduct_gid = DetailProduct_gid
    def set_DetailProduct_code(self, DetailProduct_code):
        self.DetailProduct_code = DetailProduct_code
    def set_Invoice_Header_gid(self, Invoice_Header_gid):
        self.Invoice_Header_gid = Invoice_Header_gid
    def set_DEBIT(self, DEBIT):
        self.DEBIT = DEBIT
    def set_CREDIT(self, CREDIT):
        self.CREDIT = CREDIT
    def set_vendor_name(self, vendor_name):
        self.vendor_name = vendor_name
    def set_dtltotalamt(self, dtltotalamt):
        self.dtltotalamt = dtltotalamt
    def set_invoice_po(self, invoice_po):
        self.invoice_po = invoice_po
    def set_productcode(self, productcode):
        self.productcode = productcode
    def set_productname(self, productname):
        self.productname = productname
    def set_description(self, description):
        self.description= description
    def set_hsn(self, hsn):
        self.hsn = hsn
    def set_hsn_percentage(self, hsn_percentage):
        self.hsn_percentage = hsn_percentage
    def set_uom(self, uom):
        self.uom = uom
    def set_unitprice(self, unitprice):
        self.unitprice= unitprice
    def set_quantity(self, quantity):
        self.quantity = quantity
    def set_amount(self, amount):
        self.amount = amount
    def set_discount(self, discount):
        self.discount = discount
    def set_sgst(self, sgst):
        self.sgst = sgst
    def set_cgst(self, cgst):
        self.cgst = cgst
    def set_igst(self, igst):
        self.igst = igst
    def set_taxamount(self, taxamount):
        self.taxamount = taxamount
    def set_totalamount(self, totalamount):
        self.totalamount = totalamount
    def set_Debits(self, Debits):
        self.Debits = Debits
    def set_otheramount(self, otheramount):
        self.otheramount = otheramount
    def set_roundoffamt(self, roundoffamt):
        self.roundoffamt = roundoffamt

class ApDebitResponse:
    Category_Gid = None
    Sub_Category_Gid = None
    D_GL_No = None
    Debit_Amount = None
    Debit_Gid = None
    Invoice_Sno = None
    Deduction_amt = None
    cc_code = None
    bs_code = None
    Debit_percentage = None
    GL_No = None
    Invoice_Details_Gid = None
    Invoice_Header_Gid = None
    Category_Code = None
    Sub_Category_Code = None
    category_code = None
    sub_category_code = None
    debitglno = None
    amount = None
    debittotal = None
    deductionamount = None
    ccbspercentage = None


    def set_Category_Gid(self, Category_Gid):
        self.Category_Gid = Category_Gid
    def set_Sub_Category_Gid(self, Sub_Category_Gid):
        self.Sub_Category_Gid = Sub_Category_Gid
    def set_D_GL_No(self, D_GL_No ):
        self.D_GL_No =D_GL_No
    def set_Debit_Amount(self, Debit_Amount):
        self.Debit_Amount = Debit_Amount
    def set_Debit_Gid(self, Debit_Gid):
        self.Debit_Gid = Debit_Gid
    def set_Invoice_Sno(self, Invoice_Sno):
        self.Invoice_Sno = Invoice_Sno
    def set_Deduction_amt(self, Deduction_amt):
        self.Deduction_amt = Deduction_amt
    def set_cc_code(self, cc_code):
        self.cc_code = cc_code
    def set_bs_code(self, bs_code):
        self.bs_code = bs_code
    def set_Debit_percentage(self, Debit_percentage):
        self.Debit_percentage = Debit_percentage
    def set_Invoice_Details_Gid(self, Invoice_Details_Gid):
        self.Invoice_Details_Gid = Invoice_Details_Gid
    def set_GL_No(self, GL_No ):
        self.GL_No = GL_No
    def set_Invoice_Header_Gid(self, Invoice_Header_Gid):
        self.Invoice_Header_Gid = Invoice_Header_Gid
    def set_Category_Code(self, Category_Code):
        self.Category_Code = Category_Code
    def set_Sub_Category_Code(self, Sub_Category_Code):
        self.Sub_Category_Code = Sub_Category_Code
    def set_cc_id(self, cc_id):
        self.cc_id = cc_id
    def set_bs_id(self, bs_id):
        self.bs_id = bs_id
    def set_category_code(self, category_code):
        self.category_code = category_code
    def set_subcategory_code(self, subcategory_code ):
        self.subcategory_code = subcategory_code
    def set_debitglno(self, debitglno):
        self.debitglno = debitglno
    def set_amount(self, amount):
        self.amount = amount
    def set_debittotal(self, debittotal):
        self.debittotal = debittotal
    def set_deductionamount(self, deductionamount):
        self.deductionamount = deductionamount
    def set_ccbspercentage(self, ccbspercentage):
        self.ccbspercentage = ccbspercentage
    def set_remarks(self, remarks):
        self.remarks = remarks
    def set_Ccbs(self, Ccbs):
        self.Ccbs = Ccbs

class Ccbs_Response:
    remarks = None
    code = None
    ccbspercentage = None
    glno = None
    amount = None
    debit = None
    cc_code = None
    bs_code = None


    def set_remarks(self, remarks):
        self.remarks = remarks
    def set_code(self, code):
        self.code = code
    def set_ccbspercentage(self, ccbspercentage ):
        self.ccbspercentage =ccbspercentage
    def set_glno(self, glno):
        self.glno = glno
    def set_amount(self, amount):
        self.amount = amount
    def set_debit(self, debit):
        self.debit = debit
    def set_cc_code(self, cc_code):
        self.cc_code = cc_code
    def set_bs_code(self, bs_code):
        self.bs_code = bs_code


class ApDetailsResponse:
    Doc_type = None
    packet = None
    Status = None
    Count = None
    Remark = None
    Detail_gid = None
    INW_header_gid = None
    def set_Doc_type(self, Doc_type):
        self.Doc_type = Doc_type
    def set_packet(self, packet):
        self.packet = packet
    def set_Status(self, Status):
        self.Status = Status
    def set_Count(self, Count):
        self.Count = Count
    def set_Remark(self, Remark):
        self.Remark = Remark
    def set_Detail_gid(self, Detail_gid):
        self.Detail_gid = Detail_gid
    def set_INW_header_gid(self, INW_header_gid):
        self.INW_header_gid = INW_header_gid

class ApCreditResponse:
    Paymode_Gid = None
    Paymode_name = None
    C_GL_No = None
    Bank_Gid = None
    Ref_No = None
    Tax_Gid = None
    Tax_Type = None
    Tax_Rate = None
    TDS_Exempt = None
    trnbranch = None
    paybranch = None
    Credit_Amount = None
    Credit_Gid = None
    taxable_amt = None
    ppx_headergid = None
    Is_due = None
    supplier_gid = None
    Credit_catgid = None
    Credit_subcatgid = None
    GL_No = None
    Ac_No = None
    paymode_code = None
    Invoice_Header_Gid = None
    supplier_code = None
    Credit_Cat_Code = None
    Credit_SubCat_Code = None
    paymoide_id = None
    creditbank_id = None
    suppliertax_id = None
    creditglno = None
    creditrefno = None
    suppliertaxtype = None
    suppliertaxrate = None
    taxexcempted = None
    amount = None
    taxableamount = None
    ddtranbranch = None
    ddpaybranch = None
    category_code = None
    subcategory_code = None
    bank = None
    ifsccode = None
    benificiary = None
    credittotal = None

    def set_Paymode_Gid(self, Paymode_Gid):
        self.Paymode_Gid = Paymode_Gid
    def set_Paymode_name(self, Paymode_name):
        self.Paymode_name = Paymode_name
    def set_C_GL_No(self, C_GL_No):
        self.C_GL_No = C_GL_No
    def set_GL_No(self, GL_No):
        self.GL_No = GL_No
    def set_Bank_Gid(self, Bank_Gid):
        self.Bank_Gid = Bank_Gid
    def set_Ref_No(self, Ref_No):
        self.Ref_No = Ref_No
    def set_Tax_Gid(self, Tax_Gid):
        self.Tax_Gid = Tax_Gid
    def set_Tax_Type(self, Tax_Type):
        self.Tax_Type = Tax_Type
    def set_Tax_Rate(self, Tax_Rate):
        self.Tax_Rate = Tax_Rate
    def set_TDS_Exempt(self, TDS_Exempt):
        self.TDS_Exempt= TDS_Exempt
    def set_trnbranch(self, trnbranch):
        self.trnbranch = trnbranch
    def set_paybranch(self, paybranch):
        self.paybranch = paybranch
    def set_Credit_Amount(self, Credit_Amount):
        self.Credit_Amount = Credit_Amount
    def set_Credit_Gid(self, Credit_Gid):
        self.Credit_Gid = Credit_Gid
    def set_taxable_amt(self, taxable_amt):
        self.taxable_amt = taxable_amt
    def set_ppx_headergid(self, ppx_headergid):
        self.ppx_headergid= ppx_headergid
    def set_Is_due(self, Is_due):
        self.Is_due = Is_due
    def set_supplier_gid(self, supplier_gid):
        self.supplier_gid = supplier_gid
    def set_Credit_catgid(self, Credit_catgid):
        self.Credit_catgid = Credit_catgid
    def set_Credit_subcatgid(self, Credit_subcatgid):
        self.Credit_subcatgid = Credit_subcatgid
    def set_Invoice_Header_Gid(self, Invoice_Header_Gid):
        self.Invoice_Header_Gid = Invoice_Header_Gid
    def set_Ac_No(self, Ac_No):
        self.Ac_No = Ac_No
    def set_supplier_code(self, supplier_code):
        self.supplier_code = supplier_code
    def set_paymode_code(self, paymode_code):
        self.paymode_code = paymode_code
    def set_Credit_Cat_Code(self, Credit_Cat_Code):
        self.Credit_Cat_Code = Credit_Cat_Code
    def set_Credit_SubCat_Code(self, Credit_SubCat_Code):
        self.Credit_SubCat_Code = Credit_SubCat_Code
    def set_paymode_id(self, paymode_id):
        self.paymode_id = paymode_id
    def set_creditbank_id(self, creditbank_id):
        self.creditbank_id = creditbank_id
    def set_suppliertax_id(self, suppliertax_id):
        self.suppliertax_id = suppliertax_id
    def set_creditglno(self, creditglno):
        self.creditglno = creditglno
    def set_creditrefno(self, creditrefno):
        self.creditrefno = creditrefno
    def set_suppliertaxtype(self, suppliertaxtype):
        self.suppliertaxtype = suppliertaxtype
    def set_suppliertaxrate(self, suppliertaxrate):
        self.suppliertaxrate = suppliertaxrate
    def set_taxexcempted(self, taxexcempted):
        self.taxexcempted= taxexcempted
    def set_amount(self, amount):
        self.amount = amount
    def set_taxableamount(self, taxableamount):
        self.taxableamount = taxableamount
    def set_ddtranbranch(self, ddtranbranch):
        self.ddtranbranch = ddtranbranch
    def set_ddpaybranch(self, ddpaybranch):
        self.ddpaybranch = ddpaybranch
    def set_category_code(self, category_code):
        self.category_code= category_code
    def set_subcategory_code(self, subcategory_code):
        self.subcategory_code = subcategory_code
    def set_bank(self, bank):
        self.bank = bank
    def set_branch(self, branch):
        self.branch = branch
    def set_ifsccode(self, ifsccode):
        self.ifsccode = ifsccode
    def set_benificiary(self, benificiary):
        self.benificiary = benificiary
    def set_credittotal(self, credittotal):
        self.credittotal = credittotal


class ClassificationResponse:
    Create_By = None
    Entity_Gid = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True, indent=4)

    def set_Create_By(self, Create_By):
        self.Create_By = Create_By

    def set_Entity_Gid(self, Entity_Gid):
        self.Entity_Gid = Entity_Gid