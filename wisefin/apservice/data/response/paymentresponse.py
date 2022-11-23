import json
class PaymentHeaderResponse:

    id = None
    pvno = None
    paymentheader_date = None
    paymentheader_amount = None
    ref_id = None
    reftable_id = None
    paymode = None
    bankdetails_id = None
    dispatch_id = None
    beneficiaryname = None
    chqno = None
    chqdate = None
    bankname = None
    ifsccode = None
    accno = None
    debitbankacc = None
    stalechq_id = None
    refno = None
    callbackrefno = None
    remarks = None

    def get(self):
        return json.dumps(self, default=lambda o:o.__dict__, sort_keys=True, indent=4)

    def set_id(self,id):
        self.id = id
    def set_pvno(self,pvno):
        self.pvno = pvno

    def set_paymentheader_date(self,paymentheader_date):
        self.paymentheader_date = paymentheader_date
    def set_paymentheader_amount(self,paymentheader_amount):
        self.paymentheader_amount = paymentheader_amount
    def set_ref_id(self,ref_id):
        self.ref_id = ref_id
    def set_reftable_id(self,reftable_id):
        self.reftable_id = reftable_id
    def set_paymode(self,paymode):
        self.paymode = paymode
    def set_bankdetails_id(self,bankdetails_id):
        self.bankdetails_id = bankdetails_id
    def set_dispatch_id(self,dispatch_id):
        self.dispatch_id = dispatch_id
    def set_beneficiaryname(self,beneficiaryname):
        self.beneficiaryname = beneficiaryname
    def set_chqno(self,chqno):
        self.chqno = chqno
    def set_chqdate(self,chqdate):
        self.chqdate = chqdate
    def set_bankname(self,bankname):
        self.bankname = bankname
    def set_ifsccode(self,ifsccode):
        self.ifsccode = ifsccode
    def set_accno(self,accno):
        self.accno = accno
    def set_debitbankacc(self,debitbankacc):
        self.debitbankacc = debitbankacc
    def set_stalechq_id(self,stalechq_id):
        self.stalechq_id = stalechq_id
    def set_refno(self,refno):
        self.refno = refno
    def set_callbackrefno(self,callbackrefno):
        self.callbackrefno = callbackrefno
    def set_remarks(self,remarks):
        self.remarks = remarks

class paymentdetailsresponse:
    id = None
    paymentheader_id = None
    apinvoiceheader_id = None
    apcredit_id = None
    paymentdetails_amount = None


    def get(self):
        return json.dumps(self, default=lambda o:o.__dict__, sort_keys=True, indent=4)

    def set_id(self,id):
        self.id = id
    def set_paymentheader_id(self,paymentheader_id):
        self.paymentheader_id = paymentheader_id
    def set_apinvoiceheader_id(self,apinvoiceheader_id):
        self.apinvoiceheader_id = apinvoiceheader_id
    def set_apcredit_id(self,apcredit_id):
        self.apcredit_id = apcredit_id
    def set_paymentdetails_amount(self,paymentdetails_amount):
        self.paymentdetails_amount = paymentdetails_amount
