import traceback
from django.db import IntegrityError
from django.db.models import Q
from masterservice.util.masterutil import ModifyStatus
from nwisefin.settings import logger
from userservice.data.response.entityresponse import EntityResponse
from configservice.models.configmodels import Entity
from django.utils import timezone
import json
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinuser import NWisefinUser
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from userservice.models.usermodels import Employee, EmployeeEntityMapping
from userservice.data.response.entityresponse import EntityResponse
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from django.contrib.auth import authenticate
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.service.applicationconstants import ApplicationNamespace
# costcentre
from utilityservice.service.threadlocal import NWisefinThread


class EntityService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.USER_SERVICE)
    def create_entity(self, entity_obj, user_id):
        if not entity_obj.get_id() is None:
            try:
                logger.error('ENTITY: Entity Update Started')
                entity = Entity.objects.using(self._current_app_schema()).filter(id=entity_obj.get_id()).update(
                    name=entity_obj.get_name(),
                    namespace=entity_obj.get_namespace(),
                    # updated_by=user_id,
                    # updated_date=timezone.now()
                )
                entity = Entity.objects.get(id=entity_obj.get_id())
                logger.error('ENTITY: Entity Update Success' + str(entity))
            except IntegrityError as error:
                logger.info('ERROR_Entity_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except Entity.DoesNotExist:
                logger.info('ERROR_Entity_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_ENTITY_ID)
                error_obj.set_description(ErrorDescription.INVALID_ENTITY_ID)
                return error_obj
            except:
                logger.info('ERROR_Entity_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                logger.error('ENTITY: Entity Creation Started')
                entity = Entity.objects.using(self._current_app_schema()).create(
                    name=entity_obj.get_name(),
                    namespace=entity_obj.get_namespace(),
                    # created_by=user_id
                )
                logger.error('ENTITY: Entity Creation Success' + str(entity))
            except IntegrityError as error:
                logger.error('ERROR_Entity_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                logger.error('ERROR_Entity_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        # data_obj = EntityResponse()
        # data_obj.set_id(entity.id)
        # data_obj.set_name(entity.name)
        # data_obj.set_namespace(entity.namespace)
        # data_obj.set_status(entity.name)
        # return data_obj
        data = NWisefinSuccess()
        data.set_status(SuccessStatus.SUCCESS)
        data.set_message(SuccessMessage.CREATE_MESSAGE)
        return data

    def fetch_entity_list(self, request, vys_page):
        condition = Q()
        if "data" in request.GET:
            condition &= Q(name__icontains=request.GET.get("data"))
        entityList = Entity.objects.using(self._current_app_schema()).filter(condition)[
                     vys_page.get_offset():vys_page.get_query_limit()]
        # print(entityList)
        list_length = len(entityList)
        entity_list_data = NWisefinList()
        if list_length <= 0:
            return entity_list_data
        else:
            for entity in entityList:
                data_obj = EntityResponse()
                data_obj.set_id(entity.id)
                data_obj.set_name(entity.name)
                data_obj.set_namespace(entity.namespace)
                data_obj.set_status(entity.status)
                entity_list_data.append(data_obj)
            vpage = NWisefinPaginator(entityList, vys_page.get_index(), 10)
            entity_list_data.set_pagination(vpage)
        return entity_list_data

    def entity_activate_inactivate(self, request, ent_obj):

        if (int(ent_obj.status) == 0):

            entity_data = Entity.objects.using(self._current_app_schema()).filter(id=ent_obj.id).update(
                status=1)
        else:
            entity_data = Entity.objects.using(self._current_app_schema()).filter(id=ent_obj.id).update(
                status=0)
        entity_var = Entity.objects.using(self._current_app_schema()).get(id=ent_obj.id)
        data = EntityResponse()
        data.set_status(entity_var.status)
        status = entity_var.status
        # print(status)
        data.set_id(entity_var.id)
        # return data
        if status == 1:
            data = NWisefinSuccess()
            data.set_status(SuccessStatus.SUCCESS)
            data.set_message(SuccessMessage.INACTIVATED)
            return data
        else:
            data = NWisefinSuccess()
            data.set_status(SuccessStatus.SUCCESS)
            data.set_message(SuccessMessage.ACTIVATED)
            return data
