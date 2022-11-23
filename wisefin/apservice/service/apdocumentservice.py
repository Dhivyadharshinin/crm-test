import sys
import traceback

from apservice.data.response.apauditresponse import APAuditResponse
from apservice.models import APFiles
from apservice.service.apauditservice import APAuditService
from apservice.util.aputil import APRefType, APModifyStatus
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from django.utils.timezone import now


class APDocumentService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.AP_SERVICE)

    def apdocumentcreate(self, request, file_json, apinvhdr_id, emp_id):
        apinvhdr_update = apfiles=APFiles.objects.using(self._current_app_schema()).create(
                                file_id = file_json['id'],
                                gen_filename = file_json.get('gen_file_name'),
                                filename = file_json['file_name'],
                                ref_id = apinvhdr_id,
                                ref_type = APRefType.APINVOICEHEADER,
                                created_by = emp_id,
                                entity_id=self._entity_id())

    def delete_apfile(self,file_id, emp_id):
        try:
            ap_files = APFiles.objects.using(self._current_app_schema()).filter(file_id=file_id,entity_id=self._entity_id()).update(
                                                                      is_delete=1,
                                                                      updated_by=emp_id,
                                                                      updated_date=now())

            ap_files = APFiles.objects.using(self._current_app_schema()).get(file_id=file_id)

            self.audit_function(ap_files, ap_files.id, ap_files.id, emp_id,
                                APModifyStatus.DELETE, APRefType.AP_File)
            if ap_files == 0:
                success_obj = NWisefinSuccess()
                success_obj.set_status("Failed")
                success_obj.set_message('INVALID FILE ID')
                return success_obj
            else:
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
                return success_obj

        except APFiles.DoesNotExist:
            success_obj = NWisefinSuccess()
            success_obj.set_status("Failed")
            success_obj.set_message('INVALID AP FILE ID')
            return success_obj
        except Exception as excep:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            traceback.print_exc()
            success_obj = NWisefinSuccess()
            success_obj.set_status("Failed")
            success_obj.set_message(str(excep) + " - " + str(filename) + ", line_no: " + str(line_number) + str(
                ', exception_type : {c} '.format(c=type(excep).__name__)))
            return success_obj


    def audit_function(self, audit_data, refid, relrefid, emp_id, action, reqstatus):
        if action == APModifyStatus.DELETE:
            data = None
        else:
            data = audit_data.__dict__
            del data['_state']
        audit_service = APAuditService(self._scope())
        audit_obj = APAuditResponse()
        audit_obj.set_refid(refid)
        audit_obj.set_reqstatus(reqstatus)
        audit_obj.set_reftype(APRefType.AP_File)
        audit_obj.set_relrefid(relrefid)
        audit_obj.set_relreftype(APRefType.AP_File)
        audit_obj.set_userid(emp_id)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)



