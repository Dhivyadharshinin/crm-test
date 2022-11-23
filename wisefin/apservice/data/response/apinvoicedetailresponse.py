import json

class APInvoiceDetailsResponse:
    id=None
    apinvoiceheader = None
    apinvoice_po = None
    mepno = None
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
    created_by = None
    dtltotalamt=None
    debit=None
    apinvoicedetails=None
    productcode_details=None
    otheramount = None
    roundoffamt = None
    is_entry = None
    is_capitalized = None
    entry_flag = 0

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_id(self,id):
        self.id = id
    def set_apinvoiceheader(self,invoiceheader_id):
        self.apinvoiceheader = invoiceheader_id
    def set_apinvoice_po(self,invoice_po):
        self.apinvoice_po = invoice_po
    def set_mepno(self,mepno):
        self.mepno = mepno
    def set_productcode(self,productcode):
        self.productcode = productcode
    def set_productname(self,productname):
        self.productname = productname
    def set_description(self,description):
        self.description = description
    def set_hsn(self,hsn):
        self.hsn = hsn
    def set_hsn_percentage(self,hsn_percentage):
        self.hsn_percentage = hsn_percentage
    def set_uom(self,uom):
        self.uom = uom
    def set_unitprice(self,unitprice):
        self.unitprice = unitprice
    def set_quantity(self,quantity):
        self.quantity = quantity
    def set_amount(self,amount):
        self.amount = amount
    def set_discount(self,discount):
        self.discount = discount
    def set_sgst(self,sgst):
        self.sgst = sgst
    def set_cgst(self,cgst):
        self.cgst = cgst
    def set_igst(self,igst):
        self.igst = igst
    def set_taxamount(self,taxamount):
        self.taxamount = taxamount
    def set_totalamount(self,totalamount):
        self.totalamount = totalamount
    def set_created_by(self,created_by):
        self.created_by = created_by
    def set_dtltotalamt(self,dtltotalamt):
        self.dtltotalamt = dtltotalamt
    def set_debit(self,debit):
        self.debit = debit
    def set_apinvoicedetails(self,invoicedetails):
        self.apinvoicedetails = invoicedetails

    def set_productcode_details(self,productcode_details):
        self.productcode_details = productcode_details

    def set_otheramount(self,otheramount):
        self.otheramount = str(otheramount)

    def set_roundoffamt(self,roundoffamt):
        self.roundoffamt =str(roundoffamt)

    def set_is_entry(self,is_entry):
        self.is_entry =is_entry

    def set_is_capitalized(self,is_capitalized):
        self.is_capitalized =is_capitalized

    def set_entry_flag(self,entry_flag):
        self.entry_flag =entry_flag

    #*****----APInvoiceDetailsResponse---END---******
    #Subcatcode- REG CWIP BUC

class APDebitResponse:
    id =None
    apinvoiceheader = None
    apinvoicedetail = None
    category_code = None
    subcategory_code = None
    debitglno = None
    amount = None
    deductionamount = None
    ccbs = None
    debit=None
    bsproduct_code=None
    vendor_type=None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_id(self,id):
        self.id = id
    def set_apinvoiceheader(self,apinvoiceheader_id):
        self.apinvoiceheader = apinvoiceheader_id
    def set_apinvoicedetail(self,apinvoicedetail_id):
        self.apinvoicedetail = apinvoicedetail_id
    def set_category_code(self,category_code):
        self.category_code = category_code
    def set_subcategory_code(self,subcategory_code):
        self.subcategory_code =subcategory_code
    def set_debitglno(self,debitglno):
        self.debitglno =debitglno
    def set_amount(self,amount):
        self.amount =amount
    def set_deductionamount(self,deductionamount):
        self.deductionamount =deductionamount
    def set_ccbs(self,ccbs):
        self.ccbs =ccbs
    def set_debit(self,debit):
        self.debit =debit
    def set_bsproduct_code(self,bsproduct_code):
        self.bsproduct_code =bsproduct_code

    def set_vendor_type(self,vendor_type):
        self.vendor_type =vendor_type


    #*****----APDebitResponse----END---*******


class APccbsDetailsResponse:
    id=None
    debit = None
    cc_code = None
    bs_code = None
    code = None
    ccbspercentage = None
    glno = None
    amount = None
    remarks = None
    ccbsdtl=None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_id(self,id):
        self.id = id
    def set_debit(self,debit_id):
        self.debit = debit_id
    def set_cc_code(self,cc_code):
        self.cc_code = cc_code
    def set_bs_code(self,bs_code):
        self.bs_code = bs_code
    def set_code(self,code):
        self.code = code
    def set_ccbspercentage(self,ccbspercentage):
        self.ccbspercentage = ccbspercentage
    def set_glno(self,glno):
        self.glno = glno
    def set_amount(self,amount):
        self.amount = amount
    def set_remarks(self,remarks):
        self.remarks = remarks
    def set_ccbsdtl(self,ccbsdtl):
        self.ccbsdtl = ccbsdtl


    #****-----APccbsDetailsResponse----END---******