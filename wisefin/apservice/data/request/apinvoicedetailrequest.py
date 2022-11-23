import json

class APInvoiceDetailsRequest:
    id = None
    invoiceheader = None
    mepno = None
    invoice_po = None
    productcode = None
    productname = None
    description = None
    hsn = "NOHSN"
    hsn_percentage = 0
    uom = None
    unitprice = None
    quantity = None
    amount = None
    discount = 0
    sgst = 0
    cgst = 0
    igst = 0
    taxamount = 0
    totalamount = None
    created_by = None
    dtltotalamt=None
    otheramount=0
    roundoffamt=0
    is_entry = False
    is_capitalized = False

    def __init__(self,obj_invdtl):
        if 'id' in obj_invdtl:
            self.id=obj_invdtl['id']
        if 'invoiceheader_id' in obj_invdtl:
            self.invoiceheader=obj_invdtl['invoiceheader_id']
        if 'invoice_po' in obj_invdtl:
            self.invoice_po=obj_invdtl['invoice_po']
        if 'mepno' in obj_invdtl:
            self.mepno=obj_invdtl['mepno']
        if 'productcode' in obj_invdtl:
            self.productcode=obj_invdtl['productcode']
        if 'productname' in obj_invdtl:
            self.productname=obj_invdtl['productname']
        if 'description' in obj_invdtl:
            self.description=obj_invdtl['description']
        if 'hsn' in obj_invdtl:
            self.hsn=obj_invdtl['hsn']['code']
        if 'hsn_percentage' in obj_invdtl:
            self.hsn_percentage=obj_invdtl['hsn_percentage']
        if 'uom' in obj_invdtl:
            self.uom=obj_invdtl['uom']
        if 'unitprice' in obj_invdtl:
            self.unitprice=obj_invdtl['unitprice']
        if 'quantity' in obj_invdtl:
            self.quantity=obj_invdtl['quantity']
        if 'amount' in obj_invdtl:
            self.amount=obj_invdtl['amount']
        if 'discount' in obj_invdtl:
            self.discount=obj_invdtl['discount']
        if 'sgst' in obj_invdtl:
            self.sgst=obj_invdtl['sgst']
        if 'cgst' in obj_invdtl:
            self.cgst=obj_invdtl['cgst']
        if 'igst' in obj_invdtl:
            self.igst=obj_invdtl['igst']
        if 'taxamount' in obj_invdtl:
            self.taxamount=obj_invdtl['taxamount']
        if 'totalamount' in obj_invdtl:
            self.totalamount = obj_invdtl['totalamount']
        if 'created_by' in obj_invdtl:
            self.created_by = obj_invdtl['created_by']
        if 'dtltotalamt' in obj_invdtl:
            self.dtltotalamt = obj_invdtl['dtltotalamt']
        if 'otheramount' in obj_invdtl:
            self.otheramount = obj_invdtl['otheramount']
        if 'roundoffamt' in obj_invdtl:
            self.roundoffamt = obj_invdtl['roundoffamt']
        if 'is_entry' in obj_invdtl:
            self.is_entry = obj_invdtl['is_entry']

        if 'is_capitalized' in obj_invdtl:
            self.is_capitalized = obj_invdtl['is_capitalized']


    def get_id(self):
        return self.id
    def get_invoiceheader_id(self):
        return self.invoiceheader
    def get_invoice_po(self):
        return self.invoice_po
    def get_mepno(self):
        return self.mepno
    def get_productcode(self):
        return self.productcode
    def get_productname(self):
        return self.productname
    def get_description(self):
        return self.description
    def get_hsn(self):
        return self.hsn
    def get_hsn_percentage(self):
        return self.hsn_percentage
    def get_uom(self):
        return self.uom
    def get_unitprice(self):
        return self.unitprice
    def get_quantity(self):
        return self.quantity
    def get_amount(self):
        return self.amount
    def get_discount(self):
        return self.discount
    def get_sgst(self):
        return self.sgst
    def get_cgst(self):
        return self.cgst
    def get_igst(self):
        return self.igst
    def get_taxamount(self):
        return self.taxamount
    def get_totalamount(self):
        return self.totalamount
    def get_created_by(self):
        return self.created_by
    def get_dtltotalamt(self):
        return self.dtltotalamt
    def get_otheramount(self):
        return self.otheramount
    def get_roundoffamt(self):
        return self.roundoffamt
    def get_is_capitalized(self):
        return self.is_capitalized

    #******-----APInvoiceDetailsRequest--END---*****

class APDebitRequest:
    id = None
    invoiceheader = None
    invoicedetail = None
    category_code = None
    subcategory_code = None
    debitglno = None
    amount = None
    deductionamount = 0
    debittotal = None
    bsproduct_code_id = None

    def __init__(self,obj_deb,direct_entry):
        if 'id' in obj_deb:
            self.id=obj_deb['id']
        if 'invoiceheader_id' in obj_deb:
            self.invoiceheader=obj_deb['invoiceheader_id']
        if 'invoicedetail_id' in obj_deb:
            self.invoicedetail=obj_deb['invoicedetail_id']
        if 'category_code' in obj_deb:
            self.category_code=obj_deb['category_code']['code']
        if 'subcategory_code' in obj_deb:
            self.subcategory_code=obj_deb['subcategory_code']['code']
        if 'debitglno' in obj_deb:
            self.debitglno=obj_deb['debitglno']
        if 'amount' in obj_deb:
            self.amount=obj_deb['amount']
        if 'deductionamount' in obj_deb:
            self.deductionamount=obj_deb['deductionamount']
        if 'debittotal' in obj_deb:
            self.debittotal=obj_deb['debittotal']

        if direct_entry:
            if 'bsproduct_code_id' in obj_deb:
                self.bsproduct_code_id=obj_deb['bsproduct_code_id']
        else:
            if 'bsproduct' in obj_deb:
                if obj_deb['bsproduct'] is not None:
                    if 'id' in obj_deb['bsproduct']:
                        self.bsproduct_code_id=obj_deb['bsproduct']['id']


    def get_id(self):
        return self.id
    def get_invoiceheader(self):
        return self.invoiceheader
    def get_invoicedetail(self):
        return self.invoicedetail
    def get_category_code(self):
        return self.category_code
    def get_subcategory_code(self):
        return self.subcategory_code
    def get_debitglno(self):
        return self.debitglno
    def get_amount(self):
        return self.amount
    def get_deductionamount(self):
        return self.deductionamount
    def get_debittotal(self):
        return self.debittotal
    def get_bsproduct_code(self):
        return self.bsproduct_code_id



    #****-------APDebitRequest--END----*****

class APccbsDetailsRequest:
    id = None
    debit = None
    cc_code = None
    bs_code = None
    code = None
    ccbspercentage = None
    glno = None
    amount = None
    remarks = None

    def __init__(self,obj_ccbs):
        if 'id' in obj_ccbs:
            self.id=obj_ccbs['id']
        if 'cc_code' in obj_ccbs:
            self.cc_code=obj_ccbs['cc_code']['code']
        if 'bs_code' in obj_ccbs:
            self.bs_code=obj_ccbs['bs_code']['code']
        if 'code' in obj_ccbs:
            self.code=obj_ccbs['code']
        if 'ccbspercentage' in obj_ccbs:
            self.ccbspercentage=obj_ccbs['ccbspercentage']
        if 'glno' in obj_ccbs:
            self.glno=obj_ccbs['glno']
        if 'amount' in obj_ccbs:
            self.amount=obj_ccbs['amount']
        if 'remarks' in obj_ccbs:
            self.remarks=obj_ccbs['remarks']

    def get_id(self):
        return self.id
    def get_cc_code(self):
        return self.cc_code
    def get_bs_code(self):
        return self.bs_code
    def get_code(self):
        return self.code
    def get_ccbspercentage(self):
        return self.ccbspercentage
    def get_glno(self):
        return self.glno
    def get_amount(self):
        return self.amount
    def get_remarks(self):
        return self.remarks

    #*******----APccbsDetailsRequest--END-****




class APDebitEntryRequest:
    id = None
    invoiceheader = None
    invoicedetail = None
    category_code = None
    subcategory_code = None
    debitglno = None
    amount = None
    deductionamount = 0
    debittotal = None
    bsproduct_code_id = None
    bsproduct_code=None

    def __init__(self,obj_deb):
        if 'id' in obj_deb:
            self.id=obj_deb['id']
        if 'invoiceheader_id' in obj_deb:
            self.invoiceheader=obj_deb['invoiceheader_id']
        if 'invoicedetail_id' in obj_deb:
            self.invoicedetail=obj_deb['invoicedetail_id']
        if 'category_code' in obj_deb:
            self.category_code=obj_deb['code']
        if 'subcategory_code' in obj_deb:
            self.subcategory_code=obj_deb['code']
        if 'debitglno' in obj_deb:
            self.debitglno=obj_deb['debitglno']
        if 'amount' in obj_deb:
            self.amount=obj_deb['amount']
        if 'deductionamount' in obj_deb:
            self.deductionamount=obj_deb['deductionamount']
        if 'debittotal' in obj_deb:
            self.debittotal=obj_deb['debittotal']
        if 'bsproduct_code_id' in obj_deb:
            self.bsproduct_code_id=obj_deb['bsproduct_code_id']
        if 'bsproduct_code' in obj_deb:
            self.bsproduct_code = obj_deb['bsproduct_code']



    def get_id(self):
        return self.id
    def get_invoiceheader(self):
        return self.invoiceheader
    def get_invoicedetail(self):
        return self.invoicedetail
    def get_category_code(self):
        return self.category_code
    def get_subcategory_code(self):
        return self.subcategory_code
    def get_debitglno(self):
        return self.debitglno
    def get_amount(self):
        return self.amount
    def get_deductionamount(self):
        return self.deductionamount
    def get_debittotal(self):
        return self.debittotal
    def get_bsproduct_code(self):
        return self.bsproduct_code_id
    def get_bsproduct_code_id(self):
        return self.bsproduct_code

