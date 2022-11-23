from django.db import IntegrityError
from django.db.models import Q
from django.utils.timezone import now

from masterservice.models import DocumentType
from masterservice.data.response.documenttyperesponse import DocumenttypeResponse
from masterservice.util.masterutil import ModifyStatus
from utilityservice.data.response.nwisefinerror  import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage,ErrorDescription
from utilityservice.data.response.nwisefinsuccess  import NWisefinSuccess,SuccessMessage,SuccessStatus
from utilityservice.data.response.nwisefinlist import NWisefinList
from django.utils import timezone
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


class DocumenttypeService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_documenttype(self, Doc_obj, user_id):
        condition = Q(name__exact=Doc_obj.get_name()) & Q(entity_id=self._entity_id())
        doctype = DocumentType.objects.using(self._current_app_schema()).filter(condition)
        if len(doctype) > 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.DUPLICATE_NAME)
            return error_obj
        if not Doc_obj.get_id() is None:
            try:
                Doctype = DocumentType.objects.using(self._current_app_schema()).filter(id=Doc_obj.get_id(),
                                                                                        entity_id=self._entity_id()).update(
                    # code=Doc_obj.get_code(),
                    name=Doc_obj.get_name(),
                    updated_by=user_id,
                    updated_date=timezone.now())
                Doctype = DocumentType.objects.using(self._current_app_schema()).get(id=Doc_obj.get_id(),
                                                                                     entity_id=self._entity_id())
            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except DocumentType.DoesNotExist:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DocumentType_ID)
                error_obj.set_description(ErrorDescription.INVALID_DocumentType_ID)
                return error_obj
            except:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                Doctype = DocumentType.objects.using(self._current_app_schema()).create(  # code=Doc_obj.get_code(),
                    name=Doc_obj.get_name(),
                    created_by=user_id, entity_id=self._entity_id())

                try:
                    max_cat_code = DocumentType.objects.using(self._current_app_schema()).filter(code__icontains='DOC').order_by('-code')[0].code
                    rnsl = int(max_cat_code[3:])
                except:
                    rnsl = 0
                new_rnsl = rnsl + 1
                code = "DOC" + str(new_rnsl).zfill(3)
                Doctype.code = code
                Doctype.save()
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
        DocumentType_data = DocumenttypeResponse()
        DocumentType_data.set_id(Doctype.id)
        DocumentType_data.set_code(Doctype.code)
        DocumentType_data.set_name(Doctype.name)
        DocumentType_data.set_status(Doctype.status)
        DocumentType_data.set_created_by(Doctype.created_by)
        DocumentType_data.set_updated_by(Doctype.updated_by)
        return DocumentType_data

    def fetchdoctype(self, doctype_id):
        try:
            Doctype = DocumentType.objects.using(self._current_app_schema()).get(id=doctype_id,
                                                                                 entity_id=self._entity_id())
            DocumentType_data = DocumenttypeResponse()
            DocumentType_data.set_id(Doctype.id)
            DocumentType_data.set_code(Doctype.code)
            DocumentType_data.set_name(Doctype.name)
            DocumentType_data.set_status(Doctype.status)
            DocumentType_data.set_created_by(Doctype.created_by)
            DocumentType_data.set_updated_by(Doctype.updated_by)
            return DocumentType_data
        except DocumentType.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DOCTYPE_ID)
            error_obj.set_description(ErrorDescription.INVALID_DOCTYPE_ID)
            return error_obj

    def fetch_doctype_list(self, vys_page, query):
        condition = Q(entity_id=self._entity_id())
        if query is None:
            condition &= Q(status__exact=1)
        else:
            condition &= Q(status__exact=1) & Q(name__icontains=query)

        DoctypeList = DocumentType.objects.using(self._current_app_schema()).filter(condition)[
                      vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(DoctypeList)
        cat_list_data = NWisefinList()
        if list_length <= 0:
            pass
        else:
            for Doctype in DoctypeList:
                DocumentType_data = DocumenttypeResponse()
                DocumentType_data.set_id(Doctype.id)
                DocumentType_data.set_code(Doctype.code)
                DocumentType_data.set_name(Doctype.name)
                DocumentType_data.set_status(Doctype.status)
                DocumentType_data.set_created_by(Doctype.created_by)
                DocumentType_data.set_updated_by(Doctype.updated_by)
                cat_list_data.append(DocumentType_data)
            vpage = NWisefinPaginator(DoctypeList, vys_page.get_index(), 10)
            cat_list_data.set_pagination(vpage)
        return cat_list_data

    def delete_doctype(self, doctype_id, user_id):
        Doctype = DocumentType.objects.using(self._current_app_schema()).filter(id=doctype_id,
                                                                                entity_id=self._entity_id()).update(
            status=ModifyStatus.delete,
            updated_by=user_id,
            updated_date=now())
        if Doctype == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DOCTYPE_ID)
            error_obj.set_description(ErrorDescription.INVALID_DOCTYPE_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

    def search_doctype(self, request, query, vys_page):
        condition = None
        if query is not None:
            condition = (Q(name__icontains=query) | Q(code__icontains=query)) & Q(entity_id=self._entity_id())
        doctypeList = None
        if condition is not None:
            doctypeList = DocumentType.objects.using(self._current_app_schema()).values('id', 'name', 'code').filter(
                condition)[
                          vys_page.get_offset():vys_page.get_query_limit()]
        else:
            doctypeList = DocumentType.objects.using(self._current_app_schema()).values('id', 'name', 'code').all()[
                          vys_page.get_offset():vys_page.get_query_limit()]
        vlist = NWisefinList()
        for doc in doctypeList:
            doctype_res = DocumenttypeResponse()
            disp_name = '(' + doc['code'] + ') ' + doc['name']
            doctype_res.set_name(disp_name)
            doctype_res.set_id(doc['id'])
            doctype_res.set_name(doc['name'])
            vlist.append(doctype_res)
        vpage = NWisefinPaginator(doctypeList, vys_page.get_index(), 10)
        vlist.set_pagination(vpage)
        return vlist


    def get_doctype(self, doc_data):
        docIdarr = doc_data.get('doctype_id')
        doctype = DocumentType.objects.using(self._current_app_schema()).filter(id__in=docIdarr).values('id', 'code',
                                                                                                        'name')
        doctype_list_data = NWisefinList()
        for i in doctype:
            data = {"id": i['id'],
                    "code": i['code'],
                    "name": i['name']}
            doctype_list_data.append(data)
        return doctype_list_data.get()


    def fetch_doctypedata(self, doctype_id):
        doctype = DocumentType.objects.using(self._current_app_schema()).get(id=doctype_id)
        doc_data = {"id": doctype.id, "code": doctype.code, "name": doctype.name}
        return doc_data

    def fetch_multi_doctypedata(self, doctype_arr):
        doctype = DocumentType.objects.using(self._current_app_schema()).filter(id__in=doctype_arr,status=ModifyStatus.create).values('id','code','name')
        doc_data = list(doctype)
        return doc_data

    def document_summarysearch(self, query, vys_page):
        if query is None:
            condition = Q(status=1)
        else:
            print(query)
            condition = Q(name__icontains=query["name"]) & Q(code__icontains=query["code"]) & Q(status=1)

        documentlist = DocumentType.objects.using(self._current_app_schema()).filter(condition).order_by('-created_date')[
                       vys_page.get_offset(): vys_page.get_query_limit()]
        list_length = len(documentlist)
        document_list_data = NWisefinList()
        if list_length > 0:
            for documentobj in documentlist:
                document_data = DocumenttypeResponse()
                document_data.set_id(documentobj.id)
                document_data.set_code(documentobj.code)
                document_data.set_name(documentobj.name)
                document_list_data.append(document_data)
            vpage = NWisefinPaginator(documentlist, vys_page.get_index(), 10)
            document_list_data.set_pagination(vpage)
        return document_list_data