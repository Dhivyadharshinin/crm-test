import json

class PaymentHeaderRequest:

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
    pay_to = None
    beneficiary_code = None





    def __init__(self,obj_apinv):
        if 'id' in obj_apinv:
            self.id=obj_apinv['id']
        if 'pvno' in obj_apinv:
            self.pvno = obj_apinv['pvno']
        if 'paymentheader_date' in obj_apinv:
            self.paymentheader_date = obj_apinv['paymentheader_date']
        if 'paymentheader_amount' in obj_apinv:
            self.paymentheader_amount = obj_apinv['paymentheader_amount']
        if 'ref_id' in obj_apinv:
            self.ref_id = obj_apinv['ref_id']
        if 'reftable_id' in obj_apinv:
            self.reftable_id = obj_apinv['reftable_id']
        if 'paymode' in obj_apinv:
            self.paymode = obj_apinv['paymode']
        if 'bankdetails_id' in obj_apinv:
            self.bankdetails_id = obj_apinv['bankdetails_id']
        if 'dispatch_id' in obj_apinv:
            self.dispatch_id = obj_apinv['dispatch_id']
        if 'beneficiaryname' in obj_apinv:
            self.beneficiaryname = obj_apinv['beneficiaryname']
        if 'chqno' in obj_apinv:
            self.chqno = obj_apinv['chqno']
        if 'chqdate' in obj_apinv:
            self.chqdate = obj_apinv['chqdate']
        if 'bankname' in obj_apinv:
            self.bankname = obj_apinv['bankname']
        if 'bankname' in obj_apinv:
            self.bankname = obj_apinv['bankname']
        if 'ifsc_code' in obj_apinv:
            self.ifsccode = obj_apinv['ifsc_code']
        if 'accno' in obj_apinv:
            self.accno = obj_apinv['accno']
        if 'debitbankacc' in obj_apinv:
            self.debitbankacc = obj_apinv['debitbankacc']
        if 'stalechq_id' in obj_apinv:
            self.stalechq_id = obj_apinv['stalechq_id']
        if 'refno' in obj_apinv:
            self.refno = obj_apinv['refno']
        if 'callbackrefno' in obj_apinv:
            self.callbackrefno = obj_apinv['callbackrefno']
        if 'remarks' in obj_apinv:
            self.remarks = obj_apinv['remarks']


        if 'pay_to' in obj_apinv:
            self.pay_to = obj_apinv['pay_to']
        if 'beneficiary_code' in obj_apinv:
            self.beneficiary_code = obj_apinv['beneficiary_code']




    def get_id(self):
        return self.id
    def get_pvno(self):
        return self.pvno
    def get_paymentheader_date(self):
        return self.paymentheader_date
    def get_paymentheader_amount(self):
        return self.paymentheader_amount
    def get_ref_id(self):
        return self.ref_id
    def get_reftable_id(self):
        return self.reftable_id
    def get_paymode(self):
        return self.paymode
    def get_bankdetails_id(self):
        return self.bankdetails_id
    def get_dispatch_id(self):
        return self.dispatch_id
    def get_beneficiaryname(self):
        return self.beneficiaryname
    def get_chqno(self):
        return self.chqno
    def get_chqdate(self):
        return self.chqdate
    def get_bankname(self):
        return self.bankname
    def get_ifsccode(self):
        return self.ifsccode
    def get_accno(self):
        return self.accno
    def get_debitbankacc(self):
        return self.debitbankacc
    def get_stalechq_id(self):
        return self.stalechq_id
    def get_refno(self):
        return self.refno
    def get_callbackrefno(self):
        return self.callbackrefno
    def get_remarks(self):
        return self.remarks


    def get_pay_to(self):
        return self.pay_to
    def get_beneficiary_code(self):
        return self.beneficiary_code



