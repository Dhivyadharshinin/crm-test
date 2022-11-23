import json
from entryservice.util.entryutil import EntryType,ModuleType
entrytype=EntryType()
moduletype=ModuleType()
class EntryResponse:
    id = None
    branch_id = None
    fiscalyear = None
    glnodescription = None
    total_row=None
    current_total_row=None

    def get(self):
      return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id
    def set_branch_id(self, branch_id):
        self.branch_id = branch_id
    def set_fiscalyear(self, fiscalyear):
        self.fiscalyear = fiscalyear
    def set_period(self, period):
        self.period = period
    def set_module(self, module):
        self.module = moduletype.get_val(module)
    def set_screen(self, screen):
        self.screen = screen
    def set_transactiondate(self, transactiondate):
        self.transactiondate = str(transactiondate)
    def set_transactiontime(self, transactiontime):
        self.transactiontime = str(transactiontime)
    def set_valuedate(self, valuedate):
        self.valuedate = str(valuedate)
    def set_valuetime(self, valuetime):
        self.valuetime = str(valuetime)
    def set_cbsdate(self, cbsdate):
        self.cbsdate = str(cbsdate)
    def set_localcurrency(self, localcurrency):
        self.localcurrency = localcurrency
    def set_localexchangerate(self, localexchangerate):
        self.localexchangerate = str(localexchangerate)
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
        self.type = entrytype.get_val(type)
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
        self.amount = str(amount)
    def set_fcamount(self, fcamount):
        self.fcamount = str(fcamount)
    def set_ackrefno(self, ackrefno):
        self.ackrefno = ackrefno
    def set_entry_status(self, entry_status):
        self.entry_status = entry_status
    def set_group_id(self, group_id):
        self.group_id = group_id
    def set_glnodescription(self, glnodescription):
        self.glnodescription = glnodescription
    def set_errordescription(self, errordescription):
        self.errordescription = errordescription
    def set_total_row(self, total_row):
        self.total_row = total_row
    def set_current_total_row(self, current_total_row):
        self.current_total_row = current_total_row
    def set_is_error(self, is_error):
        self.is_error = is_error
    def set_bulk_status(self, bulk_status):
        self.bulk_status = bulk_status
    def set_bulk_is_error(self, bulk_is_error):
        self.bulk_is_error = bulk_is_error
    def set_bulk_errordescription(self, bulk_errordescription):
        self.bulk_errordescription = bulk_errordescription
    def set_entry_new_data(self,entry):
        entry_staus=int(entry.entry_status)
        if(entry_staus==1):
            self.entry_new_status = "SUCCESS"
        else:
            entry_error_status=int(entry.is_error)
            if(entry_staus==0 and entry_error_status==1):
                self.entry_new_status="FAILED"
            else:
                self.entry_new_status="NOT_SEND"

    # branch_id, fiscalyear, period, module, screen, transactiondate, transactiontime,
    # valuedate, valuetime, cbsdate, localcurrency, localexchangerate, currency, exchangerate,
    # isprevyrentry, reversalentry, refno, crno, refid, reftableid, type,
    # gl, apcatno, apsubcatno, wisefinmap, glremarks, amount, fcamount, ackrefno, entry_status