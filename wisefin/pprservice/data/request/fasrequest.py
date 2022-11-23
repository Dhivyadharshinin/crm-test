


class FasRequest:
    finyear = divAmount = yearterm = quarter = hr_amount = transactionmonth = transactionyear = transactiondate = cc_code = bs_code = bsname = ccname = bizname = sectorname = income_amount = cat_id = branch_id = subcat_id = expense_id = account_no = level = DRCR_IN = None
    expensegrp = []

    level_id=expensegrp_individual=None
    def __init__(self, data,dict_arr={}):
        if 'hr_amount' in data:
            self.hr_amount = data['hr_amount']
        if 'expensegrp_individual' in data:
            self.expensegrp_individual = data['expensegrp_individual']
        if 'level_id' in data:
            self.level_id = data['level_id']
        if 'divAmount' in data:
            if data['divAmount'] == 'K':
                self.divAmount = 1000
            if data['divAmount'] == 'L':
                self.divAmount = 100000
        if 'yearterm' in data:
            self.yearterm = data['yearterm']
        if 'finyear' in data:
            self.finyear = data['finyear']
        if 'expensegrp' in data:
            self.expensegrp = data['expensegrp']
        if 'quarter' in data:
            self.quarter = data['quarter']
        if 'transactionmonth' in data:
            self.transactionmonth = data['transactionmonth']
        if 'transactionyear' in data:
            self.transactionyear = data['transactionyear']
        if 'transactiondate' in data:
            self.transactiondate = data['transactiondate']
        if 'cc_code' in data:
            if "cc_id" in dict_arr:
                for i in dict_arr["cc_id"]:
                    if int(i["code"]) == int(data['cc_code']):
                        self.cc_code = i["id"]
                        self.ccname = i["name"]
            else:
                self.cc_code = data['cc_code']

        if 'bs_code' in data:
            if 'bs_id' in dict_arr:
                for i in dict_arr["bs_id"]:
                    if int(i["code"]) == int(data['bs_code']):
                        self.bs_code = i["id"]
                        self.bsname = i["name"]
            else:
                self.bs_code = data['bs_code']
        if len(dict_arr) <= 0:
            if 'bsname' in data:
                self.bsname = data['bsname']
            if 'ccname' in data:
                self.ccname = data['ccname']

        if 'bizname' in data:
            self.bizname = data['bizname']
        if 'sectorname' in data:
            self.sectorname = data['sectorname']
        if 'income_amount' in data:
            self.income_amount = data['income_amount']
        if 'cat_id' in data:
            self.cat_id = data['cat_id']
        if 'branch_id' in data:
            self.branch_id = data['branch_id']
        if 'subcat_id' in data:
            self.subcat_id = data['subcat_id']
        if 'expense_id' in data:
            self.expense_id = data['expense_id']
        if 'account_no' in data:
            self.account_no = data['account_no']
        if 'level' in data:
            self.level = data['level']
        if 'DRCR_IN' in data:
            self.DRCR_IN = data['DRCR_IN']

    def get_hr_amount(self):
        return self.hr_amount

    def get_expensegrp_individual(self):
        return self.expensegrp_individual

    def get_level_id(self):
        return self.level_id

    def get_expensegrp(self):
        return self.expensegrp

    def get_divAmount(self):
        return self.divAmount

    def get_yearterm(self):
        return self.yearterm

    def get_finyear(self):
        return self.finyear

    def get_quarter(self):
        return self.quarter

    def get_transactionmonth(self):
        return self.transactionmonth

    def get_transactionyear(self):
        return self.transactionyear

    def get_transactiondate(self):
        return self.transactiondate

    def get_cc_code(self):
        return self.cc_code

    def get_bs_code(self):
        return self.bs_code

    def get_bsname(self):
        return self.bsname

    def get_ccname(self):
        return self.ccname

    def get_bizname(self):
        return self.bizname

    def get_sectorname(self):
        return self.sectorname

    def get_income_amount(self):
        return self.income_amount

    def get_cat_id(self):
        return self.cat_id

    def get_branch_id(self):
        return self.branch_id

    def get_subcat_id(self):
        return self.subcat_id

    def get_expense_id(self):
        return self.expense_id

    def get_account_no(self):
        return self.account_no

    def get_level(self):
        return self.level

    def get_DRCR_IN(self):
        return self.DRCR_IN