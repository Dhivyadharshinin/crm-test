class ppr_expense_request:
    transactiondate = None
    valuedate = None
    apinvoice_id = None
    apinvoicebranch_id = None
    apinvoicesupplier_id = None
    apinvoicedetails_id = None
    apsubcat_id = None
    apexpense_id = None
    bs_id = None
    cc_id = None
    business_id = None
    product_id = None
    client_id =None
    expensegroup_id = None
    sector_id = None
    amount = None
    taxamount = None
    otheramount = None
    totalamount = None
    categorygid = None
    entry_module = None
    fromdate = None
    from_date = None
    to_date = None
    asset_ref = None
    assest_class = None
    def __init__(self, exp_obj):
        if 'transactiondate' in exp_obj:
            self.transactiondate = exp_obj['transactiondate']
        if 'valuedate' in exp_obj:
            self.valuedate = exp_obj['valuedate']
        if 'apinvoice_id' in exp_obj:
            self.apinvoice_id = exp_obj['apinvoice_id']
        if 'apinvoicebranch_id' in exp_obj:
            self.apinvoicebranch_id = exp_obj['apinvoicebranch_id']
        if 'apinvoicedetails_id' in exp_obj:
            self.apinvoicedetails_id = exp_obj['apinvoicedetails_id']
        if 'apsubcat_id' in exp_obj:
            self.apsubcat_id = exp_obj['apsubcat_id']
        if 'apexpense_id' in exp_obj:
            self.apexpense_id = exp_obj['apexpense_id']
        if 'bs_id' in exp_obj:
            self.bs_id = exp_obj['bs_id']
        if 'cc_id' in exp_obj:
            self.cc_id = exp_obj['cc_id']
        if 'business_id' in exp_obj:
            self.business_id = exp_obj['business_id']
        if 'product_id' in exp_obj:
            self.product_id = exp_obj['product_id']
        if 'client_id' in exp_obj:
            self.client_id = exp_obj['client_id']
        if 'expensegroup_id' in exp_obj:
            self.expensegroup_id = exp_obj['expensegroup_id']
        if 'sector_id' in exp_obj:
            self.sector_id = exp_obj['sector_id']
        if 'amount' in exp_obj:
            self.amount = exp_obj['amount']
        if 'taxamount' in exp_obj:
            self.taxamount = exp_obj['taxamount']
        if 'otheramount' in exp_obj:
            self.otheramount = exp_obj['otheramount']
        if 'totalamount' in exp_obj:
            self.totalamount = exp_obj['totalamount']
        if 'categorygid' in exp_obj:
            self.categorygid = exp_obj['categorygid']
        if 'from_date' in exp_obj:
            self.from_date = exp_obj['from_date']
        if 'to_date' in exp_obj:
            self.to_date = exp_obj['to_date']
        if 'asset_ref' in exp_obj:
            self.asset_ref = exp_obj['asset_ref']
        if 'assest_class' in exp_obj:
            self.assest_class = exp_obj["assest_class"]

    def get_from_date(self):
        return self.from_date

    def get_to_date(self):
        return self.to_date

    def get_expensegroup_id(self):
        return self.expensegroup_id

    def get_apexpense_id(self):
        return self.apexpense_id

    def get_categorygid(self):
        return self.categorygid

    def get_asset_ref(self):
        return self.asset_ref

    def get_product_id(self):
        return self.product_id

    def get_client_id(self):
        return self.client_id

    def get_bs_id(self):
        return self.bs_id

    def get_assest_class(self):
        return self.assest_class

    def get_business_id(self):
        return self.business_id