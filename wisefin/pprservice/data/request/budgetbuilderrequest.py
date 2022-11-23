class budgetbuilderrequest:
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
    future_bgtamount = None
    supplier_id = None
    subcat_id = None
    status = None
    quarter = None
    status_id = None
    remark_key=None
    def __init__(self, budgetheader):
        if 'branch_id' in budgetheader:
            self.branch_id = budgetheader['branch_id']
        if 'finyear' in budgetheader:
            self.finyear = budgetheader['finyear']
        if 'year_term' in budgetheader:
            self.year_term = budgetheader['year_term']
        if 'divAmount' in budgetheader:
            if budgetheader['divAmount'] == 'K':
                self.divAmount = 1000
            if budgetheader['divAmount'] == 'L':
                self.divAmount = 100000
        if 'sectorname' in budgetheader:
            self.sector_name = budgetheader['sectorname']
        if 'masterbusinesssegment_name' in budgetheader:
            self.mstbussinesssegment_name = budgetheader['masterbusinesssegment_name']
        if 'bs_name' in budgetheader:
            self.bs_name = budgetheader['bs_name']
        if 'cc_name' in budgetheader:
            self.cc_name = budgetheader['cc_name']
        if 'expensegrp_name_arr' in budgetheader:
            self.expensegrp_name_arr = budgetheader['expensegrp_name_arr']
        if 'expense_id' in budgetheader:
            self.expense_id = budgetheader['expense_id']
        if 'supplier_id' in budgetheader:
            self.supplier_id = budgetheader['supplier_id']
        if 'future_bgtamount' in budgetheader:
            self.future_bgtamount = budgetheader['future_bgtamount']
        if 'subcat_id' in budgetheader:
            self.subcat_id = budgetheader['subcat_id']
        if 'status' in budgetheader:
            self.status = budgetheader['status']
        if 'quarter' in budgetheader:
            self.quarter = budgetheader['quarter']
        if 'transactionmonth' in budgetheader:
            self.transactionmonth = budgetheader['transactionmonth']
        if 'transactionyear' in budgetheader:
            self.transactionyear = budgetheader['transactionyear']
        if 'status_id' in budgetheader:
            self.status_id = budgetheader['status_id']
        if 'remark_key' in budgetheader:
            self.remark_key = budgetheader['remark_key']
        if 'expense_grp_id' in budgetheader:
            self.expense_grp_id = budgetheader['expense_grp_id']
        if 'category_id' in budgetheader:
            self.category_id = budgetheader['category_id']


    def get_remark_key(self):
        return self.remark_key
    def get_status_id(self):
        return self.status_id
    def get_transactionyear(self):
        return self.transactionyear
    def get_transactionmonth(self):
        return self.transactionmonth
    def get_quarter(self):
        return self.quarter
    def get_status(self):
        return self.status
    def get_subcat_id(self):
        return self.subcat_id
    def get_supplier_id(self):
        return self.supplier_id
    def get_future_bgtamount(self):
        return self.future_bgtamount
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
    def get_mstbusiness_segment_name(self):
        return self.mstbussinesssegment_name
    def get_bs_name(self):
        return self.bs_name
    def get_cc_name(self):
        return self.cc_name
    def get_expensegrp_name_arr(self):
        return self.expensegrp_name_arr
    def get_expense_id(self):
        return self.expense_id
    def get_expense_grp_id(self):
        return self.expense_grp_id
    def get_category_id(self):
        return self.category_id


