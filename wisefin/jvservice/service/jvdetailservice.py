import traceback
#test
from jvservice.data.response.jvauditresponse import JVAuditResponse
from jvservice.data.response.jvdetailresponse import JVDetailEntryresponse
from jvservice.models import JVQueue, JournalDetailEntry
from jvservice.service.jvauditservice import JVAuditService
from jvservice.util.jvutil import JVRefType, JVModifyStatus
from django.utils.timezone import now

from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus
from utilityservice.service.utilityservice import NWisefinUtilityService
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread

utilityservice=NWisefinUtilityService()
class JVDetailService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.JV_SERVICE)

    def jvdetailentrycreate(self,request,jve_obj,jve_id,emp_id):
        jvdentry = JournalDetailEntry.objects.using(self._current_app_schema()).create(
                                                                                    jeentry_id=jve_id,
                                                                                    jedtype=jve_obj.get_jedtype(),
                                                                                    jeddescription=jve_obj.get_jeddescription(),
                                                                                    jedamount=jve_obj.get_jedamount(),
                                                                                    jedcat_code=jve_obj.get_jedcat_code(),
                                                                                    jedsubcat_code=jve_obj.get_jedsubcat_code(),
                                                                                    jedglno=jve_obj.get_jedglno(),
                                                                                    jedcc_code=jve_obj.get_jedcc_code(),
                                                                                    jedbs_code=jve_obj.get_jedbs_code(),
                                                                                    jedbranch = jve_obj.get_jedbranch(),
                                                                                    created_by=emp_id,
                                                                                    entity_id=self._entity_id())
        self.audit_function(jvdentry, jvdentry.id, jvdentry.id, emp_id,
                            JVModifyStatus.CREATE, JVRefType.JournalDetailEntry)
        JVQueue.objects.using(self._current_app_schema()).create(ref_id=jvdentry.id, ref_type=JVRefType.JournalDetailEntry,
                                                                  from_user_id=emp_id, to_user_id=emp_id,
                                                                  created_date=now(),
                                                                  comments="PENDING  FOR APPROVAL",
                                                                  is_sys=True,
                                                                  entity_id=self._entity_id()
                                                                  )
        jve_data = JVDetailEntryresponse()
        jve_data.set_id(jvdentry.id)
        jve_data.set_jeentry_id(jvdentry.jeentry_id)
        jve_data.set_jedtype(jvdentry.jedtype)
        jve_data.set_jeddescription(jvdentry.jeddescription)
        jve_data.set_jedamount(jvdentry.jedamount)
        jve_data.set_jedcat_code(jvdentry.jedcat_code)
        jve_data.set_jedsubcat_code(jvdentry.jedsubcat_code)
        jve_data.set_jedglno(jvdentry.jedglno)
        jve_data.set_jedcc_code(jvdentry.jedcc_code)
        jve_data.set_jedbs_code(jvdentry.jedbs_code)
        jve_data.set_jedbranch(jvdentry.jedbranch)
        return jve_data

    def Delete_jvdentry(self,request, jv_id, emp_id):
        try:
            jvdentry = JournalDetailEntry.objects.using(self._current_app_schema()).filter(id=jv_id,entity_id=self._entity_id()).update(
                                                                      status=0,
                                                                      updated_by=emp_id,
                                                                      updated_date=now())
            jvdentry = JournalDetailEntry.objects.using(self._current_app_schema()).get(id=jv_id)
            self.audit_function(jvdentry, jvdentry.id, jvdentry.id, emp_id,
                                JVModifyStatus.UPDATE, JVRefType.JournalDetailEntry)
            JVQueue.objects.using(self._current_app_schema()).create(ref_id=jvdentry.id, ref_type=JVRefType.JournalDetailEntry, from_user_id=emp_id,
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
        audit_obj.set_reftype(JVRefType.JournalDetailEntry)
        audit_obj.set_relrefid(relrefid)
        audit_obj.set_relreftype(JVRefType.JournalDetailEntry)
        audit_obj.set_userid(emp_id)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)


    def jv_queuedetails(self,request,ecfhdr_id):
        try:
            from utilityservice.service import api_service
            ecf_que=JVQueue.objects.using(self._current_app_schema()).filter(ref_id=ecfhdr_id,entity_id=self._entity_id())
            vysfin_list = NWisefinList()
            stop_count=len(ecf_que)
            if len(ecf_que) > 0:
                for ecfque in ecf_que:
                    # if  stop_count > 2:
                    #     stop_count=stop_count-1
                    #     continue
                    api_serv = api_service.ApiService(self._scope())
                    ecfque_json=dict()
                    ecfque_json['from_user'] = api_serv.get_empsingle_id(request,ecfque.from_user_id)
                    ecfque_json['to_user'] = api_serv.get_empsingle_id(request,ecfque.to_user_id)
                    ecfque_json['status'] = ecfque.comments
                    ecfque_json['remarks'] = ecfque.remarks
                    ecfque_json['created_date'] = str(ecfque.created_date.date())
                    vysfin_list.append(ecfque_json)
            return vysfin_list
        except Exception as e:
            traceback.print_exc(True)
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
            error_obj.set_description(str(e))
            return error_obj

