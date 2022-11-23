import traceback

import django


from django.db import IntegrityError

from faservice.data.response.faauditresponse import FaAuditResponse
from faservice.models import FaAudit
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinerror import NWisefinError as Error
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription,ErrorMessage
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage




from datetime import datetime

from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread

now = datetime.now()




class FaAuditService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.FA_SERVICE)

    def create_audit(self, audit_obj):
        try:
            audit_var = FaAudit.objects.create( ref_id=audit_obj.ref_id,
                                ref_type=audit_obj.ref_type,
                                data=audit_obj.data,
                                user_id=audit_obj.user_id,
                                date=now,
                                req_status=audit_obj.req_status,
                                rel_refid=audit_obj.rel_refid,
                                rel_reftype=audit_obj.rel_reftype,
                                action=audit_obj.action)


        except IntegrityError as error:
            logger.info('FAL_AUDIT_EXCEPT:{}'.format(traceback.print_exc()))
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_DATA)
            return error_obj
        except:
            logger.info('FAL_AUDIT_EXCEPT:{}'.format(traceback.print_exc()))
            error_obj = Error()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            return error_obj

        audit_data = FaAuditResponse()
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
        auditlist = FaAudit.objects.all()
        list_length = len(auditlist)
        print(list_length)
        if list_length <= 0:
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_AUDIT_ID)
            error_obj.set_description(ErrorDescription.INVALID_AUDIT_ID)
            return error_obj
        else:
            audit_list_data = NWisefinList()
            for auditobj in auditlist:
                audit_data = FaAuditResponse()
                audit_data.set_id(auditobj.id)

                audit_list_data.append(audit_data)
            return audit_list_data

    def fetch_audit(self, audit_id,user_id):
        try:
            audit_var = FaAudit.objects.get(id=audit_id)
            audit_data = FaAuditResponse()
            audit_data.set_id(audit_var.id)

            return audit_data
        except FaAudit.DoesNotExist:
            logger.info('FAL_AUDIT_EXCEPT:{}'.format(traceback.print_exc()))
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_AUDIT_ID)
            error_obj.set_description(ErrorDescription.INVALID_AUDIT_ID)
            return error_obj

    def delete_audit(self, audit_id,user_id):
        audit = FaAudit.objects.filter(id=audit_id).delete()
        if audit[0] == 0:
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_AUDIT_ID)
            error_obj.set_description(ErrorDescription.INVALID_AUDIT_ID)
            return error_obj
        else:
            success_obj = Success()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

