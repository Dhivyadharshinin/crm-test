import json

class Creditresponse:
    id = None
    invoiceheader = None
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
    credit_bank = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_id(self,id):
        self.id = id
    def set_invoiceheader(self,invoiceheader_id):
        self.invoiceheader = invoiceheader_id
    def set_paymode(self,paymode_id):
        self.paymode_id = paymode_id
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
    def set_credit_bank(self,credit_bank):
        self.credit_bank = credit_bank