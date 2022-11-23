import django
from django.db import IntegrityError
from masterservice.data.response.masterauditresponse import MasterAuditResponse
from utilityservice.data.response.nwisefinerror  import NWisefinError
from utilityservice.data.response.nwisefinsuccess  import NWisefinSuccess,SuccessMessage,SuccessStatus
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage,ErrorDescription
from utilityservice.data.response.nwisefinlist import NWisefinList
from masterservice.models.mastermodels import Masteraudit

from django.utils import timezone
from datetime import datetime

from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread

now = datetime.now()
now=str(now)


class MasterAuditService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_audit(self, audit_obj):
        try:
            audit_var = Masteraudit.objects.using(self._current_app_schema()).create(ref_id=audit_obj.ref_id,
                                                                                     ref_type=audit_obj.ref_type,
                                                                                     data=audit_obj.data,
                                                                                     user_id=audit_obj.user_id,
                                                                                     date=now,
                                                                                     req_status=audit_obj.req_status,
                                                                                     rel_refid=audit_obj.rel_refid,
                                                                                     rel_reftype=audit_obj.rel_reftype,
                                                                                     action=audit_obj.action,
                                                                                     entity_id=self._entity_id())

        except IntegrityError as error:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_DATA)
            return error_obj
        except:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            return error_obj

        audit_data = MasterAuditResponse()
        audit_data.set_id(audit_var.id)
        audit_data.set_refid(audit_var.ref_id)
        audit_data.set_reftype(audit_var.ref_type)
        audit_data.set_data(audit_var.data)
        audit_data.set_date(audit_var.date)
        audit_data.set_reqstatus(audit_var.req_status)
        audit_data.set_relrefid(audit_var.rel_refid)
        audit_data.set_relreftype(audit_var.rel_reftype)
        audit_data.set_action(audit_var.action)
        return audit_data

    def fetch_vendoraudit_list(self, user_id):
        auditlist = Masteraudit.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id())
        list_length = len(auditlist)
        if list_length <= 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_VENDORAUDIT_ID)
            error_obj.set_description(ErrorDescription.INVALID_VENDORAUDIT_ID)
            return error_obj
        else:
            audit_list_data = NWisefinList()
            for auditobj in auditlist:
                audit_data = MasterAuditResponse()
                audit_data.set_id(auditobj.id)
                audit_data.set_refid(auditobj.ref_id)
                audit_data.set_reftype(auditobj.ref_type)
                audit_data.set_data(auditobj.data)
                audit_data.set_date(auditobj.date)
                audit_data.set_reqstatus(auditobj.req_status)
                audit_data.set_relrefid(auditobj.rel_refid)
                audit_data.set_relreftype(auditobj.rel_reftype)
                audit_data.set_action(auditobj.action)
                audit_list_data.append(audit_data)
            return audit_list_data

    def fetch_vendoraudit(self, vendoraudit_id, user_id):
        try:
            auditobj = Masteraudit.objects.using(self._current_app_schema()).get(id=vendoraudit_id,
                                                                                 entity_id=self._entity_id())
            audit_data = MasterAuditResponse()
            audit_data.set_id(auditobj.id)
            audit_data.set_refid(auditobj.ref_id)
            audit_data.set_reftype(auditobj.ref_type)
            audit_data.set_data(auditobj.data)
            audit_data.set_date(auditobj.date)
            audit_data.set_reqstatus(auditobj.req_status)
            audit_data.set_relrefid(auditobj.rel_refid)
            audit_data.set_relreftype(auditobj.rel_reftype)
            audit_data.set_action(auditobj.action)

            return audit_data
        except Masteraudit.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_VENDORAUDIT_ID)
            error_obj.set_description(ErrorDescription.INVALID_VENDORAUDIT_ID)
            return error_obj

    def delete_vendoraudit(self, vendoraudit_id, user_id):
        audit = Masteraudit.objects.using(self._current_app_schema()).filter(id=vendoraudit_id,
                                                                             entity_id=self._entity_id()).delete()
        if audit[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_VENDORAUDIT_ID)
            error_obj.set_description(ErrorDescription.INVALID_VENDORAUDIT_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj