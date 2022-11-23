import django
from django.db import IntegrityError
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage,ErrorDescription
from pprservice.models.pprmodel import PPRaudit
from pprservice.data.response.pprauditresponse import PprAuditResponse
from datetime import datetime
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread

now = datetime.now()
now=str(now)

class PPRAuditService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.PPR_SERVICE)


    def create_audit(self, audit_obj):
        try:
            audit_var = PPRaudit.objects.using(self._current_app_schema()).create(ref_type=audit_obj.ref_type,
                                                   data=audit_obj.data,
                                                   emp_id=audit_obj.user_id,entity_id=self._entity_id(),
                                                   date=now,
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

        audit_data = PprAuditResponse()
        audit_data.set_reftype(audit_var.ref_type)
        audit_data.set_data(audit_var.data)
        audit_data.set_date(audit_var.date)
        audit_data.set_action(audit_var.action)
        return audit_data



