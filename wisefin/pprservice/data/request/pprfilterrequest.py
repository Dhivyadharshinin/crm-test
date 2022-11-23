from utilityservice.data.response.nwisefinpage import NWisefinPage


class PPRreportrequest:
    branch_id = None
    finyear = None
    year_term = None
    divAmount = 1000
    sector_name = None
    mstbussinesssegment_name = None
    bs_name = None
    cc_name = None
    expensegrp_name_arr = None
    expense_id = None
    category_id = None


    def __init__(self, pprheader):
        if 'branch_id' in pprheader:
            self.branch_id = pprheader['branch_id']
        if 'finyear' in pprheader:
            self.finyear = pprheader['finyear']
        if 'year_term' in pprheader:
            self.year_term = pprheader['year_term']
        if 'divAmount' in pprheader:
            if pprheader['divAmount'] == 'K':
                self.divAmount = 1000
            if pprheader['divAmount'] == 'L':
                self.divAmount = 100000
        if 'sectorname' in pprheader:
            self.sector_name = pprheader['sectorname']
        if 'masterbusinesssegment_name' in pprheader:
            self.mstbussinesssegment_name = pprheader['masterbusinesssegment_name']
        if 'bs_name' in pprheader:
            self.bs_name = pprheader['bs_name']
        if 'cc_name' in pprheader:
            self.cc_name = pprheader['cc_name']
        if 'expensegrp_name_arr' in pprheader:
            self.expensegrp_name_arr = pprheader['expensegrp_name_arr']
        if 'expense_id' in pprheader:
            self.expense_id = pprheader['expense_id']

        if 'level' in pprheader:
            self.level = pprheader['level']

        if 'category_id' in pprheader:
            self.category_id = pprheader['category_id']

    def get_branch_id(self):
        return self.branch_id

    def get_finyear(self):
        return self.finyear

    def get_year_term(self):
        return self.year_term

    def get_divAmount(self):
        return self.divAmount

    def get_sector_name(self):
        return self.sector_name
    def get_mstbusiness_segment_name(self,):
        return self.mstbussinesssegment_name
    def get_bs_name(self):
        return self.bs_name
    def get_cc_name(self):
        return self.cc_name
    def get_expense_id(self):
        return self.expense_id
    def get_expensegrp_name_arr(self):
        return self.expensegrp_name_arr
    def get_level(self):
        return self.level
    def get_category_id(self):
        return self.category_id


class PPRsupplierrequest:
    finyear = None
    apexpense_id = None
    apsubcat_id = None
    transactionmonth = None
    quarter = None
    masterbusinesssegment_name = None
    apinvoicebranch_id = None
    sectorname = None
    apinvoicesupplier_id = None
    yearterm = None
    page = 1
    bs_name = None
    cc_name = None
    divAmount = 1000
    cr_no = None
    supplier_id = None
    status_id = None

    def __init__(self,supplier_obj):
        if 'cr_no' in supplier_obj:
            self.cr_no = supplier_obj['cr_no']
        if 'invoiceheader_gid' in supplier_obj:
            self.invoiceheader_gid = supplier_obj['invoiceheader_gid']
        if 'apexpense_id' in supplier_obj:
            self.apexpense_id = supplier_obj['apexpense_id']
        if 'apsubcat_id' in supplier_obj:
            self.apsubcat_id = supplier_obj['apsubcat_id']
        if 'transactionmonth' in supplier_obj:
            self.transactionmonth = supplier_obj['transactionmonth']
        if 'quarter' in supplier_obj:
            self.quarter = supplier_obj['quarter']
        if 'masterbusinesssegment_name' in supplier_obj:
            self.masterbusinesssegment_name = supplier_obj['masterbusinesssegment_name']
        if 'sectorname' in supplier_obj:
            self.sectorname = supplier_obj['sectorname']
        if 'apinvoicesupplier_id' in supplier_obj:
            self.apinvoicesupplier_id = supplier_obj['apinvoicesupplier_id']
        if 'apinvoicebranch_id' in supplier_obj:
            self.apinvoicebranch_id = supplier_obj["apinvoicebranch_id"]
        if 'finyear' in supplier_obj:
            self.finyear = supplier_obj['finyear']
        if 'bs_name' in supplier_obj:
            self.bs_name = supplier_obj['bs_name']
        if 'cc_name' in supplier_obj:
            self.cc_name = supplier_obj['cc_name']
        if 'yearterm' in supplier_obj:
            self.yearterm = supplier_obj['yearterm']
        if 'divAmount' in supplier_obj:
            if supplier_obj['divAmount'] == 'K':
                self.divAmount = 1000
            if supplier_obj['divAmount'] == 'L':
                self.divAmount = 100000
        if 'page' in supplier_obj:
            self.page = int(supplier_obj['page'])
        if 'supplier_id' in supplier_obj:
            self.supplier_id = supplier_obj['supplier_id']
        if 'status_id' in supplier_obj:
            self.status_id = supplier_obj['status_id']


    def get_status_id(self):
        return self.status_id
    def get_status_id(self):
        return self.status_id
    def get_cr_no(self):
        return self.cr_no
    def get_invoiceheader_gid(self):
        return self.invoiceheader_gid
    def get_finyear(self):
        return self.finyear
    def get_apexpense_id(self):
        return self.apexpense_id
    def get_apsubcat_id(self):
        return self.apsubcat_id
    def get_transactionmonth(self):
        return self.transactionmonth
    def get_quarter(self):
        return self.quarter
    def get_masterbusinesssegment_name(self):
        return self.masterbusinesssegment_name
    def get_sectorname(self):
        return self.sectorname
    def get_apinvoicesupplier_id(self):
        return self.apinvoicesupplier_id
    def get_apinvoicebranch_id(self):
        return self.apinvoicebranch_id
    def get_yearterm(self):
        return self.yearterm
    def get_bs_name(self):
        return self.bs_name
    def get_cc_name(self):
        return self.cc_name
    def get_divAmount(self):
        return self.divAmount
    def get_page(self):
        vys_page = NWisefinPage(self.page, 10)
        return vys_page
    def get_supplier_id(self):
        return self.supplier_id

class Pprccbsrequest:
    finyear = None
    apexpense_id = None
    apsubcat_id = None
    transactionmonth = None
    quarter = None
    masterbusinesssegment_name = None
    sectorname = None
    divAmount = 1000
    yearterm = None
    bs_name = None
    cc_name= None

    def __init__(self, ccbs_obj):
        if 'apexpense_id' in ccbs_obj:
            self.apexpense_id = ccbs_obj['apexpense_id']
        if 'apsubcat_id' in ccbs_obj:
            self.apsubcat_id = ccbs_obj['apsubcat_id']
        if 'transactionmonth' in ccbs_obj:
            self.transactionmonth = ccbs_obj['transactionmonth']
        if 'quarter' in ccbs_obj:
            self.quarter = ccbs_obj['quarter']
        if 'masterbusinesssegment_name' in ccbs_obj:
            self.masterbusinesssegment_name = ccbs_obj['masterbusinesssegment_name']
        if 'sectorname' in ccbs_obj:
            self.sectorname = ccbs_obj['sectorname']
        if 'finyear' in ccbs_obj:
            self.finyear = ccbs_obj['finyear']
        if 'bs_name' in ccbs_obj:
            self.bs_name = ccbs_obj['bs_name']
        if 'cc_name' in ccbs_obj:
            self.cc_name = ccbs_obj['cc_name']
        if 'yearterm' in ccbs_obj:
            self.yearterm = ccbs_obj['yearterm']
        if 'divAmount' in ccbs_obj:
            if ccbs_obj['divAmount'] == 'K':
                self.divAmount = 1000
            if ccbs_obj['divAmount'] == 'L':
                self.divAmount = 100000
    def get_finyear(self):
        return self.finyear
    def get_apexpense_id(self):
        return self.apexpense_id
    def get_apsubcat_id(self):
        return self.apsubcat_id
    def get_transactionmonth(self):
        return self.transactionmonth
    def get_quarter(self):
        return self.quarter
    def get_masterbusinesssegment_name(self):
        return self.masterbusinesssegment_name
    def get_bs_name(self):
        return self.bs_name
    def get_cc_name(self):
        return self.cc_name
    def get_sectorname(self):
        return self.sectorname
    def get_yearterm(self):
        return self.yearterm
    def get_divAmount(self):
        return self.divAmount
