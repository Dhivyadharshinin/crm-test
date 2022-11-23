import traceback
import django
from django.db import IntegrityError
from nwisefin.settings import logger
from userservice.models import Role
from userservice.data.response.roleresponse import RoleResponse
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinsuccess import SuccessStatus,SuccessMessage,NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from datetime import datetime
from django.db.models import Q
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from userservice.controller import cachecontroller
from utilityservice.permissions.util.dbutil import Status
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace


class RoleService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.USER_SERVICE)

    def create_role(self, role_obj, user_id):
        if not role_obj.get_id() is None:
            try:
                logger.error('ROLE: Role Update Started')
                role_update = Role.objects.using(self._current_app_schema()).filter(id=role_obj.get_id(), entity_id=self._entity_id()).update(
                                code=role_obj.get_code(),
                                name=role_obj.get_name(),
                                updated_date=datetime.now(),
                                updated_by=user_id)

                role = Role.objects.using(self._current_app_schema()).get(id=role_obj.get_id(), entity_id=self._entity_id())

                # employee catche update
                role_id = role_obj.get_id()
                role_cache_key = "role_roleid_" + str(role_id)
                cachecontroller.update_cache(role_cache_key,role)
                logger.error('ROLE: Role Update Success' + str(role_update))
            except IntegrityError as error:
                logger.info('ERROR_Role_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except Role.DoesNotExist:
                logger.info('ERROR_Role_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_ROLE_ID)
                error_obj.set_description(ErrorDescription.INVALID_ROLE_ID)
                return error_obj
            except:
                logger.info('ERROR_Role_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            # try:
                logger.error('ROLE: Role Creation Started')
                print(self._entity_id())
                role = Role.objects.using(self._current_app_schema()).create(code=role_obj.get_code(),
                                                     name=role_obj.get_name(),
                                                     operation_name=role_obj.get_name(),
                                                     created_by=user_id, entity_id=self._entity_id())
                logger.error('ROLE: Role Creation Success' + str(role))
            # except IntegrityError as error:
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.INVALID_DATA)
            #     error_obj.set_description(ErrorDescription.INVALID_DATA)
            #     return error_obj
            # except:
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            #     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            #     return error_obj

        role_data = RoleResponse()
        role_data.set_id(role.id)
        role_data.set_code(role.code)
        role_data.set_name(role.name)
        return role_data

    def fetch_role_list(self):
        rolelist = Role.objects.using(self._current_app_schema()).filter(status=Status.create, entity_id=self._entity_id()).order_by('created_date')
        list_length = len(rolelist)
        if list_length <= 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_ROLE_ID)
            error_obj.set_description(ErrorDescription.INVALID_ROLE_ID)
            return error_obj
        else:
            role_list_data = NWisefinList()
            for roleobj in rolelist:
                role_data = RoleResponse()
                role_data.set_id(roleobj.id)
                role_data.set_code(roleobj.code)
                role_data.set_name(roleobj.name)
                role_list_data.append(role_data)
            return role_list_data

    def fetch_role(self, role_id):
        try:
            role_cache_key = "role_roleid_" + str(role_id)
            role_obj=cachecontroller.get_cache(role_cache_key)
            if role_obj == None :
                role_obj = Role.objects.using(self._current_app_schema()).get(Q(id=role_id)&Q(status=Status.create)&Q(entity_id=self._entity_id()))
                cachecontroller.set_cache(role_cache_key,role_obj)

            # role_obj = Role.objects.get(id=role_id)
            role_data = RoleResponse()
            role_data.set_id(role_obj.id)
            role_data.set_code(role_obj.code)
            role_data.set_name(role_obj.name)
            return role_data
        except Role.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_ROLE_ID)
            error_obj.set_description(ErrorDescription.INVALID_ROLE_ID)
            return error_obj

    def delete_role(self, role_id):
        role = Role.objects.using(self._current_app_schema()).filter(Q(id=role_id)&Q(issys=False)&Q(entity_id=self._entity_id())).update(status=Status.delete)
        # employee catche delete
        # role_catche = "role_roleid_" + str(role_id)
        # if role_catche in cache:
        #     cache.delete(role_catche)

        if role == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_ROLE_ID)
            error_obj.set_description(ErrorDescription.INVALID_ROLE_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

    def get_role_name(self,role_arr):
        condition = None
        for i in role_arr:
            if condition is None:
                condition = Q(id__exact=i)&Q(entity_id=self._entity_id())
            else:
                condition |= Q(id__exact=i)&Q(entity_id=self._entity_id())
        role = Role.objects.using(self._current_app_schema()).values_list('operation_name', flat=True).filter(condition)
        arr = []
        for i in role:
            arr.append(i)
        return arr

    def role_isactive(self,role_id):
        try:
            role_obj = Role.objects.using(self._current_app_schema()).get(id=role_id, entity_id=self._entity_id())
            if role_obj.status == Status.create :
                active = True
            else :
                active = False
            return active
        except:
            active = False
            return active
