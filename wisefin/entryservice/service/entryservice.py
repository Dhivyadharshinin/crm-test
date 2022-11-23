import traceback

from entryservice.models.entrymodels import Entry, Oraclesegment
from entryservice.data.response.entryresponse  import EntryResponse
from django.db.models import Q
from django.utils.timezone import now
from datetime import datetime,timedelta
from django.db import IntegrityError
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinsuccess import SuccessStatus, SuccessMessage, NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
#from vysfinutility.service.utilityservice import VysfinUtilityService
#utilityservice=VysfinUtilityService()
from entryservice.data.request.entryrequest import EntryRequest
from entryservice.util.entryutil import EntryType,ModuleType
# from faservice.models.famodels import AssetHeader
from entryservice.data.response.entryoracleresponse  import OracleEntryResponse
from entryservice.util.entryutil import EntryType, APDBService, MASTERDBService, ENTRYDBService
from nwisefin.settings import DATABASES
import re
from django.db import IntegrityError, connection
import json
import pandas as pd


entrytype=EntryType()
moduletype=ModuleType()
class EntryService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.ENTRY_SERVICE)
    def create_entrydetails(self,request,emp_id,entry_obj):

        # if not entry_obj[0]['id'] is None:
        #     try:
        #         Entry_Detail = Entry.objects.using(self._current_app_schema()).filter(id=entry_obj.get_id()).update(branch_id=entry_obj.get_branch_id(),
        #                                                                           fiscalyear=now().year,
        #                                              period=entry_obj.get_period(),
        #                                              module=entry_obj.get_module(),
        #                                              screen=entry_obj.get_screen(),
        #                                              transactiondate=now().date(),
        #                                              transactiontime=now().time(),
        #                                              valuedate=now().date(),
        #                                              valuetime=now().time(),
        #                                              cbsdate=now(),
        #                                              localcurrency = entry_obj.get_localcurrency(),
        #                                              localexchangerate = entry_obj.get_localexchangerate(),
        #                                              currency = entry_obj.get_currency(),
        #                                              exchangerate = entry_obj.get_exchangerate(),
        #                                              isprevyrentry = entry_obj.get_isprevyrentry(),
        #                                              reversalentry = entry_obj.get_reversalentry(),
        #                                              refno=entry_obj.get_refno(),
        #                                              crno =entry_obj.get_crno(),
        #                                              refid=entry_obj.get_refid(),
        #                                              reftableid = entry_obj.get_reftableid(),
        #                                              type=entry_obj.get_type(),
        #                                              gl=entry_obj.get_gl(),
        #                                              apcatno=entry_obj.get_apcatno(),
        #                                              apsubcatno=entry_obj.get_apsubcatno(),
        #                                              wisefinmap = entry_obj.get_wisefinmap(),
        #                                              glremarks=entry_obj.get_glremarks(),
        #                                              amount=entry_obj.get_amount(),
        #                                              fcamount = entry_obj.get_fcamount(),
        #                                              ackrefno = entry_obj.get_ackrefno(),
        #                                              group_id =group_id,
        #                                              updated_by=emp_id,
        #                                              updated_date=now())
        #         EntryDetail = Entry.objects.get(id=entry_obj.get_id())
        #         success_obj = NWisefinSuccess()
        #         success_obj.set_status(SuccessStatus.SUCCESS)
        #         success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        #
        #     except Exception as excep:
        #         error_obj = NWisefinError()
        #         error_obj.set_code(ErrorMessage.INVALID_DATA)
        #         error_obj.set_description(str(excep))
        #         return error_obj
        #     return success_obj

        #else:
            try:
                from django.db import transaction
                with transaction.atomic(using=self._current_app_schema()):
                    if(len(entry_obj)==0):
                        success_obj = NWisefinSuccess()
                        success_obj.set_status("Failed")
                        success_obj.set_message("Given entry list is empty")
                        return success_obj
                    entry_data_frame = pd.DataFrame(entry_obj)
                    entry_data_frame['amount'] = entry_data_frame['amount'].astype(float)
                    Credit_amount = entry_data_frame.loc[entry_data_frame['type'] == '1', 'amount'].sum()
                    Debit_amount = entry_data_frame.loc[entry_data_frame['type'] == '2', 'amount'].sum()
                    Credit_amount = str(round(float(Credit_amount), 2))
                    Debit_amount = str(round(float(Debit_amount), 2))
                    if (Credit_amount != Debit_amount):
                        success_obj = NWisefinSuccess()
                        success_obj.set_status(" Entry Failed")
                        success_obj.set_message("Debit Amount and Credit Amount Not Equal.")
                        return success_obj
                    for data in entry_obj:
                        i = EntryRequest(data)
                        oracleseg = Oraclesegment.objects.using(self._current_app_schema()). \
                            values('segmentno', 'values').\
                            filter(vendortype=i.get_vendor_type(),status=1)
                        for j in oracleseg:
                            if j['segmentno']=='segment1':
                                segvalues1=j['values']
                            # if j['segmentno']=='segment2':
                            #     segvalues2=j['values']
                            if j['segmentno']=='segment4':
                                segvalues4=j['values']
                            if j['segmentno']=='segment5':
                                segvalues5=j['values']
                            if j['segmentno']=='segment6':
                                segvalues6=j['values']
                            if j['segmentno']=='segment7':
                                segvalues7=j['values']
                            if j['segmentno']=='segment8':
                                segvalues8=j['values']
                            if j['segmentno']=='segment9':
                                segvalues9=j['values']
                            if j['segmentno']=='segment10':
                                segvalues10=j['values']
                        temp_cr_data = re.compile("([a-zA-Z]+)([0-9]+)")
                        split_data = temp_cr_data.match(i.crno).groups()
                        splitcrno = split_data[0]
                        split_number = split_data[1]
                        if splitcrno == 'TCF':
                            group_id = '1' + split_number
                        elif splitcrno == 'NPO':
                            group_id = '2' + split_number
                        elif splitcrno == 'ERA':
                            group_id = '3' + split_number
                        elif splitcrno == 'ADE':
                            group_id = '4' + split_number
                        elif splitcrno == 'ADV':
                            group_id = '5' + split_number
                        elif splitcrno == 'JV':
                            group_id = '6' + split_number
                        elif splitcrno == 'NACE':
                            group_id = '7' + split_number
                        else:
                            error_obj = NWisefinError()
                            error_obj.set_code(ErrorMessage.INVALID_DATA)
                            error_obj.set_description("Please add this invoice type to entry module")
                            return error_obj
                        from utilityservice.service.entry_api_service import ApiService
                        api_serv = ApiService(self._scope())
                        description = api_serv.glno_description(request,i.get_gl())
                        if description is not None:
                            description = description
                        else:
                            description =0
                        if i.get_refgid() !=3:
                            apheaderdata=api_serv.ap_header_id_to_header_data(i.get_reftableid())
                            invoice_no=apheaderdata['invoice_no']
                            invoice_date=apheaderdata['invoice_date']
                            Payto=apheaderdata['Payto']
                            #department_code=apheaderdata['department_code']
                            reference10=invoice_no+'-'+invoice_date+'-'+Payto
                        elif i.get_refgid() ==3:
                            reference10=0
                            #segvalues4=9999
                        Entry_Detail = Entry.objects.using(self._current_app_schema()).create(branch_id=i.get_branch_id(),fiscalyear=now().year,
                                                             period=i.get_period(),
                                                             module=i.get_module(),
                                                             screen=i.get_screen(),
                                                             transactiondate=now().date(),
                                                             transactiontime=now().time(),
                                                             valuedate=now().date(),
                                                             valuetime=now().time(),
                                                             cbsdate=now(),
                                                             localcurrency = i.get_localcurrency(),
                                                             localexchangerate = i.get_localexchangerate(),
                                                             currency = i.get_currency(),
                                                             exchangerate = i.get_exchangerate(),
                                                             isprevyrentry = i.get_isprevyrentry(),
                                                             reversalentry = i.get_reversalentry(),
                                                             refno=i.get_refno(),
                                                             crno =i.get_crno() ,
                                                             refid=i.get_refgid(),
                                                             reftableid = i.get_reftableid(),
                                                             type=i.get_type(),
                                                             gl=i.get_gl(),
                                                             glnodescription=description,
                                                             apcatno=i.get_apcatno(),
                                                             apsubcatno=i.get_apsubcatno(),
                                                             wisefinmap = i.get_wisefinmap(),
                                                             glremarks=i.get_glremarks(),
                                                             amount=i.get_amount(),
                                                             fcamount = i.get_fcamount(),
                                                             ackrefno = i.get_ackrefno(),
                                                             entity_id=self._entity_id(),
                                                             group_id=group_id,
                                                             segment_1=segvalues1,
                                                             segment_2=i.get_gl(),
                                                             segment_3=i.get_branch_code(),
                                                             segment_4=segvalues4,
                                                             segment_5=segvalues5,
                                                             segment_6=segvalues6,
                                                             segment_7=segvalues7,
                                                             segment_8=segvalues8,
                                                             segment_9=segvalues9,
                                                             segment_10=segvalues10,
                                                             reference_10=reference10,
                                                             created_by=emp_id,
                                                             created_date=now())

                        success_obj = NWisefinSuccess()
                        success_obj.set_status(SuccessStatus.SUCCESS)
                        success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
                    return success_obj
            except Exception as excep:
                traceback.print_exc()
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(str(excep))
                return error_obj


    def fetch_all_entry_list(self,query,vys_page,emp_id,request):
        if(query=="Failed_Entry"):
            conditions = Q(entry_status=0)& Q(is_error=1)
            entrydetails = Entry.objects.using(self._current_app_schema()).filter(conditions)[vys_page.get_offset():vys_page.get_query_limit()]
        else:
            entrydetails = Entry.objects.using(self._current_app_schema()).all()[vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(entrydetails)
        entry_list_data = NWisefinList()
        if list_length <= 0:
            pass
        else:
            for entry_val in entrydetails:
                entry_data = EntryResponse()
                entry_data.set_id(entry_val.id)
                entry_data.set_branch_id(entry_val.entry_status)
                entry_data.set_fiscalyear(entry_val.fiscalyear)
                entry_data.set_period(entry_val.period)
                entry_data.set_module(entry_val.module)
                entry_data.set_screen(entry_val.screen)
                entry_data.set_transactiondate(entry_val.transactiondate)
                entry_data.set_transactiontime(entry_val.transactiontime)
                entry_data.set_valuedate(entry_val.valuedate)
                entry_data.set_valuetime(entry_val.valuetime)
                entry_data.set_cbsdate(entry_val.cbsdate)
                entry_data.set_localcurrency(entry_val.localcurrency)
                entry_data.set_localexchangerate(entry_val.localexchangerate)
                entry_data.set_currency(entry_val.currency)
                entry_data.set_exchangerate(entry_val.exchangerate)
                entry_data.set_isprevyrentry(entry_val.isprevyrentry)
                entry_data.set_reversalentry(entry_val.reversalentry)
                entry_data.set_refno(entry_val.refno)
                entry_data.set_crno(entry_val.crno)
                entry_data.set_refid(entry_val.refid)
                entry_data.set_reftableid(entry_val.reftableid)
                entry_data.set_type(entry_val.type)
                entry_data.set_gl(entry_val.gl)
                entry_data.set_apcatno(entry_val.apcatno)
                entry_data.set_apsubcatno(entry_val.apsubcatno)
                entry_data.set_wisefinmap(entry_val.wisefinmap)
                entry_data.set_glremarks(entry_val.glremarks)
                entry_data.set_amount(entry_val.amount)
                entry_data.set_ackrefno(entry_val.ackrefno)
                entry_data.set_fcamount(entry_val.fcamount)
                entry_data.set_entry_status(entry_val.entry_status)
                entry_data.set_errordescription(entry_val.errordescription)
                entry_list_data.append(entry_data)
                vpage = NWisefinPaginator(entrydetails, vys_page.get_index(), 10)
                entry_list_data.set_pagination(vpage)
            return entry_list_data

    def fetch_entry(self,entry_id,user_id):
        try:
            entry_val = Entry.objects.get(id=entry_id)
            entry_data = EntryResponse()
            entry_data.set_id(entry_val.id)
            entry_data.set_branch_id(entry_val.entry_status)
            entry_data.set_fiscalyear(entry_val.fiscalyear)
            entry_data.set_period(entry_val.period)
            entry_data.set_module(entry_val.module)
            entry_data.set_screen(entry_val.screen)
            entry_data.set_transactiondate(entry_val.transactiondate)
            entry_data.set_transactiontime(entry_val.transactiontime)
            entry_data.set_valuedate(entry_val.valuedate)
            entry_data.set_valuetime(entry_val.valuetime)
            entry_data.set_cbsdate(entry_val.cbsdate)
            entry_data.set_localcurrency(entry_val.localcurrency)
            entry_data.set_localexchangerate(entry_val.localexchangerate)
            entry_data.set_currency(entry_val.currency)
            entry_data.set_exchangerate(entry_val.exchangerate)
            entry_data.set_isprevyrentry(entry_val.isprevyrentry)
            entry_data.set_reversalentry(entry_val.reversalentry)
            entry_data.set_refno(entry_val.refno)
            entry_data.set_crno(entry_val.crno)
            entry_data.set_refid(entry_val.refid)
            entry_data.set_reftableid(entry_val.reftableid)
            entry_data.set_type(entry_val.type)
            entry_data.set_gl(entry_val.gl)
            entry_data.set_apcatno(entry_val.apcatno)
            entry_data.set_apsubcatno(entry_val.apsubcatno)
            entry_data.set_wisefinmap(entry_val.wisefinmap)
            entry_data.set_glremarks(entry_val.glremarks)
            entry_data.set_amount(entry_val.amount)
            entry_data.set_ackrefno(entry_val.ackrefno)
            entry_data.set_fcamount(entry_val.fcamount)
            entry_data.set_entry_status(entry_val.entry_status)
            return entry_data
        except Entry.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.NO_DATA)
            return error_obj

    def fetch_commonentry(self,crno,user_id):
            conditions=Q(crno=crno)& Q(status=1)
            entrydetails = Entry.objects.using(self._current_app_schema()).filter(conditions)
            list_length = len(entrydetails)
            entry_list_data = NWisefinList()
            if list_length <= 0:
                pass
            else:
                for entry_val in entrydetails:
                    entry_data = EntryResponse()
                    entry_data.set_id(entry_val.id)
                    entry_data.set_branch_id(entry_val.entry_status)
                    entry_data.set_fiscalyear(entry_val.fiscalyear)
                    entry_data.set_period(entry_val.period)
                    entry_data.set_module(entry_val.module)
                    entry_data.set_screen(entry_val.screen)
                    entry_data.set_transactiondate(entry_val.transactiondate)
                    entry_data.set_transactiontime(entry_val.transactiontime)
                    entry_data.set_valuedate(entry_val.valuedate)
                    entry_data.set_valuetime(entry_val.valuetime)
                    entry_data.set_cbsdate(entry_val.cbsdate)
                    entry_data.set_localcurrency(entry_val.localcurrency)
                    entry_data.set_localexchangerate(entry_val.localexchangerate)
                    entry_data.set_currency(entry_val.currency)
                    entry_data.set_exchangerate(entry_val.exchangerate)
                    entry_data.set_isprevyrentry(entry_val.isprevyrentry)
                    entry_data.set_reversalentry(entry_val.reversalentry)
                    entry_data.set_refno(entry_val.refno)
                    entry_data.set_crno(entry_val.crno)
                    entry_data.set_refid(entry_val.refid)
                    entry_data.set_reftableid(entry_val.reftableid)
                    entry_data.set_type(entry_val.type)
                    entry_data.set_gl(entry_val.gl)
                    entry_data.set_apcatno(entry_val.apcatno)
                    entry_data.set_apsubcatno(entry_val.apsubcatno)
                    entry_data.set_wisefinmap(entry_val.wisefinmap)
                    entry_data.set_glremarks(entry_val.glremarks)
                    entry_data.set_amount(entry_val.amount)
                    entry_data.set_ackrefno(entry_val.ackrefno)
                    entry_data.set_fcamount(entry_val.fcamount)
                    entry_data.set_errordescription(entry_val.errordescription)
                    entry_data.set_entry_status(entry_val.entry_status)
                    entry_data.set_group_id(entry_val.group_id)
                    entry_data.set_glnodescription(entry_val.glnodescription)
                    entry_data.set_is_error(entry_val.is_error)
                    entry_data.set_bulk_status(entry_val.bulk_status)
                    entry_data.set_bulk_is_error(entry_val.bulk_is_error)
                    entry_data.set_bulk_errordescription(entry_val.bulk_errordescription)
                    entry_data.set_entry_new_data(entry_val)
                    entry_list_data.append(entry_data)
                    #vpage = VysfinPaginator(entrydetails, vys_page.get_index(), 10)
                    #entry_list_data.set_pagination(vpage)
            return entry_list_data

    def update_oracelstatus(self,entry_obj,emp_id):
            try:
                entry_id=entry_obj['id']
                entry_status=entry_obj['entry_status']
                is_error=entry_obj['is_error']
                errordescription=entry_obj['errordescription']
                Entry_Detail = Entry.objects.using(self._current_app_schema()).filter(id=entry_id).update(
                                                     entry_status = entry_status,
                                                     is_error = is_error,
                                                     errordescription = errordescription,
                                                     updated_by=emp_id,
                                                     updated_date=now())
                #EntryDetail = Entry.objects.get(id=entry_obj.get_id())
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)

            except Exception as excep:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(str(excep))
                return error_obj
            return success_obj

    def update_oracle_bulk_status(self,entry_obj,emp_id):
            try:
                CR_number=entry_obj['CR_Number']
                entry_process_id=entry_obj['Process_id']
                bulk_status=entry_obj['bulk_status']
                bulk_is_error=entry_obj['bulk_is_error']
                bulk_errordescription=entry_obj['bulk_errordescription']
                Entry_Detail = Entry.objects.using(self._current_app_schema()).filter(crno=CR_number).update(
                                                     entry_process_id = entry_process_id,
                                                     bulk_status = bulk_status,
                                                     bulk_is_error = bulk_is_error,
                                                     bulk_errordescription = bulk_errordescription,
                                                     updated_by=emp_id,
                                                     updated_date=now())
                #EntryDetail = Entry.objects.get(id=entry_obj.get_id())
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)

            except Exception as excep:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(str(excep))
                return error_obj
            return success_obj

    def oracle_fetch_commonentry(self, crno,AP_Type,ap_data,user_id):
        module = moduletype.get_value_to_id(AP_Type)
        conditions = Q(crno=crno) & Q(module=module) & Q(status=1)
        entrydetails = Entry.objects.using(self._current_app_schema()).filter(conditions)
        list_length = len(entrydetails)
        entry_list_data = NWisefinList()
        if list_length <= 0:
            return entry_list_data
        else:
            for entry_val in entrydetails:
                entry_data = OracleEntryResponse()
                if (entry_val.segment_1 is None or entry_val.segment_1 == "" or entry_val.segment_2 is None or entry_val.segment_2 == "" or
                        entry_val.segment_3 is None or entry_val.segment_3 == "" or entry_val.segment_4 is None or entry_val.segment_4 == "" or
                        entry_val.segment_5 is None or entry_val.segment_5 == "" or entry_val.segment_6 is None or entry_val.segment_6 == "" or
                        entry_val.segment_7 is None or entry_val.segment_7 == "" or entry_val.segment_8 is None or entry_val.segment_8 == "" or
                        entry_val.segment_9 is None or entry_val.segment_9 == "" or entry_val.segment_10 is None or entry_val.segment_10 == "" or
                        entry_val.reference_10 is None or entry_val.reference_10 == ""):
                    entry_data.set_Message("FAIL")
                    entry_data.set_desc("Entry segment or reference is None")
                    entry_list_data.append(entry_data)
                    return entry_list_data
            for entry_val in entrydetails:
                entry_data = OracleEntryResponse()
                entry_data.set_Message("SUCCESS")
                entry_data.set_id(entry_val.id)
                entry_data.set_branch_id(entry_val.entry_status)
                entry_data.set_fiscalyear(entry_val.fiscalyear)
                entry_data.set_period(entry_val.period)
                entry_data.set_module(entry_val.module)
                entry_data.set_screen(entry_val.screen)
                entry_data.set_transactiondate(entry_val.transactiondate)
                entry_data.set_transactiontime(entry_val.transactiontime)
                entry_data.set_valuedate(entry_val.valuedate)
                entry_data.set_valuetime(entry_val.valuetime)
                entry_data.set_cbsdate(entry_val.cbsdate)
                entry_data.set_localcurrency(entry_val.localcurrency)
                entry_data.set_localexchangerate(entry_val.localexchangerate)
                entry_data.set_currency(entry_val.currency)
                entry_data.set_exchangerate(entry_val.exchangerate)
                entry_data.set_isprevyrentry(entry_val.isprevyrentry)
                entry_data.set_reversalentry(entry_val.reversalentry)
                entry_data.set_refno(entry_val.refno)
                entry_data.set_crno(entry_val.crno)
                entry_data.set_refid(entry_val.refid)
                entry_data.set_reftableid(entry_val.reftableid)
                entry_data.set_type(entry_val.type)
                entry_data.set_gl(entry_val.gl)
                entry_data.set_apcatno(entry_val.apcatno)
                entry_data.set_apsubcatno(entry_val.apsubcatno)
                entry_data.set_wisefinmap(entry_val.wisefinmap)
                entry_data.set_glremarks(entry_val.glremarks)
                entry_data.set_amount(entry_val.amount)
                entry_data.set_ackrefno(entry_val.ackrefno)
                entry_data.set_fcamount(entry_val.fcamount)
                entry_data.set_entry_status(entry_val.entry_status)
                entry_data.set_entry_oracle_data(entry_val,AP_Type,ap_data)
                entry_list_data.append(entry_data)
                # vpage = VysfinPaginator(entrydetails, vys_page.get_index(), 10)
                # entry_list_data.set_pagination(vpage)
        return entry_list_data

    def entry_failed_transactions(self,entry_obj,vys_page,emp_id):
        cr_number=entry_obj.get('CR_Number')
        branch_id=entry_obj.get('Branch_id')
        if(cr_number==""):
            cr_number=None
        if(branch_id==""):
            branch_id=None
        if(cr_number==None and branch_id==None):
            conditions = Q(entry_status=0) & Q(is_error=1)
            entrydetails = Entry.objects.using(self._current_app_schema()).filter(conditions)[vys_page.get_offset():vys_page.get_query_limit()]
            #entrydetails = Entry.objects.using(self._current_app_schema()).all()[vys_page.get_offset():vys_page.get_query_limit()]
        else:
            if(cr_number!=None and branch_id!=None):
                conditions = Q(entry_status=0)& Q(is_error=1) & Q(crno=cr_number) & Q(branch_id=branch_id)
                entrydetails = Entry.objects.using(self._current_app_schema()).filter(conditions)[vys_page.get_offset():vys_page.get_query_limit()]
            elif(cr_number!=None):
                conditions = Q(entry_status=0) & Q(is_error=1) & Q(crno=cr_number)
                entrydetails = Entry.objects.using(self._current_app_schema()).filter(conditions)[vys_page.get_offset():vys_page.get_query_limit()]
            elif(branch_id!=None):
                conditions = Q(entry_status=0) & Q(is_error=1) & Q(branch_id=branch_id)
                entrydetails = Entry.objects.using(self._current_app_schema()).filter(conditions)[vys_page.get_offset():vys_page.get_query_limit()]

        list_length = len(entrydetails)
        entry_list_data = NWisefinList()
        if list_length <= 0:
            return entry_list_data
        else:
            for entry_val in entrydetails:
                entry_data = EntryResponse()
                entry_data.set_id(entry_val.id)
                entry_data.set_branch_id(entry_val.entry_status)
                entry_data.set_fiscalyear(entry_val.fiscalyear)
                entry_data.set_period(entry_val.period)
                entry_data.set_module(entry_val.module)
                entry_data.set_screen(entry_val.screen)
                entry_data.set_transactiondate(entry_val.transactiondate)
                entry_data.set_transactiontime(entry_val.transactiontime)
                entry_data.set_valuedate(entry_val.valuedate)
                entry_data.set_valuetime(entry_val.valuetime)
                entry_data.set_cbsdate(entry_val.cbsdate)
                entry_data.set_localcurrency(entry_val.localcurrency)
                entry_data.set_localexchangerate(entry_val.localexchangerate)
                entry_data.set_currency(entry_val.currency)
                entry_data.set_exchangerate(entry_val.exchangerate)
                entry_data.set_isprevyrentry(entry_val.isprevyrentry)
                entry_data.set_reversalentry(entry_val.reversalentry)
                entry_data.set_refno(entry_val.refno)
                entry_data.set_crno(entry_val.crno)
                entry_data.set_refid(entry_val.refid)
                entry_data.set_reftableid(entry_val.reftableid)
                entry_data.set_type(entry_val.type)
                entry_data.set_gl(entry_val.gl)
                entry_data.set_apcatno(entry_val.apcatno)
                entry_data.set_apsubcatno(entry_val.apsubcatno)
                entry_data.set_wisefinmap(entry_val.wisefinmap)
                entry_data.set_glremarks(entry_val.glremarks)
                entry_data.set_amount(entry_val.amount)
                entry_data.set_ackrefno(entry_val.ackrefno)
                entry_data.set_fcamount(entry_val.fcamount)
                entry_data.set_entry_status(entry_val.entry_status)
                entry_data.set_errordescription(entry_val.errordescription)
                entry_list_data.append(entry_data)
                vpage = NWisefinPaginator(entrydetails, vys_page.get_index(), 10)
                entry_list_data.set_pagination(vpage)
            return entry_list_data
    def inactiveentry(self,crno,emp_id,ap_type):
            try:
                module=moduletype.get_value_to_id(ap_type)
                condition=Q(crno=crno)&Q(module=module)
                entryinactive = Entry.objects .using(self._current_app_schema())\
                    .filter(condition).update(updated_by=emp_id,status=0,
                                                 updated_date=now())
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.CREATE_MESSAGE)

            except Exception as excep:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(str(excep))
                return error_obj
            return success_obj


    def entry_success_transactions(self,entry_obj,offset,limit,emp_id,scope):
        ap_db = APDBService(scope)
        Dynamic_schema = ap_db.get_ap_schema()
        DB_NAME_apdb = DATABASES.get(Dynamic_schema).get("NAME")

        mst_db = MASTERDBService(scope)
        Dynamicmst_schema = mst_db.get_master_schema()
        DB_NAME_masterdb = DATABASES.get(Dynamicmst_schema).get("NAME")

        entry_db = ENTRYDBService(scope)
        Dynamicmst_schema = entry_db.get_entry_schema()
        DB_NAME_entrydb = DATABASES.get(Dynamicmst_schema).get("NAME")

        from_date=""
        to_date=""
        from_date=entry_obj.get("transaction_from_date")
        to_date=entry_obj.get("transaction_to_date")
        Query_columns=""
        Query_limit=" LIMIT "+str(limit)+" OFFSET "+str(offset)
        if(from_date!="" and to_date!=""):
            Query_columns="(entry.transactiondate BETWEEN "+"'"+str(from_date) +"'"+" AND "+"'" +str(to_date) +"'"+")"
        else:
            if(from_date!=""):
                Query_columns = "(entry.transactiondate = "+"'"+str(from_date) +"'"+")"

        Dynamic_query=(" select entry.id,entry.crno,entry.branch_id as apinvoicebranch_id,date_format(entry.transactiondate,'%Y-%m-%d') as transactiondate, "
                       " date_format(entry.valuedate,'%Y-%m-%d') as valuedate,entry.amount,case when entry.type=1 then "                      
                       " 'DEBIT' else 'CREDIT' end as 'type',a.id as ap_invoice_id,a.client_code as client_id, "
                        " (case when (entry.module = '1') then coalesce('AP') "
                       " when (entry.module = '2' ) then coalesce('PAYMENT') "
                       " when (entry.module = '3' ) then coalesce('JV') "
                       " end) as entry_module, "
                       " b.taxamount as tax_amount,b.otheramount as other_amount,b.totalamount, "
                       " b.supplier_id as apinvoicesupplier_id,c.id as apinvoicedetails_id,p.id as product_id, "
                       " cat.id as categorygid,cat.expense_id as apexpense_id,sub.id as apsubcat_id,cc.id as cc_id,exps.exp_grp_id as expense_group_id, "
                       " bs.id as bs_id,masterbussinesssegment_id as biz_id, "
                       " 1 as sector_id from "+str(DB_NAME_entrydb)+" .entryservice_entry as entry "
                       " inner join "+str(DB_NAME_apdb)+" .apservice_apheader as a on a.crno=entry.crno "
                       " inner join "+str(DB_NAME_apdb)+" .apservice_apinvoiceheader as b on b.apheader_id=a.id "
                       " inner join "+str(DB_NAME_apdb)+" .apservice_apinvoicedetail as c on c.apinvoiceheader_id=b.id "
                       " inner join "+str(DB_NAME_masterdb)+" .masterservice_product as p on p.code=c.productcode "
                       " inner join "+str(DB_NAME_apdb)+" .apservice_apdebit as debits on debits.apinvoiceheader_id=b.id "
                       " inner join "+str(DB_NAME_masterdb)+" .masterservice_apcategory as cat on cat.code=debits.category_code "
                       " inner join "+str(DB_NAME_masterdb)+" .masterservice_apsubcategory as sub on sub.no=entry.apsubcatno and sub.glno=entry.gl "
                       " left join "+str(DB_NAME_apdb)+" .apservice_apccbsdetails as ccbs on ccbs.apdebit_id=debits.id "
                       " left join "+str(DB_NAME_masterdb)+" .masterservice_costcentre as cc on cc.code=ccbs.cc_code "
                       " left join "+str(DB_NAME_masterdb)+" .masterservice_businesssegment as bs on bs.code=ccbs.bs_code "
                       " left join "+str(DB_NAME_masterdb)+" .masterservice_apexpense as exps on exps.id=cat.expense_id "
                       " where entry.entry_status=1 and entry.is_error=0 and entry.status=1 and exps.status=1 and "
                       " a.is_delete=0 and b.is_delete=0 and c.is_delete=0  and"
                       " p.status=1 and ccbs.is_delete=0 and debits.is_delete=0 and cat.status=1 and sub.status=1 and "
                        +Query_columns+
                        " group by entry.id"
                       +Query_limit+" ")

        with connection.cursor() as cursor:
            print(Dynamic_query)
            cursor.execute(Dynamic_query)
            columns = [x[0] for x in cursor.description]
            rows = cursor.fetchall()
            rows = list(rows)
            df_data = pd.DataFrame(rows, columns=columns)
            resp = {"Message": "Found","total_records":"", "DATA":json.loads(df_data.to_json(orient='records'))}
            total_records=len(resp['DATA'])
            if ( total_records!= 0):
                resp['total_records']=total_records
                return resp
            else:
                resp1 = {"Message": "Not Found", "DATA": json.loads(df_data.to_json(orient='records'))}
                return resp1


        # if(to_date==None or to_date==""):
        #     conditions = Q(entry_status=1) & Q(is_error=0) & Q(status=1) & Q(transactiondate=from_date)
        # else:
        #     conditions = Q(entry_status=1) & Q(is_error=0) & Q(status=1) & Q(transactiondate__range=[from_date,to_date])
        # entrydetails = Entry.objects.using(self._current_app_schema()).filter(conditions)[offset:limit]
        # #print("Total row",offset,limit)
        # total_entrydetails = Entry.objects.using(self._current_app_schema()).filter(conditions)
        # #entrydetails = Entry.objects.using(self._current_app_schema()).all()[vys_page.get_offset():vys_page.get_query_limit()]
        # total_entrydetails_len=len(total_entrydetails)
        # list_length = len(entrydetails)
        # entry_list_data = NWisefinList()
        # if list_length <= 0:
        #     return entry_list_data
        # else:
        #     for entry_val in entrydetails:
        #         entry_data = EntryResponse()
        #         entry_data.set_id(entry_val.id)
        #         entry_data.set_branch_id(entry_val.entry_status)
        #         entry_data.set_period(entry_val.period)
        #         entry_data.set_module(entry_val.module)
        #         entry_data.set_transactiondate(entry_val.transactiondate)
        #         entry_data.set_transactiontime(entry_val.transactiontime)
        #         entry_data.set_valuedate(entry_val.valuedate)
        #         entry_data.set_valuetime(entry_val.valuetime)
        #         entry_data.set_cbsdate(entry_val.cbsdate)
        #         entry_data.set_refno(entry_val.refno)
        #         entry_data.set_crno(entry_val.crno)
        #         entry_data.set_type(entry_val.type)
        #         entry_data.set_gl(entry_val.gl)
        #         entry_data.set_apcatno(entry_val.apcatno)
        #         entry_data.set_apsubcatno(entry_val.apsubcatno)
        #         entry_data.set_amount(entry_val.amount)
        #         entry_data.set_fcamount(entry_val.fcamount)
        #         entry_data.set_entry_status(entry_val.entry_status)
        #         # if (offset == 0):
        #         entry_data.set_total_row(total_entrydetails_len)
        #         entry_list_data.append(entry_data)
        #         entry_data.set_current_total_row(list_length)
        #         #else:
        #         entry_data.set_current_total_row(list_length)
        #         entry_list_data.append(entry_data)
        #         #vpage = NWisefinPaginator(entrydetails, vys_page.get_index(), 10)
        #         #entry_list_data.set_pagination(vpage)
        #     return entry_list_data