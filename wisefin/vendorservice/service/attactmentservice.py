import boto3
# from memoservice.models import Documents
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from vendorservice.models import VendorFileAttachment
from django.http import HttpResponse , StreamingHttpResponse
from django.conf import settings
from django.db.models import Q
from utilityservice.data.response.nwisefinsuccess import SuccessStatus,SuccessMessage,NWisefinSuccess
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace


class VendorAttactments(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.VENDOR_SERVICE)


    def vendor_delete(self, file_id):
        try:
            doc_obj = VendorFileAttachment.objects.using(self._current_app_schema()).filter(file_id=file_id,entity_id=self._entity_id()).update(status=0)
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            response = HttpResponse(success_obj.get(), content_type="application/json")
            return response
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj

    def get_fileid_using_id(self, file_id):
        doc_id = VendorFileAttachment.objects.using(self._current_app_schema()).get(id=file_id, entity_id=self._entity_id())
        return doc_id.file_id
