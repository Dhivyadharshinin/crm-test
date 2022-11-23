import django
from django.db import IntegrityError

from inwardservice.data.response.inwardauditresponse import InwardAuditResponse
from inwardservice.models import InwardAudit
from datetime import datetime

from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread

now = datetime.now()


class InwardAuditService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.INWARD_SERVICE)
    def create_audit(self, audit_obj):
        try:
            audit_var = InwardAudit.objects.using(self._current_app_schema()).create( ref_id=audit_obj.ref_id,
                                ref_type=audit_obj.ref_type,
                                data=audit_obj.data,
                                user_id=audit_obj.user_id,
                                date=now,
                                req_status=audit_obj.req_status,
                                rel_refid=audit_obj.rel_refid,
                                rel_reftype=audit_obj.rel_reftype,
                                action=audit_obj.action)

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

        audit_data = InwardAuditResponse()
        audit_data.set_id(audit_var.id)
        audit_data.set_refid(audit_var.ref_id)
        audit_data.set_reftype(audit_var.ref_type)
        audit_data.set_data(audit_var.data)
        audit_data.set_userid(audit_var.user_id)
        audit_data.set_date(audit_var.date)
        audit_data.set_relrefid(audit_var.rel_refid)
        audit_data.set_reqstatus(audit_var.req_status)
        audit_data.set_relrefid(audit_var.rel_refid)
        audit_data.set_relreftype(audit_var.rel_reftype)
        audit_data.set_action(audit_var.action)
        return audit_data

    def fetch_audit_list(self,user_id):
        auditlist = InwardAudit.objects.using(self._current_app_schema()).all()
        list_length = len(auditlist)
        print(list_length)
        if list_length <= 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_AUDIT_ID)
            error_obj.set_description(ErrorDescription.INVALID_AUDIT_ID)
            return error_obj
        else:
            audit_list_data = NWisefinList()
            for auditobj in auditlist:
                audit_data = InwardAuditResponse()
                audit_data.set_id(auditobj.id)
                audit_list_data.append(audit_data)
            return audit_list_data

    def fetch_audit(self, audit_id,user_id):
        try:
            audit_var = InwardAudit.objects.using(self._current_app_schema()).get(id=audit_id)
            audit_data = InwardAuditResponse()
            audit_data.set_id(audit_var.id)
            return audit_data
        except InwardAudit.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_AUDIT_ID)
            error_obj.set_description(ErrorDescription.INVALID_AUDIT_ID)
            return error_obj

    def delete_audit(self, audit_id,user_id):
        audit = InwardAudit.objects.using(self._current_app_schema()).filter(id=audit_id).delete()
        if audit[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_AUDIT_ID)
            error_obj.set_description(ErrorDescription.INVALID_AUDIT_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj
