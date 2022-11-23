from django.db.models import Q

from configservice.models import Application
from masterservice.data.request.appversionrequest import AppVersionRequest
from masterservice.models import AppVersion
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from wisefinapi.employeeapi import EmployeeAPI

class AppVersionService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)


    def AppVersion(self, request, user_id, vys_page):
        condition = Q(entity_id=self._entity_id())
        if 'no' in request.GET and request.GET.get('no') != '' or "":
            condition &= Q(no=request.GET.get('no'))
        if 'remarks' in request.GET and request.GET.get('remarks') != '' or "":
            condition &= Q(remarks__icontains=request.GET.get('remarks'))
        appversion = AppVersion.objects.using(self._current_app_schema()).filter(condition)[vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(appversion)
        appversion_list_data = NWisefinList()
        if list_length > 0:
            for i in appversion:
                app_data = AppVersionRequest()
                app_data.set_id(i.id)
                app_data.set_no(i.no)
                app_data.set_ref_no(i.ref_no)
                app_data.set_remarks(i.remarks)
                appversion_list_data.append(app_data)
                vpage = NWisefinPaginator(appversion, vys_page.get_index(), 10)
                appversion_list_data.set_pagination(vpage)
            return appversion_list_data
        else:
            return appversion_list_data


    def AppVersionData(self, app_obj, emp_id):
        if app_obj.get_no()  != None or '':
            try:
                appversion = AppVersion.objects.using(self._current_app_schema()).create(no=app_obj.get_no(),
                                                                                         ref_no=app_obj.get_ref_no(),
                                                                                         remarks=app_obj.get_remarks(),
                                                                                         status=1,
                                                                                         entity_id=self._entity_id(),
                                                                                         created_by=emp_id)

                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
                return success_obj
            except Exception as e:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(str(e))
                return error_obj
        else:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.INVALID_DATA)
            return error_obj

    def appversion_activate_inactivate(self,request,app_obj):
        if (int(app_obj.status) == 0):

            app_data = AppVersion.objects.using(self._current_app_schema()).filter(id=app_obj.id).update(
                status=1)
        else:
            app_data = AppVersion.objects.using(self._current_app_schema()).filter(id=app_obj.id).update(
                status=0)
        fin_var = AppVersion.objects.using(self._current_app_schema()).get(id=app_obj.id)
        data = AppVersionRequest()
        data.set_status(fin_var.status)
        status = fin_var.status
        data.set_id(fin_var.id)
        if status == 1:
            data = NWisefinSuccess()
            data.set_status(SuccessStatus.SUCCESS)
            data.set_message(SuccessMessage.ACTIVATED)
            return data
        else:
            data = NWisefinSuccess()
            data.set_status(SuccessStatus.SUCCESS)
            data.set_message(SuccessMessage.INACTIVATED)
            return data

# class CONFIGDBService(NWisefinThread):
#     def __init__(self, scope):
#         super().__init__(scope)
#         self._set_namespace(ApplicationNamespace.CONF_SERVICE)
#
#     def get_configuration_schema(self):
#         return self._current_app_schema()
#
#     def AppSchemaDropDown(self,request, scope):
#         conf_db = CONFIGDBService(scope)
#         conf_Dynamic_schema = conf_db.get_configuration_schema()
#         from nwisefin.settings import DATABASES
#         # DB_NAME_config = DATABASES.get(conf_Dynamic_schema).get("NAME")
#         appSchema = Application.objects.using(str(conf_Dynamic_schema)).all()
#         list_length = len(appSchema)
#         appversion_list_data = NWisefinList()
#         if list_length > 0:
#             for i in appSchema:
#                 app_data = AppVersionRequest()
#                 app_data.set_id(i.id)
#                 app_data.set_name(i.name)
#                 appversion_list_data.append(app_data)
#             return appversion_list_data
