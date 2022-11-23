

class FasResponse:
    finyear = ccbs_name=ccbs_code=expensename = expensegrpname = quarter = transactionmonth = transactionyear = transactiondate = cc_code = bs_code = bsname = ccname = bizname = sectorname = income_amount = cat_id = cat_name = branch_id = subcat_id = subcat_name = expense_id = expense_name = expensegrp_name= account_no = level_id = level_name = DRCR_IN = None

    def get(self):
        return self.__dict__

    def set_ccbs_name(self, ccbs_name):
        self.ccbs_name = ccbs_name

    def set_ccbs_code(self, ccbs_code):
        self.ccbs_code = ccbs_code

    def set_ccbs_data(self,bs_id,cc_id,arr):
        for i in arr:
            if int(bs_id) == int(i["businesssegment"]) and int(cc_id) == int(i["costcentre"]):
                self.ccbs_name = i['name']
                self.ccbs_code = i['code']

    def set_finyear(self, finyear):
        self.finyear = finyear

    def set_level_id(self, level_id):
        self.level_id = level_id

    def set_quarter(self, quarter):
        self.quarter = quarter

    def set_transactionmonth(self, transactionmonth):
        self.transactionmonth = transactionmonth

    def set_transactionyear(self, transactionyear):
        self.transactionyear = transactionyear

    def set_transactiondate(self, transactiondate):
        self.transactiondate = transactiondate

    def set_cc_code(self, cc_code):
        self.cc_code = cc_code

    def set_bs_code(self, bs_code):
        self.bs_code = bs_code

    def set_bsname(self, bsname):
        self.bsname = bsname

    def set_ccname(self, ccname):
        self.ccname = ccname

    def set_bizname(self, bizname):
        self.bizname = bizname

    def set_sectorname(self, sectorname):
        self.sectorname = sectorname

    def set_income_amount(self, income_amount):
        self.income_amount = income_amount

    def set_cat_id(self, cat_id):
        self.cat_id = cat_id

    def set_cat_name(self, cat_name):
        self.cat_name = cat_name

    def set_branch_id(self, branch_id):
        self.branch_id = branch_id

    def set_subcat_id(self, subcat_id):
        self.subcat_id = subcat_id

    def set_subcat_name(self, subcat_name):
        self.subcat_name = subcat_name

    def set_expense_id(self, expense_id):
        self.expense_id = expense_id

    def set_expense_name(self, expense_name):
        self.expense_name = expense_name

    def set_expensegrp_name(self, expensegrp_name):
        self.expensegrp_name = expensegrp_name

    def set_account_no(self, account_no):
        self.account_no = account_no

    def set_level_name(self, level_name):
        self.level_name = level_name

    def set_DRCR_IN(self, DRCR_IN):
        self.DRCR_IN = DRCR_IN

    def set_expense_data(self, arr, expense_id):
        for i in arr:
            if i['expense_id'] == expense_id:
                self.expense_id = i['expense_id']
                self.expensename = i['expense_head']
                self.expensegrpname = i['expense_group']

    def set_cat_data(self,arr,cat_id):
        for i in arr:
            if i['id'] == cat_id:
                self.cat_id=i['id']
                self.cat_name=i['name']

    def set_subcat_data(self,arr,subcat_id):
        for i in arr:
            if i['subcat_id'] == subcat_id:
                self.subcat_id=i['subcat_id']
                self.subcat_name=i['subcat_name']

    def set_level_data(self,arr,level_id):
        for i in arr:
            if i['id'] == level_id:
                self.level_id=i['id']
                self.level_name=f"LEVEL-{i['id']} {i['name']}"