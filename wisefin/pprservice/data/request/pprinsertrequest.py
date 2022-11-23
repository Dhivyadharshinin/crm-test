import datetime
import json

class pprinrequest:
    finyear = None
    quarter = None
    month = None
    year = None
    trndate = None
    valuedate = None
    invoiceid = None
    branchid = None
    supplierid = None
    invoicedetialid = None
    subcatid = None
    expenseid = None
    bs_code = None
    cc_code = None
    bsname = None
    ccname = None
    bussinessname = None
    sectorname = None
    amount = None
    taxamount = None
    otheramount = 0
    totalamount = None
    create_by = None
    status = 1
    cat_id = None
    ccbsdtl_bs = None
    ccbsdtl_cc = None
    entry_module = None
    entry_crno = None
    fas_flag = None

    def __init__(self, pprheader,ids):
        if 'tran_FinYear' in pprheader:
            self.finyear = pprheader["tran_FinYear"]
        if 'tran_quarter' in pprheader:
            self.quarter = pprheader["tran_quarter"]
        if 'tran_month' in pprheader:
            self.month = pprheader["tran_month"]
        if 'tran_year' in pprheader:
            self.year = pprheader["tran_year"]
        if 'entry_transactiondate' in pprheader:
            self.trndate = pprheader["entry_transactiondate"]
            self.valuedate = pprheader["entry_transactiondate"]
        if 'invoiceheader_gid' in pprheader:
            self.invoiceid = pprheader["invoiceheader_gid"]
        if 'invoiceheader_branchgid' in pprheader:
            for i in ids["branch"]:
                if i.code == pprheader["invoiceheader_branchgid"]:
                    self.branchid = i.id
        if 'invoiceheader_suppliergid' in pprheader:
            for i in ids["supplier"]:
                if i.code == pprheader["invoiceheader_suppliergid"]:
                    self.supplierid = i.id
        if 'invoicedetails_gid' in pprheader:
            self.invoicedetialid = pprheader["invoicedetails_gid"]
        if 'debit_subcategorygid' in pprheader:
            for i in ids["subcategory"]:
                if i.code == pprheader["subcategory_code"] and i.category.code == pprheader["category_code"]:
                    self.subcatid = i.id
        if 'expense_gid' in pprheader:
            for i in ids["expense"]:
                if i.code == pprheader["expense_gid"]:
                    self.expenseid = i.id
        if 'tbs_code' in pprheader:
            for i in ids["bs"]:
                if i.code == pprheader["tbs_code"]:
                    self.bs_code = i.id
        if 'tcc_code' in pprheader:
            for i in ids['cc']:
                if i.code == pprheader["tcc_code"]:
                    self.cc_code = i.id
        if 'tbs_name' in pprheader:
            self.bsname = pprheader["tbs_name"]
        if 'tcc_name' in pprheader:
            self.ccname = pprheader["tcc_name"]
        if 'businesssegment_name' in pprheader:
            self.bussinessname = pprheader["businesssegment_name"]
        if 'invoicedetails_amount' in pprheader:
            self.amount = pprheader['invoicedetails_amount']
        if 'invoiceheader_amount' in pprheader:
            self.otheramount = pprheader["invoiceheader_amount"]
        if 'pprdata_taxamount' in pprheader:
            self.taxamount = pprheader["pprdata_taxamount"]
        if 'invoicedetails_totalamt' in pprheader:
            self.totalamount = pprheader["invoicedetails_totalamt"]
        if 'ccbsdtl_amount' in pprheader:
            self.otheramount = pprheader["ccbsdtl_amount"]
        if 'debit_categorygid' in pprheader:
            for i in ids["category"]:
                if i.code == pprheader["category_code"]:
                    self.cat_id = i.id
        if 'ccbsdtl_bs' in pprheader:
            self.ccbsdtl_bs = pprheader["ccbsdtl_bs"]
        if 'ccbsdtl_cc' in pprheader:
            self.ccbsdtl_cc = pprheader["ccbsdtl_cc"]
        if 'entry_module' in pprheader:
            self.entry_module = pprheader["entry_module"]
        if 'entry_crno' in pprheader:
            self.entry_crno = pprheader["entry_crno"]
        if 'create_by' in pprheader:
            self.create_by = pprheader["create_by"]
        if 'fas_flag' in pprheader:
            self.fas_flag = pprheader["fas_flag"]
        if 'sectorname' in pprheader:
            self.sectorname = pprheader['sectorname']

    def set_create_by(self,create_by):
        self.create_by = create_by

    def get_cat_id(self):
        return self.cat_id

    def get_ccbsdtl_bs(self):
        return self.ccbsdtl_bs

    def get_ccbsdtl_cc(self):
        return self.ccbsdtl_cc

    def get_entry_module(self):
        return self.entry_module

    def get_entry_crno(self):
        return self.entry_crno

    def get_finyear(self):
        return self.finyear

    def get_quarter(self):
        return self.quarter

    def get_month(self):
        return self.month

    def get_year(self):
        return self.year

    def get_trndate(self):
        return self.trndate.split("T")[0]

    def get_valuedate(self):
        return self.valuedate.split("T")[0]

    def get_invoiceid(self):
        return self.invoiceid

    def get_branchid(self):
        return self.branchid

    def get_supplierid(self):
        return self.supplierid

    def get_invoicedetialid(self):
        return self.invoicedetialid

    def get_subcatid(self):
        return self.subcatid

    def get_expenseid(self):
        return self.expenseid

    def get_bs_code(self):
        return self.bs_code

    def get_cc_code(self):
        return self.cc_code

    def get_bsname(self):
        return self.bsname

    def get_ccname(self):
        return self.ccname

    def get_bussinessname(self):
        return self.bussinessname

    def get_sectorname(self):
        return self.sectorname

    def get_amount(self):
        return self.amount

    def get_taxamount(self):
        return self.taxamount

    def get_otheramount(self):
        return self.otheramount

    def get_totalamount(self):
        return self.totalamount

    def get_createby(self):
        return self.create_by

    def get_status(self):
        return self.status

    def get_fas_flag(self):
        return self.fas_flag


class PPRlogrequest:
    maindata = None
    range_from = None
    range_to = None
    current_datetime = None

    def __init__(self, pprlogdata, range_from, range_to, current_datetime):
        if "DATA" in pprlogdata:
            self.maindata = pprlogdata["DATA"][0]
        if range_from != "":
            self.range_from = range_from
        if range_to != "":
            self.range_to = range_to
        if current_datetime != "":
            self.current_datetime = current_datetime

    def get_maindata(self):
        return self.maindata

    def get_range_from(self):
        return self.range_from

    def get_range_to(self):
        return self.range_to

    def get_current_datetime(self):
        return self.current_datetime