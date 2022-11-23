import json

class ReportRequest:

    id = None
    branch_id = None
    fiscalyear = None
    period = None
    module = None
    screen = None
    regioncode = None
    transactiondate = None
    transactiontime = None
    valuetime = None
    cbsdate = None
    localcurrency = None
    localexchangerate = None
    currency = None
    exchangerate = None
    isprevyrentry = None
    reversalentry = None
    refno = None
    crno = None
    refid = None
    reftableid = None
    type = None
    gl = None
    apcatno = None
    apsubcatno = None
    wisefinmap = None
    glremarks = None
    amount = None
    fcamount = None
    ackrefno = None
    entry_status = None


    def __init__(self, entry_obj):
        if 'id' in entry_obj:
            self.id = entry_obj['id']
        if 'branch_id' in entry_obj:
            self.branch_id = entry_obj['branch_id']
        if 'fiscalyear' in entry_obj:
            self.fiscalyear = entry_obj['fiscalyear']
        if 'period' in entry_obj:
            self.period = entry_obj['period']
        if 'module' in entry_obj:
            self.module = entry_obj['module']
        if 'screen' in entry_obj:
            self.screen = entry_obj['screen']
        if 'transactiondate' in entry_obj:
            self.transactiondate = entry_obj['transactiondate']
        if 'transactiontime' in entry_obj:
            self.transactiontime = entry_obj['transactiontime']
        if 'valuedate' in entry_obj:
            self.valuedate = entry_obj['valuedate']
        if 'valuetime' in entry_obj:
            self.valuetime = entry_obj['valuetime']
        if 'cbsdate' in entry_obj:
            self.cbsdate = entry_obj['cbsdate']
        if 'localcurrency' in entry_obj:
            self.localcurrency = entry_obj['localcurrency']
        if 'localexchangerate' in entry_obj:
            self.localexchangerate = entry_obj['localexchangerate']
        if 'currency' in entry_obj:
            self.currency = entry_obj['currency']
        if 'exchangerate' in entry_obj:
            self.exchangerate = entry_obj['exchangerate']
        if 'isprevyrentry' in entry_obj:
            self.isprevyrentry = entry_obj['isprevyrentry']
        if 'reversalentry' in entry_obj:
            self.reversalentry = entry_obj['reversalentry']
        if 'refno' in entry_obj:
            self.refno = entry_obj['refno']
        if 'crno' in entry_obj:
            self.crno = entry_obj['crno']
        if 'refid' in entry_obj:
            self.refid = entry_obj['refid']
        if 'reftableid' in entry_obj:
            self.reftableid = entry_obj['reftableid']
        if 'type' in entry_obj:
            self.type = entry_obj['type']
        if 'gl' in entry_obj:
            self.gl = entry_obj['gl']
        if 'apcatno' in entry_obj:
            self.apcatno = entry_obj['apcatno']
        if 'apsubcatno' in entry_obj:
            self.apsubcatno = entry_obj['apsubcatno']
        if 'wisefinmap' in entry_obj:
            self.wisefinmap = entry_obj['wisefinmap']
        if 'glremarks' in entry_obj:
            self.glremarks = entry_obj['glremarks']
        if 'amount' in entry_obj:
            self.amount = entry_obj['amount']
        if 'fcamount' in entry_obj:
            self.fcamount = entry_obj['fcamount']
        if 'ackrefno' in entry_obj:
            self.ackrefno = entry_obj['ackrefno']
        if 'entry_status' in entry_obj:
            self.entry_status = entry_obj['entry_status']

    def get_id(self):
        return self.id
    def get_branch_id(self):
        return self.branch_id
    def get_fiscalyear(self):
        return self.fiscalyear
    def get_period(self):
        return self.period
    def get_moduled(self):
        return self.module
    def get_screen(self):
        return self.screen
    def get_transactiondate(self):
        return self.transactiondate
    def get_transactiontime(self):
        return self.transactiontime
    def get_valuedate(self):
        return self.valuedate
    def get_valuetime(self):
        return self.valuetime
    def get_cbsdate(self):
        return self.cbsdate
    def get_localcurrency(self):
        return self.localcurrency
    def get_module(self):
        return self.module
    def get_refgid(self):
        return self.refid
    def get_localexchangerate(self):
        return self.localexchangerate
    def get_currency(self):
        return self.currency
    def get_exchangerate(self):
        return self.exchangerate
    def get_isprevyrentry(self):
        return self.isprevyrentry
    def get_reversalentry(self):
        return self.reversalentry
    def get_refno(self):
        return self.refno
    def get_crno(self):
        return self.crno
    def get_refid(self):
        return self.refid
    def get_reftableid(self):
        return self.reftableid
    def get_type(self):
        return self.type
    def get_gl(self):
        return self.gl
    def get_apcatno(self):
        return self.apcatno
    def get_apsubcatno(self):
        return self.apsubcatno
    def get_wisefinmap(self):
        return self.wisefinmap
    def get_glremarks(self):
        return self.glremarks
    def get_amount(self):
        return self.amount
    def get_fcamount(self):
        return self.fcamount
    def get_ackrefno(self):
        return self.ackrefno
    def get_entry_status(self):
        return self.entry_status

