import json

class ppr_expense_response:
    transactiondate = None,
    valuedate = None,
    apinvoice_id = None,
    apinvoicebranch_id = None,
    apinvoicesupplier_id = None,
    apinvoicedetails_id = None,
    apsubcat_id = None,
    apexpense_id = None,
    bs_id = None,
    cc_id = None,
    biz_id = None,
    product_id = None,
    client_id = None,
    expensegroup_id = None
    sector_id = None,
    amount = None,
    taxamount = None,
    otheramount = None,
    totalamount = None,
    category_id = None,
    expensegroup_name = None
    asset_name = None
    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id
    def set_name(self, name):
        self.name = name
    def set_expensegroup_id(self, expensegroup_id):
        self.expensegroup_id = expensegroup_id
    def set_expensegroup_name(self,expensegroup_name):
        self.expensegroup_name = expensegroup_name
    def set_amount(self,amount):
        self.amount = amount
    def set_apexpense_id(self,apexpense_id):
        self.apexpense_id = apexpense_id
    def set_apexpense_name(self,apexpense_name):
        self.apexpense_name = apexpense_name
    def set_asset_name(self, asset_name):
        self.asset_name = asset_name
    def set_category_id(self, category_id):
        self.category_id = category_id