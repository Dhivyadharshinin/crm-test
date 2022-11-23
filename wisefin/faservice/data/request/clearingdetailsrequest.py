import json

class ClearingDetailsRequest:

    id = clearingheader = supplier_id = product_id = branch_id = invoice_id = invoicedtails_id = \
    apsubcat_id = doctype = productname = qty = balanceqty = invoiceno = invoicedate = taxamount = otheramount = \
    amount = totamount = markedup = mepno = ponum = ecfnum = inv_debit_tax=None

    def __init__(self, clearing_data):
        if 'id' in clearing_data:
            self.id = clearing_data['id']
        if 'clearingheader' in clearing_data:
            self.clearingheader = clearing_data['clearingheader']
        if 'supplier_code' in clearing_data:
            self.supplier_id = clearing_data['supplier_code']
        if 'product_code' in clearing_data:
            self.product_id = clearing_data['product_code']
        if 'branch_code' in clearing_data:
            self.branch_id = clearing_data['branch_code']
        if 'invoice_id' in clearing_data:
            self.invoice_id = clearing_data['invoice_id']
        if 'invoicedtails_id' in clearing_data:
            self.invoicedtails_id = clearing_data['invoicedtails_id']
        if 'apsubcat_code' in clearing_data:
            self.apsubcat_id = clearing_data['apsubcat_code']
        if 'Doc_Type' in clearing_data:
            self.doctype = clearing_data['Doc_Type']
        if 'productname' in clearing_data:
            self.productname = clearing_data['productname']
        if 'qty' in clearing_data:
            self.qty = clearing_data['qty']
        if 'balanceqty' in clearing_data:
            self.balanceqty = clearing_data['balanceqty']
        if 'invoiceno' in clearing_data:
            self.invoiceno = clearing_data['invoiceno']
        if 'invoicedate' in clearing_data:
            self.invoicedate = clearing_data['invoicedate']
        if 'taxamount' in clearing_data:
            self.taxamount = clearing_data['taxamount']
        if 'otheramount' in clearing_data:
            self.otheramount = clearing_data['otheramount']
        if 'amount' in clearing_data:
            self.amount = clearing_data['amount']
        if 'totamount' in clearing_data:
            self.totamount = clearing_data['totamount']
        if 'markedup' in clearing_data:
            self.markedup = clearing_data['markedup']
        if 'mepno' in clearing_data:
            self.mepno = clearing_data['mepno']
        if 'ponum' in clearing_data:
            self.ponum = clearing_data['ponum']
        if 'ecfnum' in clearing_data:
            self.ecfnum = clearing_data['ecfnum']
        if 'inv_debit_tax' in clearing_data:
            self.inv_debit_tax = clearing_data['inv_debit_tax']





    def get_id(self):
        return self.id
    def get_clearingheader(self):
        return self.clearingheader
    def get_supplier_id(self):
        return self.supplier_id
    def get_product_id(self):
        return self.product_id
    def get_branch_id(self):
        return self.branch_id
    def get_invoice_id(self):
        return self.invoice_id
    def get_invoicedtails_id(self):
        return self.invoicedtails_id
    def get_apsubcat_id(self):
        return self.apsubcat_id
    def get_doctype(self):
        return self.doctype
    def get_productname(self):
        return self.productname
    def get_qty(self):
        return self.qty
    def get_balanceqty(self):
        return self.balanceqty
    def get_invoiceno(self):
        return self.invoiceno
    def get_invoicedate(self):
        return self.invoicedate
    def get_taxamount(self):
        return self.taxamount
    def get_otheramount(self):
        return self.otheramount
    def get_amount(self):
        return self.amount
    def get_totamount(self):
        return self.totamount
    def get_markedup(self):
        return self.markedup
    def get_mepno(self):
        return self.mepno
    def get_ponum(self):
        return self.ponum
    def get_ecfnum(self):
        return self.ecfnum
    def get_inv_debit_tax(self):
        return self.inv_debit_tax

