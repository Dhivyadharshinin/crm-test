from django.db.models import Q
from django.utils import timezone
from django.utils.timezone import now
from cmsservice.data.response.documenttyperesponse import DocumenttypeResponse
from cmsservice.models import DocumentType
from cmsservice.util.cmsutil import ActiveStatus, CodePrefix
from cmsservice.service.codegenhistoryservice import Codegenservice
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread

class DocumenttypeService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.CMS_SERVICE)

    def create_documenttype(self, Doc_obj, emp_id, scope):
        condition = Q(name__exact=Doc_obj.get_name()) & Q(status=ActiveStatus.Active)
        doctype = DocumentType.objects.using(self._current_app_schema()).filter(condition)
        if len(doctype) > 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.DUPLICATE_NAME)
            return error_obj
        if not Doc_obj.get_id() is None:
            Doctype = DocumentType.objects.using(self._current_app_schema()).filter(
                                                id=Doc_obj.get_id()).update(
                                                name=Doc_obj.get_name(),
                                                updated_by=emp_id,
                                                updated_date=timezone.now())
            Doctype = DocumentType.objects.using(self._current_app_schema()).get(id=Doc_obj.get_id())
        else:
            table_type = CodePrefix.DocumentType
            codegen_service = Codegenservice(scope)
            code = codegen_service.codegen(table_type, emp_id)
            Doctype = DocumentType.objects.using(self._current_app_schema()).create(
                                                name=Doc_obj.get_name(),
                                                code=code,
                                                created_by=emp_id)
            print("DoctypeId", Doctype.id)
        DocumentType_data = DocumenttypeResponse()
        DocumentType_data.set_id(Doctype.id)
        DocumentType_data.set_name(Doctype.name)
        return DocumentType_data

    def fetchdoctype(self, doctype_id):
        try:
            Doctype = DocumentType.objects.using(self._current_app_schema()).get(id=doctype_id)
            DocumentType_data = DocumenttypeResponse()
            DocumentType_data.set_id(Doctype.id)
            DocumentType_data.set_code(Doctype.code)
            DocumentType_data.set_name(Doctype.name)
            return DocumentType_data
        except DocumentType.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DOCUMENTTYPE_ID)
            error_obj.set_description(ErrorDescription.INVALID_DOCUMENTTYPE_ID)
            return error_obj

    def delete_doctype(self, doctype_id, emp_id):
        Doctype = DocumentType.objects.using(self._current_app_schema()).filter(id=doctype_id).update(status=ActiveStatus.Delete,
                                                                   updated_by=emp_id,
                                                                   updated_date=now())
        if Doctype == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DOCUMENTTYPE_ID)
            error_obj.set_description(ErrorDescription.INVALID_DOCUMENTTYPE_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

    def fetch_doctype_list(self, vys_page, query):
        condition = None
        if query is not None:
            condition = (Q(name__icontains=query) | Q(code__icontains=query)) & Q(status=ActiveStatus.Active)
        if condition is not None:
            doctypeList = DocumentType.objects.using(self._current_app_schema()).filter(condition).values('id', 'name', 'code')[
                           vys_page.get_offset():vys_page.get_query_limit()]
        else:
            doctypeList = DocumentType.objects.using(self._current_app_schema()).all().values('id', 'name', 'code')[
                           vys_page.get_offset():vys_page.get_query_limit()]
        vlist = NWisefinList()
        for doc in doctypeList:
            doctype_res = DocumenttypeResponse()
            doctype_res.set_id(doc['id'])
            doctype_res.set_name(doc['name'])
            vlist.append(doctype_res)
        vpage = NWisefinPaginator(doctypeList, vys_page.get_index(), 10)
        vlist.set_pagination(vpage)
        return vlist