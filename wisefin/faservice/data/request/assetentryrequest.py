import json

class AssetEntryRequest:
    id = None
    branch_id = None
    fiscalyear = None
    period = None
    module = None
    screen = None
    transactiondate = None
    transactiontime = None
    valuedate = None
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

    def __init__(self, assetdebit_data):
        if 'id' in assetdebit_data:
            self.id = assetdebit_data['id']
        if 'branch_id' in assetdebit_data:
            self.branch_id = assetdebit_data['branch_id']
        if 'fiscalyear' in assetdebit_data:
            self.fiscalyear = assetdebit_data['fiscalyear']
        if 'period' in assetdebit_data:
                self.period = assetdebit_data['period']
        if 'module' in assetdebit_data:
                self.module = assetdebit_data['module']
        if 'screen' in assetdebit_data:
                self.screen = assetdebit_data['screen']
        if 'transactiondate' in assetdebit_data:
                self.transactiondate = assetdebit_data['transactiondate']
        if 'transactiontime' in assetdebit_data:
                self.transactiontime = assetdebit_data['transactiontime']
        if 'valuedate' in assetdebit_data:
                self.valuedate = assetdebit_data['valuedate']
        if 'valuetime' in assetdebit_data:
                self.valuetime = assetdebit_data['valuetime']
        if 'cbsdate' in assetdebit_data:
                self.cbsdate = assetdebit_data['cbsdate']
        if 'localcurrency' in assetdebit_data:
                self.localcurrency = assetdebit_data['localcurrency']
        if 'localexchangerate' in assetdebit_data:
                self.localexchangerate = assetdebit_data['localexchangerate']
        if 'currency' in assetdebit_data:
                self.currency = assetdebit_data['currency']
        if 'exchangerate' in assetdebit_data:
                self.exchangerate = assetdebit_data['exchangerate']
        if 'isprevyrentry' in assetdebit_data:
                self.isprevyrentry = assetdebit_data['isprevyrentry']
        if 'reversalentry' in assetdebit_data:
                self.reversalentry = assetdebit_data['reversalentry']
        if 'refno' in assetdebit_data:
                self.refno = assetdebit_data['refno']
        if 'crno' in assetdebit_data:
                self.crno = assetdebit_data['crno']
        if 'refid' in assetdebit_data:
                self.refid = assetdebit_data['refid']
        if 'reftableid' in assetdebit_data:
                self.reftableid = assetdebit_data['reftableid']
        if 'type' in assetdebit_data:
                self.type = assetdebit_data['type']
        if 'gl' in assetdebit_data:
                self.gl = assetdebit_data['gl']
        if 'apcatno' in assetdebit_data:
                self.apcatno = assetdebit_data['apcatno']
        if 'apsubcatno' in assetdebit_data:
                self.apsubcatno = assetdebit_data['apsubcatno']
        if 'wisefinmap' in assetdebit_data:
                self.wisefinmap = assetdebit_data['wisefinmap']
        if 'glremarks' in assetdebit_data:
                self.glremarks = assetdebit_data['glremarks']
        if 'amount' in assetdebit_data:
                self.amount = assetdebit_data['amount']
        if 'fcamount' in assetdebit_data:
                self.fcamount = assetdebit_data['fcamount']
        if 'ackrefno' in assetdebit_data:
                self.ackrefno = assetdebit_data['ackrefno']

    def get_id(self):
        return self.id
    def get_branch_id(self):
        return self.branch_id
    def get_fiscalyear(self):
        return self.fiscalyear
    def get_period(self):
        return self.period
    def get_module(self):
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


class CreditDebitRequest:
    InvoiceHeader_Gid = crno = branchgid = refgid = gl = ApCatNo = ApSubCatNo = entry_amt = TransactionDate = ValueDate = TransactionTime = Period = Module = Screen = Entry_Remarks = type = None
def __init__(self, credit_data):
    if ("InvoiceHeader_Gid" in credit_data):
        self.InvoiceHeader_Gid = credit_data["InvoiceHeader_Gid"]
    if ("crno" in credit_data):
        self.crno = credit_data["crno"]
    if ("branchgid" in credit_data):
        self.branchgid = credit_data["branchgid"]
    if ("refgid" in credit_data):
        self.refgid = credit_data["refgid"]
    if ("gl" in credit_data):
        self.gl = credit_data["gl"]
    if ("ApCatNo" in credit_data):
        self.ApCatNo = credit_data["ApCatNo"]
    if ("ApSubCatNo" in credit_data):
        self.ApSubCatNo = credit_data["ApSubCatNo"]
    if ("entry_amt" in credit_data):
        self.entry_amt = credit_data["entry_amt"]
    if ("TransactionDate" in credit_data):
        self.TransactionDate = credit_data["TransactionDate"]
    if ("ValueDate" in credit_data):
        self.ValueDate = credit_data["ValueDate"]
    if ("TransactionTime" in credit_data):
        self.TransactionTime = credit_data["TransactionTime"]
    if ("Period" in credit_data):
        self.Period = credit_data["Period"]
    if ("Module" in credit_data):
        self.Module = credit_data["Module"]
    if ("Screen" in credit_data):
        self.Screen = credit_data["Screen"]
    if ("Entry_Remarks" in credit_data):
        self.Entry_Remarks = credit_data["Entry_Remarks"]
    if ("type" in credit_data):
        self.type = credit_data["type"]