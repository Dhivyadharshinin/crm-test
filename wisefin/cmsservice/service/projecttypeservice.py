from django.db.models.query_utils import Q
from django.utils.timezone import now
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from cmsservice.service.codegenhistoryservice import Codegenservice
from cmsservice.util.cmsutil import ActiveStatus, CodePrefix
from cmsservice.models import ProjectType,AgreementType
from cmsservice.data.response.projecttyperesponse import ProjectTypeResponse


class ProjectTypeService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.CMS_SERVICE)

    def create_projecttype(self, data_obj, emp_id, scope):
        condition = Q(name__exact=data_obj.get_name()) & Q(status=ActiveStatus.Active)
        projectty = ProjectType.objects.using(self._current_app_schema()).filter(condition)
        if len(projectty) > 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.DUPLICATE_NAME)
            return error_obj
        if not data_obj.get_id() is None:
            project_var = ProjectType.objects.using(self._current_app_schema()).filter(id=data_obj.get_id()).update(
                                                   name=data_obj.get_name(),
                                                   updated_by=emp_id,
                                                   updated_date=now())
            projectty = ProjectType.objects.using(self._current_app_schema()).get(id=data_obj.get_id())

        else:
            table_type = CodePrefix.ProjectType
            codegen_service = Codegenservice(scope)
            code = codegen_service.codegen(table_type, emp_id)
            projectty = ProjectType.objects.using(self._current_app_schema()).create(
                                                    code=code,
                                                    name=data_obj.get_name(),
                                                    created_by=emp_id)
        projectty_data = ProjectTypeResponse()
        projectty_data.set_id(projectty.id)
        projectty_data.set_name(projectty.name)
        return projectty_data

    def delete_projecttype(self, projectty_id, emp_id):
        projectty = ProjectType.objects.using(self._current_app_schema()).filter(id=projectty_id).update(
                                        status=ActiveStatus.Delete,
                                        updated_by=emp_id,
                                        updated_date=now())
        if projectty[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_PROJECTTYPE_ID)
            error_obj.set_description(ErrorDescription.INVALID_PROJECTTYPE_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

    def fetch_projecttype(self, projectty_id):
        try:
            projectty = ProjectType.objects.using(self._current_app_schema()).get(id=projectty_id)
            projectty_data = ProjectTypeResponse()
            projectty_data.set_id(projectty.id)
            projectty_data.set_name(projectty.name)
            projectty_data.set_code(projectty.code)
            return projectty_data
        except:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_PROJECTTYPE_ID)
            error_obj.set_description(ErrorDescription.INVALID_PROJECTTYPE_ID)
            return error_obj

    def get_projecttype_info(self, type_arr):
            projectty_obj = ProjectType.objects.using(self._current_app_schema()).filter(id__in=type_arr)
            arr=[]
            for i in projectty_obj:
                projectty_data = ProjectTypeResponse()
                projectty_data.set_id(i.id)
                projectty_data.set_name(i.name)
                projectty_data.set_code(i.code)
                arr.append(projectty_data)
            return arr

    def fetch_projecttype_list(self, vys_page, query):
        condition = None
        if query is not None:
            condition = Q(name__icontains=query) | Q(code__icontains=query) & Q(status=ActiveStatus.Active)
        if condition is not None:
            doctypeList = ProjectType.objects.using(self._current_app_schema()).filter(condition).values('id', 'name', 'code')[
                           vys_page.get_offset():vys_page.get_query_limit()]
        else:
            doctypeList = ProjectType.objects.using(self._current_app_schema()).all().values('id', 'name', 'code')[
                           vys_page.get_offset():vys_page.get_query_limit()]
        vlist = NWisefinList()
        for doc in doctypeList:
            doctype_res = ProjectTypeResponse()
            doctype_res.set_id(doc['id'])
            doctype_res.set_name(doc['name'])
            doctype_res.set_code(doc['code'])
            vlist.append(doctype_res)
        vpage = NWisefinPaginator(doctypeList, vys_page.get_index(), 10)
        vlist.set_pagination(vpage)
        return vlist

class AgreementtypeService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.CMS_SERVICE)
    def create_agreement(self,data_obj,emp_id,scope):
        if not data_obj.get_id() is None:
            agreementtype =AgreementType.objects.using(self._current_app_schema()).filter(id=data_obj.get_id()).update(
                                                   name=data_obj.get_name(),
                                                   updated_by=emp_id,
                                                   updated_date=now())
            success_obj = NWisefinSuccess()
            success_obj.set_status("Success")
            success_obj.set_message("Updated Successfully")
            return success_obj

        else:
            table_type = CodePrefix.AgreementType
            codegen_service = Codegenservice(scope)
            code = codegen_service.codegen(table_type, emp_id)
            agreementtype1 = AgreementType.objects.using(self._current_app_schema()).create(code=code,
                                                                                            name=data_obj.get_name(),
                                                                                            created_by=emp_id)
        agreementtype_data = ProjectTypeResponse()
        agreementtype_data.set_id(agreementtype1.id)
        agreementtype_data.set_name(agreementtype1.name)
        return agreementtype_data
    def agreementtypeall(self):
        agreementtype_obj = AgreementType.objects.using(self._current_app_schema()).all()
        arr = []
        for i in agreementtype_obj:
            agreement_data = ProjectTypeResponse()
            agreement_data.set_id(i.id)
            agreement_data.set_name(i.name)
            agreement_data.set_code(i.code)
            arr.append(agreement_data.get())
        return arr
    def get_agreementype(self,agreementtype_id):
        agreementtypee = AgreementType.objects.using(self._current_app_schema()).get(id=agreementtype_id)
        projectt_data = ProjectTypeResponse()
        projectt_data.set_id(agreementtypee.id)
        projectt_data.set_name(agreementtypee.name)
        projectt_data.set_code(agreementtypee.code)
        return projectt_data
    def delete_agreementtype(self,agreementtype_id):
        agreementtypee1 = AgreementType.objects.using(self._current_app_schema()).filter(id=agreementtype_id).update(status=ActiveStatus.Delete)
        success_obj = NWisefinSuccess()
        success_obj.set_status("Success")
        success_obj.set_message("Deleted Successfully")
        return success_obj
