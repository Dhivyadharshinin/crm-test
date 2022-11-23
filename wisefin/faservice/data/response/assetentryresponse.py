import json

from faservice.util.fautil import dictdefault

class AssetEntryResponse:
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

    def get(self):
        return json.dumps(self.__dict__, default=dictdefault,sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id
    def set_branch_id(self, branch_id):
        self.branch_id = branch_id
    def set_fiscalyear(self, fiscalyear):
        self.fiscalyear = fiscalyear
    def set_module(self, module):
        self.module = module
    def set_screen(self, screen):
        self.screen = screen
    def set_period(self, period):
        self.period = period
    def set_transactiondate(self, transactiondate):
        self.transactiondate = str(transactiondate)
    def set_transactiontime(self, transactiontime):
        self.transactiontime = transactiontime
    def set_valuedate(self, valuedate):
        self.valuedate = str(valuedate)
    def set_valuetime(self, valuetime):
        self.valuetime = valuetime
    def set_cbsdate(self, cbsdate):
        self.cbsdate = str(cbsdate)
    def set_localcurrency(self, localcurrency):
        self.localcurrency = localcurrency
    def set_localexchangerate(self, localexchangerate):
        self.localexchangerate = localexchangerate
    def set_currency(self, currency):
        self.currency = currency
    def set_exchangerate(self, exchangerate):
        self.exchangerate = exchangerate
    def set_isprevyrentry(self, isprevyrentry):
        self.isprevyrentry = isprevyrentry
    def set_reversalentry(self, reversalentry):
        self.reversalentry = reversalentry
    def set_refno(self, refno):
        self.refno = refno
    def set_crno(self, crno):
        self.crno = crno
    def set_refid(self, refid):
        self.refid = refid
    def set_reftableid(self, reftableid):
        self.reftableid = reftableid
    def set_type(self, type):
        self.type = type
    def set_gl(self, gl):
        self.gl = gl
    def set_apcatno(self, apcatno):
        self.apcatno = apcatno
    def set_apsubcatno(self, apsubcatno):
        self.apsubcatno = apsubcatno
    def set_wisefinmap(self, wisefinmap):
        self.wisefinmap = wisefinmap
    def set_glremarks(self, glremarks):
        self.glremarks = glremarks
    def set_amount(self, amount):
        self.amount = amount
    def set_fcamount(self, fcamount):
        self.fcamount = fcamount
    def set_ackrefno(self, ackrefno):
        self.ackrefno = ackrefno
class CreditDebitResponse:
    InvoiceHeader_Gid = crno = branchgid = refgid = gl = ApCatNo = ApSubCatNo = entry_amt = TransactionDate = ValueDate =\
        TransactionTime = Period = Module = Screen = Entry_Remarks = type = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,sort_keys=True, indent=4)

    def set_InvoiceHeader_Gid(self, InvoiceHeader_Gid):
        self.InvoiceHeader_Gid = InvoiceHeader_Gid

    def set_crno(self, crno):
        self.crno = crno

    def set_branchgid(self, branchgid):
        self.branchgid = branchgid

    def set_refgid(self, refgid):
        self.refgid = refgid

    def set_gl(self, gl):
        self.gl = gl

    def set_ApCatNo(self, ApCatNo):
        self.ApCatNo = ApCatNo

    def set_ApSubCatNo(self, ApSubCatNo):
        self.ApSubCatNo = ApSubCatNo
    def set_entry_amt(self, entry_amt):
        self.entry_amt = entry_amt
    def set_TransactionDate(self, TransactionDate):
        self.TransactionDate = str(TransactionDate)
    def set_ValueDate(self, ValueDate):
        self.ValueDate = str(ValueDate)
    def set_TransactionTime(self, TransactionTime):
        self.TransactionTime = TransactionTime
    def set_Period(self, Period):
        self.Period = Period
    def set_Module(self, Module):
        self.Module = Module
    def set_Screen(self, Screen):
        self.Screen = Screen
    def set_Entry_Remarks(self, Entry_Remarks):
        self.Entry_Remarks = Entry_Remarks
    def set_type(self, type):
        self.type = type
