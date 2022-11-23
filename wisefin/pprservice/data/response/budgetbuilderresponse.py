import json
from decimal import Decimal

class BudgetBuilderresponse:
    id = None
    finyear = None
    quarter = None
    transactionmonth = None
    transactionyear = None
    transactiondate = None
    apinvoicebranch_id = None
    sectorname = None
    bizname = None
    bsname = None
    ccname = None
    apsubcat_glno = None
    pprline = None
    apexpense_id = None
    expense_id = None
    expensegrpname = None
    expensename = None
    apcat_id = None
    cat_id = None
    apsubcat_id = None
    subcat_id = None
    categoryname = None
    subcategoryname = None
    ppramount = Decimal(0.00)
    bgtamount = Decimal(0.00)
    supplier_id = None
    supplier_name = None
    supplier_code = None
    supplier_branchname = None
    supplier_panno = None
    supplier_gstno = None
    totamount = None
    future_bgtamount = None
    expense_id = None
    status = None
    remark_key = None
    expensegrp_id = None


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_remark_key(self, remark_key):
        self.remark_key = remark_key

    def set_status(self, status):
        self.status = status

    def set_id(self,id):
        self.id = id
    def set_finyear(self,finyear):
        self.finyear = finyear
    def set_quarter(self,quarter):
        self.quarter = quarter
    def set_transactionmonth(self,transactionmonth):
        self.transactionmonth = transactionmonth
    def set_transactionyear(self,transactionyear):
        self.transactionyear= transactionyear
    def set_transactiondate(self,transactiondate):
        self.transactiondate=transactiondate
    def set_apinvoicebranch_id(self,apinvoicebranch_id):
        self.apinvoicebranch_id = apinvoicebranch_id
    def set_sectorname(self,sectorname):
        self.sectorname= sectorname
    def set_bizname(self,bizname):
        self.bizname = bizname
    def set_bsname(self,bsname):
        self.bsname=bsname
    def set_ccname(self,ccname):
        self.ccname = ccname
    def set_apcat_id(self,apcat_id):
        self.apcat_id=apcat_id
    def set_apsubcat_id(self,apsubcat_id):
        self.apsubcat_id=apsubcat_id
    def set_apsubcat_glno(self,apsubcat_glno):
        self.apsubcat_glno=apsubcat_glno
    def set_apexpense_id(self,apexpense_id):
        self.apexpense_id=apexpense_id
    def set_expense_id(self,expense_id):
        self.expense_id=expense_id

    def set_pprline(self,pprline):
        self.pprline=pprline
    def set_ppramount(self,ppramount):
        self.ppramount=ppramount

    def set_bgtamount(self,bgtamount):
        self.bgtamount=bgtamount

    def set_future_bgtamount(self,future_bgtamount):
        self.future_bgtamount = future_bgtamount

    def set_totamount(self, totamount):
        self.totamount = totamount

    def set_expensegrp_id(self,expensegrp_id):
        self.expensegrp_id = expensegrp_id


    def set_expense_detial(self,arr,expense_id):
        for i in arr:
            if i['expense_id'] == expense_id:
                self.apexpense_id = i['expense_id']
                self.expensename = i['expense_head']
                self.expensegrpname = i['expense_group']

    def set_expense_detial_future(self,arr,expense_id):
        for i in arr:
            if i['expense_id'] == expense_id:
                self.expense_id = i['expense_id']
                self.expensename = i['expense_head']
                self.expensegrpname = i['expense_group']

    def set_subcat_datials(self,arr,subcat_id):
        for i in arr:
            if i['subcat_id'] == subcat_id:
                self.apsubcat_id = i['subcat_id']
                self.subcategoryname = i['subcat_name']
                self.apcat_id = i['category_id']
                self.categoryname = i['category_name']

    def set_subcat_datials_future(self,arr,subcat_id):
        for i in arr:
            if i['subcat_id'] == subcat_id:
                self.subcat_id = i['subcat_id']
                self.subcategoryname = i['subcat_name']
                self.cat_id = i['category_id']
                self.categoryname = i['category_name']

    def set_supplier_detial(self,supplier_detial,bgt_supplier_id):
        if bgt_supplier_id == 0:
            self.supplier_id = 0
            self.supplier_name = 'OTHERS'
            self.supplier_code = "SU0000000"
            self.supplier_branchname = 'dummy'
            self.supplier_panno = ''
            self.supplier_gstno = ''
        elif int(bgt_supplier_id) == -1:
            self.supplier_id = -1
            self.supplier_name = 'TASK'
            self.supplier_code = "SU0000000"
            self.supplier_branchname = 'dummy'
            self.supplier_panno = ''
            self.supplier_gstno = ''
        else:
            for i in supplier_detial:
                if bgt_supplier_id == i['supplier_id']:
                    self.supplier_id = i['supplier_id']
                    self.supplier_name = i['supplier_name']
                    self.supplier_code = i['supplier_code']
                    self.supplier_branchname = i['supplier_branchname']
                    self.supplier_panno = i['supplier_panno']
                    self.supplier_gstno = i['supplier_gstno']

    def set_budget_status(self, status):
        if status == 1:
            self.status = 'Draft'
            self.id = status
        elif status == 2:
            self.status = 'Maker-Initiated'
            self.id = status
        elif status == 3:
            self.status = 'Checked'
            self.id = status
        elif status == 4:
            self.status = 'Approved'
            self.id = status
        elif status == 6:
            self.status = 'Rejected'
            self.id = status




class EmployeeBranchresponse:
    id = None
    code = None
    name = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self,id):
        self.id = id
    def set_code(self,code):
        self.code=code
    def set_name(self,name):
        self.name=name


class BudgetRemarkResponse:
    module = username = remark = remark_key = created_date = status =  None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_module(self, module):
        self.module = module

    def set_username(self, username):
        self.username = username

    def set_user_data(self,arr,id):
        for i in arr:
            if int(i['id']) == int(id):
                self.username=f"({i['code']}) {i['full_name']}"

    def set_remark(self, remark):
        self.remark = remark

    def set_remark_key(self, remark_key):
        self.remark_key = remark_key

    def set_created_date(self, created_date):
        self.created_date = created_date

    def set_status(self,module):
        if module == 'Budget Draft':
            self.status = 'Saved in Draft'
        if module == 'Budget Maker':
            self.status = 'Budget-Initiated'
        if module == 'Budget Approver':
            self.status = 'Budget-Approved'
        if module == 'Budget Reject':
            self.status = 'Budget-Rejected'

class budget_reject_response:
    message = status = None

    branch_message = "The budget for this branch is already Done by superuser"
    status_message = "Failed"

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_message(self, message):
        self.message = message

    def set_status(self, status):
        self.status = status