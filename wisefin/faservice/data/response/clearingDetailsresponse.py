import json
from datetime import datetime

from faservice.util.fautil import get_clearingheader_status

class ClearingDetailsResponse:

    id = clearingheader = supplier_id = product_id = branch_id = invoice_id = invoicedtails_id = \
    apsubcat_id = doctype = productname = qty = balanceqty = invoiceno = invoicedate = taxamount = otheramount = \
    amount = totamount = markedup = mepno = ponum = ecfnum = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id
    def set_clearingheader(self, clearingheader):
        self.clearingheader = clearingheader
    def set_supplier_id(self, supplier_id):
        self.supplier_id = supplier_id
    def set_product_id(self, product_id):
        self.product_id =product_id
    def set_branch_id(self, branch_id):
        self.branch_id = branch_id
    def set_invoice_id(self, invoice_id):
        self.invoice_id = invoice_id
    def set_invoicedtails_id(self, invoicedtails_id):
        self.invoicedtails_id = invoicedtails_id
    def set_apsubcat_id(self, apsubcat_id):
        self.apsubcat_id =apsubcat_id
    def set_doctype(self, doctype):
        self.doctype = doctype
    def set_productname(self, productname):
        self.productname = productname
    def set_qty(self, qty):
        self.qty = str(qty)
    def set_balanceqty(self, balanceqty):
        self.balanceqty = str(balanceqty)
    def set_invoiceno(self, invoiceno):
        self.invoiceno =invoiceno
    def set_invoicedate(self, invoicedate):
        self.invoicedate = str(invoicedate)
    def set_taxamount(self, taxamount):
        self.taxamount = str(taxamount)
    def set_otheramount(self, otheramount):
        self.otheramount = str(otheramount)
    def set_amount(self, amount):
        self.amount = str(amount)
    def set_totamount(self, totamount):
        self.totamount =str(totamount)
    def set_markedup(self, markedup):
        self.markedup = str(markedup)
    def set_mepno(self, mepno):
        self.mepno = mepno
    def set_ponum(self, ponum):
        self.ponum = ponum
    def set_ecfnum(self, ecfnum):
        self.ecfnum = ecfnum

    def set_clearingheader_id(self, clearingheader_id):
        self.clearingheader_id = clearingheader_id
    def set_assettype(self, assettype):
        self.assettype = assettype
    def set_invoicecount(self, invoicecount):
        self.invoicecount = invoicecount
    def set_totinvoiceamount(self, totinvoiceamount):
        self.totinvoiceamount =str(totinvoiceamount)
    def set_tottaxamount(self, tottaxamount):
        self.tottaxamount = str(tottaxamount)
    # def set_totamount(self, totamount):
    #     self.totamount = str(totamount)
    def set_captalizedamount(self, captalizedamount):
        self.captalizedamount = str(captalizedamount)
    def set_balanceamount(self, balanceamount):
        self.balanceamount =str(balanceamount)
    def set_groupno(self, groupno):
        self.groupno = groupno
    def set_remarks(self, remarks):
        self.remarks = remarks
    def set_clearingheader_status(self, clearingheader_status):
        self.clearingheader_status = get_clearingheader_status(clearingheader_status)
    def set_supplier_name(self, param):
        self.supplier_name=param
        pass


class ClearingDetailsCapitalizeResponse:
    faclringheader_balanceqty=crnum=isChecked=isChecked_apportion=faclringheader_gid=faclringdetails_gid=faclringdetails_productgid=faclringdetails_productname=faclrance_qty=faclringdetails_qty=faclringheader_totamount=faclringheader_tottaxamount=faclringheader_totinvamount=product_name=branch_name=supplier_name=inv_debit_tax=invoicedetails_totalamt=faclringdetails_ponum=faclringheader_captalizedamount=faclringheader_balanceamount=faclringheader_expenseamount=lifetime=images=id=nobillChecked=billChecked=files=None

    def set_isChecked(self, isChecked):
        self.isChecked = isChecked

    def set_isChecked_apportion(self, isChecked_apportion):
        self.isChecked_apportion = isChecked_apportion

    def set_faclringheader_gid(self, faclringheader_gid):
        self.faclringheader_gid = faclringheader_gid

    def set_faclringdetails_gid(self, faclringdetails_gid):
        self.faclringdetails_gid = faclringdetails_gid

    def set_faclringdetails_productgid(self, faclringdetails_productgid):
        self.faclringdetails_productgid = faclringdetails_productgid

    def set_faclringdetails_productname(self, faclringdetails_productname):
        self.faclringdetails_productname = faclringdetails_productname

    def set_faclrance_qty(self, faclrance_qty):
        self.faclrance_qty = faclrance_qty

    def set_faclringdetails_qty(self, faclringdetails_qty):
        self.faclringdetails_qty = faclringdetails_qty

    def set_faclringheader_totamount(self, faclringheader_totamount):
        self.faclringheader_totamount = faclringheader_totamount

    def set_faclringdetail_totamount(self, faclringdetail_totamount):
        self.faclringdetail_totamount = faclringdetail_totamount

    def set_faclringheader_tottaxamount(self, faclringheader_tottaxamount):
        self.faclringheader_tottaxamount = faclringheader_tottaxamount

    def set_faclringheader_totinvamount(self, faclringheader_totinvamount):
        self.faclringheader_totinvamount = faclringheader_totinvamount

    def set_product_name(self, product_name):
        self.product_name = product_name

    def set_branch_name(self, branch_name):
        self.branch_name = branch_name

    def set_supplier_name(self, supplier_name):
        self.supplier_name = supplier_name

    def set_inv_debit_tax(self, inv_debit_tax):
        self.inv_debit_tax = inv_debit_tax

    def set_invoicedetails_totalamt(self, invoicedetails_totalamt):
        self.invoicedetails_totalamt = invoicedetails_totalamt

    def set_faclringdetails_ponum(self, faclringdetails_ponum):
        self.faclringdetails_ponum = faclringdetails_ponum

    def set_faclringheader_captalizedamount(self, faclringheader_captalizedamount):
        self.faclringheader_captalizedamount = faclringheader_captalizedamount

    def set_faclringheader_balanceamount(self, faclringheader_balanceamount):
        self.faclringheader_balanceamount = faclringheader_balanceamount

    def set_faclringheader_balanceqty(self, faclringheader_balanceqty):
        self.faclringheader_balanceqty = faclringheader_balanceqty

    def set_faclringheader_expenseamount(self, faclringheader_expenseamount):
        self.faclringheader_expenseamount = faclringheader_expenseamount

    def set_lifetime(self, lifetime):
        self.lifetime = lifetime

    def set_images(self, images):
        self.images = images

    def set_id(self, id):
        self.id = id

    def set_crnum(self, id):
        self.crnum = id

    def set_nobillChecked(self, nobillChecked):
        self.nobillChecked = nobillChecked

    def set_billChecked(self, billChecked):
        self.billChecked = billChecked

    def set_files(self, files):
        self.files = files
    def get(self):
        return self.__dict__

