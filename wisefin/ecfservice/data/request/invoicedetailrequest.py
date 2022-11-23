import json

class Invoicedetailrequest:
    id = None
    invoiceheader = None
    mepno = None
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
    created_by = None
    dtltotalamt=None
    invoiceno = None
    invoicedate = None
    supplier_name = None
    suppliergst = None
    pincode = None
    otheramount = None
    roundoffamt = None

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
            self.hsn=obj_invdtl['hsn']
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
        if 'invoiceno' in obj_invdtl:
            self.invoiceno=obj_invdtl['invoiceno']
        if 'invoicedate' in obj_invdtl:
            self.invoicedate=obj_invdtl['invoicedate']
        if 'supplier_name' in obj_invdtl:
            self.supplier_name=obj_invdtl['supplier_name']
        if 'suppliergst' in obj_invdtl:
            self.suppliergst=obj_invdtl['suppliergst']
        if 'pincode' in obj_invdtl:
            self.pincode=obj_invdtl['pincode']
        if 'otheramount' in obj_invdtl:
            self.otheramount=obj_invdtl['otheramount']
        if 'roundoffamt' in obj_invdtl:
            self.roundoffamt=obj_invdtl['roundoffamt']


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
    def get_invoiceno(self):
        return self.invoiceno
    def get_invoicedate(self):
        return self.invoicedate
    def get_supplier_name(self):
        return self.supplier_name
    def get_suppliergst(self):
        return self.suppliergst
    def get_pincode(self):
        return self.pincode
    def get_otheramount(self):
        return self.otheramount
    def get_roundoffamt(self):
        return self.roundoffamt

class Debitrequest:
    id = None
    invoiceheader = None
    invoicedetail = None
    category_code = None
    subcategory_code = None
    debitglno = None
    amount = None
    deductionamount = None
    debittotal = None
    bsproduct = None

    def __init__(self,obj_deb):
        if 'id' in obj_deb:
            self.id=obj_deb['id']
        if 'invoiceheader_id' in obj_deb:
            self.invoiceheader=obj_deb['invoiceheader_id']
        if 'invoicedetail_id' in obj_deb:
            self.invoicedetail=obj_deb['invoicedetail_id']
        if 'category_code' in obj_deb:
            self.category_code=obj_deb['category_code']
        if 'subcategory_code' in obj_deb:
            self.subcategory_code=obj_deb['subcategory_code']
        if 'debitglno' in obj_deb:
            self.debitglno=obj_deb['debitglno']
        if 'amount' in obj_deb:
            self.amount=obj_deb['amount']
        if 'deductionamount' in obj_deb:
            self.deductionamount=obj_deb['deductionamount']
        if 'debittotal' in obj_deb:
            self.debittotal=obj_deb['debittotal']
        if 'bsproduct' in obj_deb:
            self.bsproduct=obj_deb['bsproduct']

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
    def get_bsproduct(self):
        return self.bsproduct

class ccbsdtlrequest:
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
            self.cc_code=obj_ccbs['cc_code']
        if 'bs_code' in obj_ccbs:
            self.bs_code=obj_ccbs['bs_code']
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

