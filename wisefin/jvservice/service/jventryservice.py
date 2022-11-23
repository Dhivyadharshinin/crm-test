import json
import traceback
#test
from django.db.models import Q

from entryservice.data.request.entryoraclecommonrequest import OracleRequest
from jvservice.data.response.jvauditresponse import JVAuditResponse
from jvservice.data.response.jvdetailresponse import JVDetailEntryresponse
from jvservice.data.response.jventryresponse import JVEntryresponse
from jvservice.data.response.jvfileresponse import jvfileResponse
from jvservice.models import JournalEntry, JVQueue, JournalDetailEntry, JVFiles
from jvservice.service.jvauditservice import JVAuditService
from jvservice.util.jvutil import JVRefType, JVModifyStatus, JournalStatus, JournalType, JournalDetailType
from django.utils.timezone import now

from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus
from utilityservice.service.utilityservice import NWisefinUtilityService
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from datetime import datetime

utilityservice=NWisefinUtilityService()
class JVEntryService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.JV_SERVICE)

    def jventrycreate(self,request,jve_obj,emp_id):
        try:
            jventry = JournalEntry.objects.using(self._current_app_schema()).create(
                jemode=jve_obj.get_jemode(),
                jebranch=jve_obj.get_jebranch(),
                jetype=jve_obj.get_jetype(),
                jerefno=jve_obj.get_jerefno(),
                jedescription=jve_obj.get_jedescription(),
                jetransactiondate=jve_obj.get_jetransactiondate(),
                jeamount=jve_obj.get_jeamount(),
                jestatus=JournalStatus.PENDING_FOR_APPROVAL,
                created_by=emp_id,
                entity_id=self._entity_id())

            code = "JV"+ str(datetime.now().strftime("%y%m%d")) + str(jventry.id).zfill(5)
            jventry.jecrno = code
            jventry.save()
            self.audit_function(jventry, jventry.id, jventry.id, emp_id,
                                JVModifyStatus.CREATE, JVRefType.JournalEntry)
            JVQueue.objects.using(self._current_app_schema()).create(ref_id=jventry.id, ref_type=JVRefType.JournalEntry,
                                                                      from_user_id=emp_id, to_user_id=emp_id,
                                                                      created_date=now(),
                                                                      comments="New",
                                                                      is_sys=True,
                                                                      entity_id=self._entity_id()
                                                                      )
            jve_data = JVEntryresponse()
            jve_data.set_id(jventry.id)
            jve_data.set_jecrno(jventry.jecrno)
            jve_data.set_jemode(jventry.jemode)
            jve_data.set_jebranch(jventry.jebranch)
            jve_data.set_jetype(jventry.jetype)
            jve_data.set_jerefno(jventry.jerefno)
            jve_data.set_jedescription(jventry.jedescription)
            jve_data.set_jeamount(jventry.jeamount)
            jve_data.set_jestatus(jventry.jestatus)
            jve_data.set_jetransactiondate(jventry.jetransactiondate)
            return jve_data
        except Exception as e:
            traceback.print_exc(True)
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            error_obj.set_description(str(e))
            return error_obj

    def fetch_journal_list(self, request,vys_page):
        try:
            condition = Q(status=1)
            journal_header = JournalEntry.objects.using(self._current_app_schema()).filter(condition).order_by('-created_date')[vys_page.get_offset():vys_page.get_query_limit()]
            list_len = len(journal_header)
            pro_list = NWisefinList()
            if list_len > 0:
                for jventry in journal_header:
                    from utilityservice.service import api_service
                    api_serv = api_service.ApiService(self._scope())
                    jve_data = JVEntryresponse()
                    jve_data.set_id(jventry.id)
                    jve_data.set_jecrno(jventry.jecrno)
                    jve_data.set_jemode(jventry.jemode)
                    empbranch = api_serv.get_empbranch_id(request, jventry.jebranch)
                    jve_data.set_jebranch(empbranch)
                    jve_data.set_jetype_id(jventry.jetype)
                    if jventry.jetype == JournalType.NEW_ENTRY:
                        jve_data.set_jetype(JournalType.NEW_ENTRY_TYPE)
                    if jventry.jetype == JournalType.RECTIFICATION_ENTRY:
                        jve_data.set_jetype(JournalType.RECTIFICATION_ENTRY_TYPE)
                    if jventry.jetype == JournalType.TA_ENTRY:
                        jve_data.set_jetype(JournalType.TA_ENTRY_TYPE)
                    if jventry.jetype == JournalType.PROVISION_ENTRY:
                        jve_data.set_jetype(JournalType.PROVISION_ENTRY_TYPE)
                    jve_data.set_jerefno(jventry.jerefno)
                    jve_data.set_jedescription(jventry.jedescription)
                    jve_data.set_jeamount(jventry.jeamount)
                    jve_data.set_jestatus_id(jventry.jestatus)
                    if jventry.jestatus == JournalStatus.PENDING_FOR_APPROVAL:
                        jve_data.set_jestatus(JournalStatus.PENDING_FOR_APPROVAL_TYPE)
                    if jventry.jestatus == JournalStatus.APPROVED:
                        jve_data.set_jestatus(JournalStatus.APPROVED_TYPE)
                    if jventry.jestatus == JournalStatus.REJECTED:
                        jve_data.set_jestatus(JournalStatus.REJECTED_TYPE)
                    if jventry.jestatus == JournalStatus.DELETED:
                        jve_data.set_jestatus(JournalStatus.DELETED_TYPE)
                    jve_data.set_jetransactiondate(jventry.jetransactiondate)
                    emp_name = api_serv.get_empsingle_id(request,jventry.created_by)
                    jve_data.set_created_by(emp_name)
                    pro_list.append(jve_data)
                vpage = NWisefinPaginator(journal_header, vys_page.get_index(), 10)
                pro_list.set_pagination(vpage)
            return pro_list
        except Exception as e:
            traceback.print_exc(True)
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            error_obj.set_description(str(e))
            return error_obj


    def fetch_jventry(self,request,jv_id):
        try:
            jventry = JournalEntry.objects.using(self._current_app_schema()).get(id=jv_id,entity_id=self._entity_id())
            jvid = jventry.id

            from utilityservice.service import api_service
            api_serv = api_service.ApiService(self._scope())
            jve_data = JVEntryresponse()
            # jve_data.set_id(jventry.id)
            jve_data.set_jecrno(jventry.jecrno)
            jve_data.set_jemode(jventry.jemode)
            empbranch = api_serv.get_empbranch_id(request, jventry.jebranch)
            jve_data.set_jebranch(empbranch)
            jve_data.set_jetype_id(jventry.jetype)
            if jventry.jetype == JournalType.NEW_ENTRY:
                jve_data.set_jetype(JournalType.NEW_ENTRY_TYPE)
            if jventry.jetype == JournalType.RECTIFICATION_ENTRY:
                jve_data.set_jetype(JournalType.RECTIFICATION_ENTRY_TYPE)
            if jventry.jetype == JournalType.TA_ENTRY:
                jve_data.set_jetype(JournalType.TA_ENTRY_TYPE)
            if jventry.jetype == JournalType.PROVISION_ENTRY:
                jve_data.set_jetype(JournalType.PROVISION_ENTRY_TYPE)
            jve_data.set_jerefno(jventry.jerefno)
            jve_data.set_jedescription(jventry.jedescription)
            jve_data.set_jeamount(jventry.jeamount)
            jve_data.set_jestatus_id(jventry.jestatus)
            if jventry.jestatus == JournalStatus.PENDING_FOR_APPROVAL:
                jve_data.set_jestatus(JournalStatus.PENDING_FOR_APPROVAL_TYPE)
            if jventry.jestatus == JournalStatus.APPROVED:
                jve_data.set_jestatus(JournalStatus.APPROVED_TYPE)
            if jventry.jestatus == JournalStatus.REJECTED:
                jve_data.set_jestatus(JournalStatus.REJECTED_TYPE)
            if jventry.jestatus == JournalStatus.DELETED:
                jve_data.set_jestatus(JournalStatus.DELETED_TYPE)
            jve_data.set_jetransactiondate(jventry.jetransactiondate)
            jvdentry = JournalDetailEntry.objects.using(self._current_app_schema()).filter(jeentry_id=jv_id,status=1,entity_id=self._entity_id())
            jvelist = []
            for jvdentry in jvdentry:
                jved_data = JVDetailEntryresponse()
                jved_data.set_id(jvdentry.id)
                jved_data.set_jeentry_id(jvdentry.jeentry_id)
                jved_data.set_jedtype_id(jvdentry.jedtype)
                if jvdentry.jedtype == JournalDetailType.CREDIT:
                    jved_data.set_jedtype(JournalDetailType.CREDIT_TYPE)
                if jvdentry.jedtype == JournalDetailType.DEBIT:
                    jved_data.set_jedtype(JournalDetailType.DEBIT_TYPE)
                jved_data.set_jeddescription(jvdentry.jeddescription)
                jved_data.set_jedamount(jvdentry.jedamount)
                cat = api_serv.get_cat_code(request, jvdentry.jedcat_code)
                sub = api_serv.get_subcat_code(request, jvdentry.jedsubcat_code)
                jved_data.set_jedcat_code(cat)
                jved_data.set_jedsubcat_code(sub)
                jved_data.set_jedglno(jvdentry.jedglno)
                cc = api_serv.get_cc_code(request, jvdentry.jedcc_code)
                bs = api_serv.get_bs_code(request, jvdentry.jedbs_code)
                jved_data.set_jedcc_code(cc)
                jved_data.set_jedbs_code(bs)
                empbranch = api_serv.get_empbranch_id(request, jvdentry.jedbranch)
                jved_data.set_jedbranch(empbranch)
                jvelist.append(json.loads(jved_data.get()))
                # jve_listdata.append(jvelist)
            jve_data.set_journaldetails(jvelist)
            invfile = JVFiles.objects.using(self._current_app_schema()).filter(jvfile_id=jv_id,status=1,entity_id=self._entity_id())
            print(invfile)
            list_lent = len(invfile)
            pro_list2 = list()
            if list_lent > 0:
                for invf in invfile:
                    dtpc_res = jvfileResponse()
                    dtpc_res.set_id(invf.id)
                    dtpc_res.set_file_id(invf.file_id)
                    dtpc_res.set_file_name(invf.file_name)
                    pro_list2.append(dtpc_res)
            jve_data.set_file_data(pro_list2)
            return jve_data
        except JournalEntry.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code("Invalid JournalEntry_Id")
            error_obj.set_description("Please give correct JournalEntry ID")
            return error_obj

    def search_jv(self, request,vys_page,jecrno,jestatus,jeamount,jerefno,jetype,jebranch,created_by):
        try:
            condition = Q(jecrno__icontains=jecrno) & Q(jestatus__icontains=jestatus) & Q(jeamount__icontains=jeamount) \
                        & Q(jerefno__icontains=jerefno) & Q(jetype__icontains=jetype) & Q(jebranch__icontains=jebranch) \
                        & Q(created_by__icontains=created_by)
            jentry = JournalEntry.objects.using(self._current_app_schema()).filter(condition).order_by('created_date')[vys_page.get_offset():vys_page.get_query_limit()]
            list_length = len(jentry)
            print(list_length)
            loandata_list_data = NWisefinList()
            if list_length > 0:
                for jventry in jentry:
                    from utilityservice.service import api_service
                    api_serv = api_service.ApiService(self._scope())
                    jve_data = JVEntryresponse()
                    jve_data.set_id(jventry.id)
                    jve_data.set_jecrno(jventry.jecrno)
                    jve_data.set_jemode(jventry.jemode)
                    empbranch = api_serv.get_empbranch_id(request, jventry.jebranch)
                    jve_data.set_jebranch(empbranch)
                    jve_data.set_jetype_id(jventry.jetype)
                    if jventry.jetype == JournalType.NEW_ENTRY:
                        jve_data.set_jetype(JournalType.NEW_ENTRY_TYPE)
                    if jventry.jetype == JournalType.RECTIFICATION_ENTRY:
                        jve_data.set_jetype(JournalType.PROVISION_ENTRY_TYPE)
                    if jventry.jetype == JournalType.TA_ENTRY:
                        jve_data.set_jetype(JournalType.TA_ENTRY_TYPE)
                    if jventry.jetype == JournalType.PROVISION_ENTRY:
                        jve_data.set_jetype(JournalType.PROVISION_ENTRY_TYPE)
                    jve_data.set_jerefno(jventry.jerefno)
                    jve_data.set_jedescription(jventry.jedescription)
                    jve_data.set_jeamount(jventry.jeamount)
                    jve_data.set_jestatus_id(jventry.jestatus)
                    if jventry.jestatus == JournalStatus.PENDING_FOR_APPROVAL:
                        jve_data.set_jestatus(JournalStatus.PENDING_FOR_APPROVAL_TYPE)
                    if jventry.jestatus == JournalStatus.APPROVED:
                        jve_data.set_jestatus(JournalStatus.APPROVED_TYPE)
                    if jventry.jestatus == JournalStatus.REJECTED:
                        jve_data.set_jestatus(JournalStatus.REJECTED_TYPE)
                    if jventry.jestatus == JournalStatus.DELETED:
                        jve_data.set_jestatus(JournalStatus.DELETED_TYPE)
                    jve_data.set_jetransactiondate(jventry.jetransactiondate)
                    emp_name = api_serv.get_empsingle_id(request, jventry.created_by)
                    jve_data.set_created_by(emp_name)
                    loandata_list_data.append(jve_data)
                    vpage = NWisefinPaginator(jentry, vys_page.get_index(), 10)
                    loandata_list_data.set_pagination(vpage)
            return loandata_list_data
        except Exception as e:
            traceback.print_exc(True)
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            error_obj.set_description(str(e))
            return error_obj

    def audit_function(self, audit_data, refid, relrefid, emp_id, action, reqstatus):
        if action == JVModifyStatus.DELETE:
            data = None
        else:
            data = audit_data.__dict__
            del data['_state']
        audit_service = JVAuditService(self._scope())
        audit_obj = JVAuditResponse()
        audit_obj.set_refid(refid)
        audit_obj.set_reqstatus(reqstatus)
        audit_obj.set_reftype(JVRefType.JournalEntry)
        audit_obj.set_relrefid(relrefid)
        audit_obj.set_relreftype(JVRefType.JournalEntry)
        audit_obj.set_userid(emp_id)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)

    def fetch_journalaprvl_list(self, request,vys_page):
        try:
            condition = Q(status=1)&Q(jestatus=1)
            journal_header = JournalEntry.objects.using(self._current_app_schema()).filter(condition).order_by('-created_date')[vys_page.get_offset():vys_page.get_query_limit()]
            list_len = len(journal_header)
            pro_list = NWisefinList()
            if list_len > 0:
                for jventry in journal_header:
                    from utilityservice.service import api_service
                    api_serv = api_service.ApiService(self._scope())
                    jve_data = JVEntryresponse()
                    jve_data.set_id(jventry.id)
                    jve_data.set_jecrno(jventry.jecrno)
                    jve_data.set_jemode(jventry.jemode)
                    empbranch = api_serv.get_empbranch_id(request, jventry.jebranch)
                    jve_data.set_jebranch(empbranch)
                    jve_data.set_jetype_id(jventry.jetype)
                    if jventry.jetype == JournalType.NEW_ENTRY:
                        jve_data.set_jetype(JournalType.NEW_ENTRY_TYPE)
                    if jventry.jetype == JournalType.RECTIFICATION_ENTRY:
                        jve_data.set_jetype(JournalType.RECTIFICATION_ENTRY_TYPE)
                    if jventry.jetype == JournalType.TA_ENTRY:
                        jve_data.set_jetype(JournalType.TA_ENTRY_TYPE)
                    if jventry.jetype == JournalType.PROVISION_ENTRY:
                        jve_data.set_jetype(JournalType.PROVISION_ENTRY_TYPE)
                    jve_data.set_jerefno(jventry.jerefno)
                    jve_data.set_jedescription(jventry.jedescription)
                    jve_data.set_jeamount(jventry.jeamount)
                    jve_data.set_jestatus_id(jventry.jestatus)
                    if jventry.jestatus == JournalStatus.PENDING_FOR_APPROVAL:
                        jve_data.set_jestatus(JournalStatus.PENDING_FOR_APPROVAL_TYPE)
                    if jventry.jestatus == JournalStatus.APPROVED:
                        jve_data.set_jestatus(JournalStatus.APPROVED_TYPE)
                    if jventry.jestatus == JournalStatus.REJECTED:
                        jve_data.set_jestatus(JournalStatus.REJECTED_TYPE)
                    if jventry.jestatus == JournalStatus.DELETED:
                        jve_data.set_jestatus(JournalStatus.DELETED_TYPE)
                    jve_data.set_jetransactiondate(jventry.jetransactiondate)
                    emp_name = api_serv.get_empsingle_id(request, jventry.created_by)
                    jve_data.set_created_by(emp_name)
                    pro_list.append(jve_data)
                vpage = NWisefinPaginator(journal_header, vys_page.get_index(), 10)
                pro_list.set_pagination(vpage)
            return pro_list
        except Exception as e:
            traceback.print_exc(True)
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            error_obj.set_description(str(e))
            return error_obj

    def Delete_jventry(self,request, jv_id, emp_id):
        try:
            jventry = JournalEntry.objects.using(self._current_app_schema()).filter(id=jv_id,entity_id=self._entity_id()).update(jestatus=JournalStatus.DELETED,
                                                                      status=0,
                                                                      updated_by=emp_id,
                                                                      updated_date=now())
            jventry = JournalEntry.objects.using(self._current_app_schema()).get(id=jv_id)
            self.audit_function(jventry, jventry.id, jventry.id, emp_id,
                                JVModifyStatus.UPDATE, JVRefType.JournalEntry)
            JVQueue.objects.using(self._current_app_schema()).create(ref_id=jventry.id, ref_type=JVRefType.JournalEntry, from_user_id=emp_id,
                                    to_user_id=emp_id,
                                    created_date=now(),
                                    comments="DELETE",
                                    is_sys=True,
                                    entity_id=self._entity_id()
                                    )
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            # success_obj.set_message(SuccessMessage.APPROVED_MESSAGE)
            return success_obj

        except Exception as e:
            traceback.print_exc(True)
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            error_obj.set_description(str(e))
            return error_obj

    def status_UpdateRejected(self, request,ecf_obj, emp_id):
        try:
            ecf = JournalEntry.objects.using(self._current_app_schema()).get(id=ecf_obj.get_id())
            creatby = ecf.created_by
            if creatby != emp_id:
                Ecfhdr = JournalEntry.objects.using(self._current_app_schema()).filter(id=ecf_obj.get_id(),entity_id=self._entity_id(),status=1).update(
                                                                    jestatus=JournalStatus.REJECTED,
                                                                    jedescription = ecf_obj.get_jedescription(),
                                                                    updated_by=emp_id,
                                                                    updated_date=now())
                ecf = JournalEntry.objects.using(self._current_app_schema()).get(id=ecf_obj.get_id())
                self.audit_function(ecf, ecf.id, ecf.id, emp_id,
                                    JVModifyStatus.UPDATE, JVRefType.JournalEntry)
                JVQueue.objects.using(self._current_app_schema()).create(ref_id=ecf.id, ref_type=JVRefType.JournalEntry, from_user_id=emp_id,
                                        to_user_id=emp_id,
                                        created_date=now(),
                                        comments="Rejected",
                                        is_sys=True,
                                        entity_id=self._entity_id()
                                        )
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                return success_obj
            else:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_REJECT_ID)
                error_obj.set_description("No_Rights_To_Reject")
                return error_obj

        except Exception as e:
            traceback.print_exc(True)
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            error_obj.set_description(str(e))
            return error_obj


    def status_UpdateApproved(self, request,ecf_obj, emp_id):
        try:
            ecf = JournalEntry.objects.using(self._current_app_schema()).get(id=ecf_obj.get_id())
            creatby = ecf.created_by
            if creatby != emp_id:
                print("jv",ecf)
                jvdata = JournalDetailEntry.objects.using(self._current_app_schema()).filter(jeentry_id=ecf_obj.get_id(),entity_id=self._entity_id(),status=1)
                print("jvfulldata",jvdata)
                entry = []
                for i in jvdata:
                    from utilityservice.service import api_service
                    api_serv = api_service.ApiService(self._scope())
                    emp1 = api_serv.get_empbranch_id(request, i.jedbranch)
                    branchcode = emp1['code']
                    print("branchcode",branchcode)
                    jvtoentry ={
                        "branch_id": i.jedbranch,
                        "fiscalyear": "2021",
                        "period": "1",
                        "module": 3,
                        "screen": 2,
                        "valuedate": "1",
                        "valuetime": "11:12",
                        "cbsdate": now(),
                        "localcurrency": "1",
                        "localexchangerate": "12",
                        "currency": "1",
                        "exchangerate": "10",
                        "isprevyrentry": "1",
                        "reversalentry": "2",
                        "refno": "CTOOO9087",
                        "crno": ecf.jecrno,
                        "refid": "JV",
                        "reftableid": "1",
                        "type": i.jedtype,
                        "gl": i.jedglno,
                        "apcatno": 1,
                        "apsubcatno": "1234",
                        "wisefinmap": "12",
                        "glremarks": i.jeddescription,
                        "amount": i.jedamount,
                        "fcamount": "13",
                        "ackrefno": "123",
                        "entry_status": 1,
                        "vendor_type": "default",
                        "branch_code": branchcode
                      }

                    entry.append(jvtoentry)
                print("entry",entry)
                from utilityservice.service import api_service
                api_serv = api_service.ApiService(self._scope())
                entry_module = api_serv.get_entryapi(request,emp_id,entry)
                print("entrymodule",entry_module.__dict__)
                i = entry_module.__dict__
                if i.get('status')=='success':
                    oracle = {
                        "AP_Type": "JV_PAYMENT",
                        "CR_Number": ecf.jecrno
                    }
                else:
                    error_obj = NWisefinError()
                    error_obj.set_code("API Call in EntryModule")
                    error_obj.set_description("Failed in EntryModule")
                    return error_obj
                entry_orcle_obj = OracleRequest(oracle)
                oracle_api = api_serv.get_entryoracleapi(entry_orcle_obj,emp_id)
                print("oracle",oracle_api)
                if oracle_api.get('Message')=='SUCCESS':
                    Ecfhdr = JournalEntry.objects.using(self._current_app_schema()).filter(id=ecf_obj.get_id(),entity_id=self._entity_id()).update(
                                                                        jestatus=JournalStatus.APPROVED,
                                                                        jedescription = ecf_obj.get_jedescription(),
                                                                        updated_by=emp_id,
                                                                        updated_date=now())
                    ecf = JournalEntry.objects.using(self._current_app_schema()).get(id=ecf_obj.get_id())
                    self.audit_function(ecf, ecf.id, ecf.id, emp_id,
                                        JVModifyStatus.UPDATE, JVRefType.JournalEntry)
                    JVQueue.objects.using(self._current_app_schema()).create(ref_id=ecf.id, ref_type=JVRefType.JournalEntry, from_user_id=emp_id,
                                            to_user_id=emp_id,
                                            created_date=now(),
                                            comments="Approved",
                                            is_sys=True,
                                            entity_id=self._entity_id()
                                            )
                    success_obj = NWisefinSuccess()
                    success_obj.set_status(SuccessStatus.SUCCESS)
                    return success_obj
                else:
                    error_obj = NWisefinError()
                    error_obj.set_code("API Call in OracleModule")
                    error_obj.set_description("Failed in Oracle")
                    return error_obj
            else:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_APPROVER_ID)
                error_obj.set_description(ErrorDescription.No_Rights_To_Approve)
                return error_obj

        except Exception as e:
            traceback.print_exc(True)
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            error_obj.set_description(str(e))
            return error_obj


    def search_jvrefno(self, request,jerefno):
        try:
            condition = Q(jecrno__icontains=jerefno) & Q(status=1) & Q(jestatus=2)
            jentry = JournalEntry.objects.using(self._current_app_schema()).filter(condition).order_by('created_date')
            if jentry:
                print(jentry)
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                # success_obj.set_message(SuccessMessage.APPROVED_MESSAGE)
                return success_obj
            else:
                traceback.print_exc(True)
                error_obj = NWisefinError()
                error_obj.set_code("Invalid JVCRNO")
                error_obj.set_description("Please give approved JVCRNO")
                return error_obj
        except Exception as e:
            traceback.print_exc(True)
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            error_obj.set_description(str(e))
            return error_obj


    def upload(self,document_json,header_id,emp_id):
        arrdoc = []
        for doc_json in document_json:
            dtpcdocument = JVFiles.objects.using(self._current_app_schema()).create(
                jvfile_id=header_id,
                file_id=doc_json['id'],
                file_name=doc_json['file_name'],
                # gen_file_name=doc_json['gen_file_name'],
                created_by=emp_id,entity_id=self._entity_id()
            )
        arrdoc.append(dtpcdocument)
        print("save")


    def Delete_jvfiles(self,request, file_id, emp_id):
        try:
            Ecfhdr = JVFiles.objects.using(self._current_app_schema()).filter(file_id=file_id,entity_id=self._entity_id()).update(
                                                                      status=0,
                                                                      updated_by=emp_id,
                                                                      updated_date=now())
            ecf = JVFiles.objects.using(self._current_app_schema()).get(file_id=file_id)
            self.audit_function(ecf, ecf.id, ecf.id, emp_id,
                                JVModifyStatus.UPDATE, JVRefType.JVFiles)
            JVQueue.objects.using(self._current_app_schema()).create(ref_id=ecf.id, ref_type=JVRefType.JVFiles, from_user_id=emp_id,
                                    to_user_id=emp_id,
                                    created_date=now(),
                                    comments="DELETE",
                                    is_sys=True,
                                    entity_id=self._entity_id()
                                    )
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            # success_obj.set_message(SuccessMessage.APPROVED_MESSAGE)
            return success_obj

        except Exception as ex:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            error_obj.set_description(str(ex))
            return error_obj
