import json

class Invoicedetailresponse:
    id=None
    invoiceheader = None
    invoice_po = None
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
    invoicedetails=None
    invoiceno = None
    invoicedate = None
    supplier_name = None
    suppliergst = None
    pincode = None
    otheramount = None
    roundoffamt = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_id(self,id):
        self.id = id
    def set_invoiceheader(self,invoiceheader_id):
        self.invoiceheader = invoiceheader_id
    def set_invoice_po(self,invoice_po):
        self.invoice_po = invoice_po
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
    def set_invoicedetails(self,invoicedetails):
        self.invoicedetails = invoicedetails
    def set_invoiceno(self,invoiceno):
        self.invoiceno = invoiceno
    def set_invoicedate(self, invoicedate):
        invoicedate = str(invoicedate)
        self.invoicedate = invoicedate
    def set_supplier_name(self,supplier_name):
        self.supplier_name = supplier_name
    def set_suppliergst(self,suppliergst):
        self.suppliergst = suppliergst
    def set_pincode(self,pincode):
        self.pincode = pincode
    def set_otheramount(self,otheramount):
        self.otheramount = otheramount
    def set_roundoffamt(self,roundoffamt):
        roundoffamt= str(roundoffamt)
        self.roundoffamt = roundoffamt

class Debitresponse:
    id =None
    invoiceheader = None
    invoicedetail = None
    category_code = None
    subcategory_code = None
    debitglno = None
    amount = None
    deductionamount = None
    ccbs = None
    debit=None
    bsproduct = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_id(self,id):
        self.id = id
    def set_invoiceheader(self,invoiceheader_id):
        self.invoiceheader = invoiceheader_id
    def set_invoicedetail(self,invoicedetail_id):
        self.invoicedetail = invoicedetail_id
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
    def set_bsproduct(self,bsproduct):
        self.bsproduct =bsproduct


class ccbsdtlresponse:
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


