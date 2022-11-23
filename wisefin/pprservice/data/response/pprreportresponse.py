import json


class pprresponse:
    finyear = None
    quarter = None
    transactionmonth = None
    transactionyear = None
    transactiondate = None
    valuedate = None
    apinvoice_id = None
    apinvoicebranch_id = None
    apinvoicesupplier_id = None
    apinvoicedetails_id = None
    cc_code=None
    bs_code=None
    bsname = None
    ccname = None
    bizname = None
    sectorname = None
    amount = None
    taxamount = None
    otheramount = None
    totalamount = None
    cat_id = None
    subcat_id = None
    expense_id = None
    categoryname = None
    expensename = None
    expensegrpname = None
    subcategoryname = None
    cc_codename=None
    bs_codename=None
    expensegrp_id = None
    status = None
    remark_key = None


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_finyear(self, finyear):
        self.finyear = finyear

    def set_quarter(self, quarter):
        self.quarter = quarter

    def set_transactionmonth(self, transactionmonth):
        self.transactionmonth = transactionmonth

    def set_transactionyear(self, transactionyear):
        self.transactionyear = transactionyear

    def set_transactiondate(self, transactiondate):
        self.transactiondate = transactiondate

    def set_valuedate(self, valuedate):
        self.valuedate = valuedate

    def set_apinvoiceid(self, apinvoice_id):
        self.apinvoice_id = apinvoice_id

    def set_apinvoicebranchid(self, apinvoicebranch_id):
        self.apinvoicebranch_id = apinvoicebranch_id

    def set_apinvoicesupplierid(self, apinvoicesupplier_id):
        self.apinvoicesupplier_id = apinvoicesupplier_id

    def set_apinvoicedetailsid(self, apinvoicedetails_id):
        self.apinvoicedetails_id = apinvoicedetails_id

    def set_cccode(self,cc_code):
        self.cc_code = cc_code

    def set_bscode(self,bs_code):
        self.bs_code = bs_code

    def set_bsname(self, bsname):
        self.bsname = bsname

    def set_ccname(self, ccname):
        self.ccname = ccname

    def set_bizname(self, bizname):
        self.bizname = bizname

    def set_sectorname(self, sectorname):
        self.sectorname = sectorname

    def set_amount(self, amount):
        self.amount = amount

    def set_taxamount(self, taxamount):
        self.taxamount = taxamount

    def set_otheramount(self, otheramount):
        self.otheramount = otheramount

    def set_totalamount(self, totalamount):
        self.totalamount = totalamount

    def set_catid(self,cat_id):
        self.cat_id=cat_id

    def set_apsubcatid(self, subcat_id):
        self.subcat_id = subcat_id

    def set_apexpenseid(self, expense_id):
        self.expense_id = expense_id

    def set_category(self, category):
        self.categoryname = category

    def set_expensename(self, expensename):
        self.expensename = expensename

    def set_expensegrpname(self, expensegrpname):
        self.expensegrpname = expensegrpname

    def set_subcategory(self, subcategory):
        self.subcategoryname = subcategory

    def set_future_bgtamount(self,future_bgtamount):
        self.future_bgtamount = future_bgtamount

    def set_bgtamount(self,bgtamount):
        self.bgtamount=bgtamount

    def set_status(self,status):
        self.status = status

    def set_remark_key(self,remark_key):
        self.remark_key = remark_key

    def set_subcat_cat_data(self,arr,subcat_id):
        for i in arr:
            if i['subcat_id'] == subcat_id:
                self.subcat_id = i['subcat_id']
                self.cat_id = i['category_id']
                self.subcategoryname = i['subcat_name']
                self.expense_id = i['expense_id']

    def set_expense_data(self,arr,expense_id):
        for i in arr:
            if i['expense_id'] == expense_id:
                self.expense_id = i['expense_id']
                self.expensename = i['expense_head']
                self.expensegrpname = i['expense_group']
                self.expense_id = i['expense_id']

    def set_expense_datacheck(self,arr,expense_id):
        for i in arr:
            if i['expense_id'] == expense_id:
                return True
    def set_cc_codename(self,cc_code,arr):
        data_arr = []
        for i in arr:
            if i['code']==cc_code:
                data_arr=i
        self.cc_data=data_arr

    def set_bs_codename(self,bs_code,arr):
        data_arr = []
        for i in arr:
            if i['code']==bs_code:
                data_arr=i
        self.bs_data=data_arr

    def set_cat_data(self,arr,cat_id):
        for i in arr:
            if int(i['cat_id']) == int(cat_id):
                self.cat_id = i['cat_id']
                self.categoryname = i['categoryname']
                self.expense_id = i['expense_id']

    def set_subcat_data(self,arr,subcat_id):
        for i in arr:
            if i['subcat_id'] == subcat_id:
                self.subcat_id = i['subcat_id']
                self.cat_id = i['category_id']
                self.subcategoryname = i['subcat_name']
                self.expense_id = i['expense_id']

    def set_expensegrp_id(self,expensegrp_id):
        self.expensegrp_id = expensegrp_id

    def set_new_cat(self,arr,cat_id):
        for i in arr:
            if int(i['cat_id']) == int(cat_id):
                self.cat_id = i['cat_id']
                self.categoryname = i['categoryname']
                self.expense_id = i['expense_id']

class PPRlogresonse:
    id = None
    range_from = None
    range_to = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self,id):
        self.id = id

    def set_range_from(self,range_from):
        self.range_from = range_from

    def set_range_to(self,range_to):
        self.range_to = range_to

class PPRecfresponse:
    file_reftablegid=file_isduplicate=file_gid=file_name=file_path=ref_name=cr_no=invoiceheaderid=None

    def get(self):
        return self.__dict__

    def set_file_reftablegid(self, file_reftablegid):
        self.file_reftablegid = file_reftablegid

    def set_file_isduplicate(self, file_isduplicate):
        self.file_isduplicate = file_isduplicate

    def set_file_gid(self, file_gid):
        self.file_gid = file_gid

    def set_file_name(self, file_name):
        self.file_name = file_name

    def set_file_path(self, file_path):
        self.file_path = file_path

    def set_ref_name(self, ref_name):
        self.ref_name = ref_name

    def set_cr_no(self, cr_no):
        self.cr_no = cr_no

    def set_invoiceheaderid(self, invoiceheaderid):
        self.invoiceheaderid = invoiceheaderid
