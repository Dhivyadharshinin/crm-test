import json

class APCreditResponse:
    id = None
    apinvoiceheader = None
    paymode_id = None
    creditbank_id = None
    suppliertax_id = None
    creditglno = None
    creditrefno = None
    suppliertaxtype = None
    suppliertaxrate = None
    taxexcempted = None
    amount = None
    taxableamount = None
    ddtranbranch = None
    ddpaybranch = None
    category_code = None
    subcategory_code = None
    paydetails = None
    tdsrate=None
    credit=None
    tds_subtraction_rate=None
    creditamount=None
    tds_percentage=None
    is_display=None
    vendor_type=None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_id(self,id):
        self.id = id
    def set_apinvoiceheader(self,apinvoiceheader_id):
        self.apinvoiceheader = apinvoiceheader_id
    def set_paymode(self,paymode):
        self.paymode = paymode
    def set_paymode_id(self, paymode_id, arr):
        if paymode_id != None:
            for i in arr:
                if i['id'] == paymode_id:
                    self.paymode_id = i
                    break
    def set_creditbank(self,creditbank_id):
        self.creditbank_id = creditbank_id

    def set_creditbank_id(self, creditbank_id, arr):
        if creditbank_id != None:
            for i in arr:
                if i['id'] == creditbank_id:
                    self.creditbank_id = i
                    break
    def set_suppliertax(self,suppliertax_id):
        self.suppliertax_id = suppliertax_id
    def set_suppliertax_id(self, suppliertax_id, arr):
        if suppliertax_id != None:
            for i in arr:
                if i['id'] == suppliertax_id:
                    self.suppliertax_id = i
                    break
    def set_creditglno(self,creditglno):
        self.creditglno = creditglno
    def set_creditrefno(self,creditrefno):
        self.creditrefno = creditrefno
    def set_suppliertaxrate(self,suppliertaxrate):
        self.suppliertaxrate = suppliertaxrate
    def set_suppliertaxtype(self,suppliertaxtype):
        self.suppliertaxtype = suppliertaxtype
    def set_taxexcempted(self,taxexcempted):
        self.taxexcempted = taxexcempted
    def set_amount(self,amount):
        self.amount = amount
    def set_taxableamount(self,taxableamount):
        self.taxableamount = taxableamount
    def set_ddtranbranch(self,ddtranbranch):
        self.ddtranbranch = ddtranbranch
    def set_ddpaybranch(self,ddpaybranch):
        self.ddpaybranch = ddpaybranch
    def set_category_code(self,category_code):
        self.category_code = category_code
    def set_subcategory_code(self,subcategory_code):
        self.subcategory_code = subcategory_code
    def set_paydetails(self,paydetails):
        self.paydetails = paydetails
    def set_tdsrate(self,tdsrate):
        self.tdsrate = tdsrate
    def set_credit(self,credit):
        self.credit = credit

    def set_tds_subtraction_rate(self,tds_subtraction_rate):
        self.tds_subtraction_rate = tds_subtraction_rate
    def set_creditamount(self,creditamount):
        self.creditamount = creditamount


    def set_tds_percentage(self,tds_percentage):
        self.tds_percentage = tds_percentage

    def set_is_display(self,is_display):
        self.is_display = is_display


    def set_supplierpayment_details(self,supplierpayment_details):
        self.supplierpayment_details = supplierpayment_details


    def set_vendor_type(self,vendor_type):
        self.vendor_type = vendor_type


