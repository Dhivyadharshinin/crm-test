import sys
import traceback

from apservice.data.response.apauditresponse import APAuditResponse
from apservice.models import APFiles
from apservice.service.apauditservice import APAuditService
from apservice.util.aputil import APRefType, APModifyStatus
from ecfservice.models import ECFFiles
from ecfservice.util.ecfutil import ECFRefType
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from django.utils.timezone import now


class ECFDocumentService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.ECF_SERVICE)

    def ecfdocumentcreate(self, request, file_json, apinvhdr_id, emp_id):
        ecfinvhdr_update = apfiles=ECFFiles.objects.using(self._current_app_schema()).create(
                                file_id = file_json['id'],
                                file_name = file_json['file_name'],
                                ecffile_id = apinvhdr_id,
                                created_by = emp_id,
                                entity_id=self._entity_id())