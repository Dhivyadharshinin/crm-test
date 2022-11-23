import traceback
from nwisefin.settings import logger

from django.db import IntegrityError
from userservice.data.response.hierarchyresponse import HierarchyResponse
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinlist import NWisefinList
from userservice.models import EmployeeHierarchy
from django.utils import timezone
import json
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


class HierarchyService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.USER_SERVICE)
    def create_hierarchy(self, hierarchy_obj, user_id):
        if not hierarchy_obj.get_id() is None:
            try:
                logger.error('EMPLOYEEHIERARCHY: EmployeeHierarchy Update Started')
                hierarchy = EmployeeHierarchy.objects.using(self._current_app_schema()).filter(id=hierarchy_obj.get_id()).update(layer=hierarchy_obj.get_layer(),
                                                                                 order=hierarchy_obj.get_order(),
                                                                                 remarks=hierarchy_obj.get_remarks(),
                                                                                 flag=hierarchy_obj.get_flag(),
                                                                                 updated_by=user_id,
                                                                                 updated_date=timezone.now())
                hierarchy = EmployeeHierarchy.objects.using(self._current_app_schema()).get(id=hierarchy_obj.get_id())
                logger.error('EMPLOYEEHIERARCHY: EmployeeHierarchy Update Success' + str(hierarchy))
            except IntegrityError as error:
                logger.info('ERROR_EmployeeHierarchy_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except EmployeeHierarchy.DoesNotExist:
                logger.info('ERROR_EmployeeHierarchy_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_hierarchy_ID)
                error_obj.set_description(ErrorDescription.INVALID_hierarchy_ID)
                return error_obj
            except:
                logger.info('ERROR_EmployeeHierarchy_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                logger.error('EMPLOYEEHIERARCHY: EmployeeHierarchy Creation Started')
                hierarchy = EmployeeHierarchy.objects.using(self._current_app_schema()).create(layer=hierarchy_obj.get_layer(),
                                                                                 order=hierarchy_obj.get_order(),
                                                                                 remarks=hierarchy_obj.get_remarks(),
                                                                                 flag=hierarchy_obj.get_flag(),
                                                                                 created_by=user_id
                                                                                 )
                logger.error('EMPLOYEEHIERARCHY: EmployeeHierarchy Creation Success' + str(hierarchy))
            except IntegrityError as error:
                logger.error('ERROR_EmployeeHierarchy_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                logger.error('ERROR_EmployeeHierarchy_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        data_obj = HierarchyResponse()
        data_obj.set_id(hierarchy.id)
        data_obj.set_layer(hierarchy.layer)
        data_obj.set_order(hierarchy.order)
        data_obj.set_remarks(hierarchy.remarks)
        data_obj.set_flag(hierarchy.flag)
        return data_obj


    def fetch_hierarchy(self, hierarchy_id):
        try:
            hierarchy = EmployeeHierarchy.objects.using(self._current_app_schema()).get(id=hierarchy_id)
            data_obj = HierarchyResponse()
            data_obj.set_id(hierarchy.id)
            data_obj.set_layer(hierarchy.layer)
            data_obj.set_order(hierarchy.order)
            data_obj.set_remarks(hierarchy.remarks)
            data_obj.set_flag(hierarchy.flag)
            return data_obj
        except EmployeeHierarchy.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_hierarchy_ID)
            error_obj.set_description(ErrorDescription.INVALID_hierarchy_ID)
            return error_obj
    def fetch_hierarchy_list(self,vys_page,data):
        hierarchyList = EmployeeHierarchy.objects.using(self._current_app_schema()).filter(layer__icontains= data)[
                         vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(hierarchyList)
        hierarchy_list_data = NWisefinList()
        if list_length <= 0:
            pass
        else:
            for hierarchy in hierarchyList:
                data_obj = HierarchyResponse()
                data_obj.set_id(hierarchy.id)
                data_obj.set_layer(hierarchy.layer)
                data_obj.set_order(hierarchy.order)
                data_obj.set_remarks(hierarchy.remarks)
                data_obj.set_flag(hierarchy.flag)
                hierarchy_list_data.append(data_obj)
                vpage = NWisefinPaginator(hierarchyList, vys_page.get_index(), 10)
                hierarchy_list_data.set_pagination(vpage)
        return hierarchy_list_data

    def delete_hierarchy(self, hierarchy_id):
        hierarchy = EmployeeHierarchy.objects.using(self._current_app_schema()).filter(id=hierarchy_id).delete()
        if hierarchy[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_HIERARCHY_ID)
            error_obj.set_description(ErrorDescription.INVALID_HIERARCHY_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj
