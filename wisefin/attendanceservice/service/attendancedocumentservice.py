from datetime import datetime
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from attendanceservice.models.attendancemodels import AttendanceFileAttachments
from docservice.service.documentservice import DocumentsService
from attendanceservice.data.response.leaveresponse import AttendanceFileResponse
from docservice.util.docutil import DocModule
from attendanceservice.util.responsemessage import MessageResponse, StatusType
from utilityservice.data.response.nwisefinsuccess import SuccessMessage
from django.http import HttpResponse


class AttendanceDocumentService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.ATTENDANCE_SERVICE)

    def get_file_id_by_id(self, req_id):
        file_data = AttendanceFileAttachments.objects.using(self._current_app_schema()).filter(id=req_id)
        return file_data[0].file_id

    def create_attendance_document(self, resp_obj, tab_type, request, attachment=None):
        doc_service = DocumentsService(self._scope())
        params = dict()
        params['module'] = DocModule.ATD
        params['ref_id'] = resp_obj.id
        params['ref_type'] = tab_type

        if attachment is None:
            attachment = 'file'
            upload = doc_service.upload(request, params)
        else:
            upload = doc_service.multiple_upload(request, params, attachment)

        data_count = len(request.FILES.getlist(attachment))
        obj_list = []
        for i in range(0, data_count):
            data_obj = request.FILES.getlist(attachment)[i]
            name = data_obj.name
            file_id = upload.data[i].id
            file_name = upload.data[i].file_name
            file_name_new = str(datetime.now().strftime("%y%m%d_%H%M%S")) + name
            obj = AttendanceFileAttachments.objects.using(self._current_app_schema()).create(
                ref_id=resp_obj.id, tab_type=tab_type, gen_file_name=file_name_new,
                file_name=file_name, entity_id=self._entity_id(), file_id=file_id)
            obj_list.append(obj)
        return obj_list

    def attendance_delete(self, file_id):
        try:
            AttendanceFileAttachments.objects.using(self._current_app_schema()).filter(file_id=file_id,
                                                                                       entity_id=self._entity_id()
                                                                                       ).update(status=0)
            success_obj = MessageResponse()
            success_obj.set_status(StatusType.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            response = HttpResponse(success_obj.get(), content_type="application/json")
            return response
        except Exception as e:
            error_obj = MessageResponse()
            error_obj.set_status(StatusType.FAILED)
            error_obj.set_message(str(e))
            return error_obj

    def get_file_attachment(self, ref_id):
        file_list = AttendanceFileAttachments.objects.using(self._current_app_schema()).filter(ref_id=ref_id, status=1)
        list_data = []
        for file in file_list:
            resp = AttendanceFileResponse()
            resp.set_id(file.id)
            resp.set_file_name(file.file_name)
            list_data.append(resp)
        return list_data
