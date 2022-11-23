import json
from entryservice.util.entryutil import EntryType,ModuleType
from datetime import datetime



entrytype=EntryType()
moduletype=ModuleType()
SourceName="Vsolv"
UserCategoryName="Miscellaneous"

class OracleEntryResponse:
    id = None
    branch_id = None
    fiscalyear = None

    def get(self):
      return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id
    def set_Message(self, Message):
        self.Message = Message
    def set_desc(self,desc):
        self.desc=desc
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
    def set_entry_oracle_data(self,oracle_data,AP_Type,ap_data):
        now_today_date = datetime.now()
        crno=oracle_data.crno
        cbsdate=oracle_data.cbsdate
        today_date = now_today_date.strftime("%Y-%m-%d")
        # today_Hour = now_today_date.strftime("%H")
        # today_Minutes = now_today_date.strftime("%M")
        # today_Seconds = now_today_date.strftime("%S")
        # today_Micro_Seconds = now_today_date.strftime("%f")
        # cbs_date_with_format = cbsdate.strftime("%Y-%m-%d")
        now_date_Month_Char=now_today_date.strftime("%b")
        now_date_Date=now_today_date.strftime("%d")
        now_date_Year=now_today_date.strftime("%Y")
        # date_time_concate=cbs_date_Month_Char+cbs_date_Date+cbs_date_Year
        PeriodName=now_date_Month_Char+"-"+now_date_Year[2:4]
        self.BatchName=oracle_data.crno#VsolvBatchMar23202201
        self.BatchDescription=oracle_data.crno #VsolvBatchMar23202201
        self.LedgerId="300000001389007"#oracle_data.gl
        self.AccountingPeriodName=PeriodName#"Mar-22"
        self.AccountingDate=today_date#"2022-03-23"#today_date
        self.UserSourceName=SourceName
        self.UserCategoryName=UserCategoryName
        self.ErrorToSuspenseFlag="True"
        self.SummaryFlag="True"
        self.ImportDescriptiveFlexField="N"

        self.Reference1 =crno
        self.Reference4=crno#VsolvJournalJan032202
        self.Reference5=crno#VsolvJournalJan032202

        #self.LedgerId=""#300000001389007

        self.PeriodName=PeriodName#"Mar-22"
        #AccountingDate=""#2022-03-23

        self.UserJeSourceName=SourceName
        self.UserJeCategoryName=SourceName
        #cr_9=crno[-9:]
        self.GroupId=oracle_data.group_id#2303202201#2303210413
        self.ChartOfAccountsId=""
        self.BalanceType="A"
        self.CodeCombinationId=""
        self.Segment1=oracle_data.segment_1
        self.Segment2=oracle_data.segment_2#"232601"
        self.Segment3 = oracle_data.segment_3
        self.Segment4 = oracle_data.segment_4
        self.Segment5 = oracle_data.segment_5
        self.Segment6 = oracle_data.segment_6
        self.Segment7 = oracle_data.segment_7
        self.Segment8 = oracle_data.segment_8
        self.Segment9 = oracle_data.segment_9
        self.Segment10 = oracle_data.segment_10

        self.Reference10 = oracle_data.reference_10

        self.CurrencyCode="INR"
        cr_de_type = entrytype.get_val(oracle_data.type)
        if(cr_de_type=="DEBIT"):
            self.EnteredDrAmount=float(oracle_data.amount)
        else:
            self.EnteredCrAmount=float(oracle_data.amount)

        self.AccountedCr=""
        self.AccountedDr=""
        self.StatisticalValue=""
        self.UserCurrencyConversionType=""
        self.CurrencyConversionDate=""
        self.CurrencyConversionRate=""
        self.CurrencyConversionType=""

        self.Reference30=""
        self.ReferenceDate=""
        self.Attribute1=""
        self.Attribute20=""

        self.AttributeCategory=""
        self.AttributeCategory2=""
        self.AttributeCategory3=""
        self.AverageJournalFlag=""
        self.BalancingSegmentValue=""
        self.DescrFlexErrorMessage=""
        self.GlSlLinkId=""
        self.GlSlLinkTable=""
        self.InvoiceDate=""
        self.InvoiceIdentifier=""
        self.JeCategoryName=""
        self.JeSourceName=""
        self.JgzzReconReference=""
        self.ManagementSegmentValue=""
        self.ObjectVersionNumber="1"
        self.OriginatingBalSegValue=""
        self.SetOfBooksId=""
        self.Status = "NEW"
        self.TaxCode = ""
        self.TransactionDate = ""
        self.USSGLTransactionCode = ""
        self.GlInterfaceId = ""
        self.LegalEntityIdentifier = ""
        self.LedgerName = ""
        self.AttributeDate1 = ""
        self.AttributeDate10 = ""
        self.AttributeNumber1 = ""
        self.AttributeNumber10 = ""


        #self.GlInterfaceId = ""
        self.FLEX_PARAM_GLOBAL_COUNTRY_CODE = ""
        self.__FLEX_Context = ""
        self.__FLEX_Context_DisplayValue = ""
        self._FLEX_NumOfSegments = ""


    # branch_id, fiscalyear, period, module, screen, transactiondate, transactiontime,
    # valuedate, valuetime, cbsdate, localcurrency, localexchangerate, currency, exchangerate,
    # isprevyrentry, reversalentry, refno, crno, refid, reftableid, type,
    # gl, apcatno, apsubcatno, wisefinmap, glremarks, amount, fcamount, ackrefno, entry_status