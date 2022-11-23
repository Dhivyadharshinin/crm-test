import traceback

import django
from django.db import IntegrityError
from nwisefin.settings import logger
from userservice.models import RoleModule
from userservice.data.response.roleresponse import RoleModuleResponse
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinsuccess import SuccessStatus,SuccessMessage,NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from datetime import datetime
from userservice.controller import cachecontroller
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace


class RoleModuleService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.USER_SERVICE)

    def create_rolemodule(self, rolemodule_obj, user_id):
        if not rolemodule_obj.get_id() is None:
            try:
                logger.error('ROLEMODULE: RoleModule Update Started')
                rolemodule_update = RoleModule.objects.using(self._current_app_schema()).filter(id=rolemodule_obj.get_id(), entity_id=self._entity_id()).update(
                                role_id=rolemodule_obj.get_role_id(),
                                module_id=rolemodule_obj.get_module_id(),
                                updated_date=datetime.now(),
                                updated_by=user_id)

                rolemodule = RoleModule.objects.using(self._current_app_schema()).get(id=rolemodule_obj.get_id(), entity_id=self._entity_id())

                # rolemodule catche update
                role_id = rolemodule.role_id
                rolemodule_role_id_catche_key = "rolemodule_" + "roleid_" + str(role_id)
                cachecontroller.update_cache(rolemodule_role_id_catche_key, rolemodule)

                module_id = rolemodule.module_id
                rolemodule_module_id_catche_key = "rolemodule_" + "moduleid_" + str(module_id)
                cachecontroller.update_cache(rolemodule_module_id_catche_key, rolemodule)

                logger.error('ROLEMODULE: RoleModule Update Success' + str(rolemodule_update))

            except IntegrityError as error:
                logger.info('ERROR_RoleModule_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except RoleModule.DoesNotExist:
                logger.info('ERROR_RoleModule_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_MODULEROLE_ID)
                error_obj.set_description(ErrorDescription.INVALID_MODULEROLE_ID)
                return error_obj
            except:
                logger.info('ERROR_RoleModule_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                logger.error('ROLEMODULE: RoleModule Creation Started')
                rolemodule = RoleModule.objects.using(self._current_app_schema()).create(role_id=rolemodule_obj.get_role_id(),
                                                     module_id=rolemodule_obj.get_module_id(),
                                                     created_by=user_id, entity_id=self._entity_id())
                logger.error('ROLEMODULE: RoleModule Creation Success' + str(rolemodule))
            except IntegrityError as error:
                logger.error('ERROR_RoleModule_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                logger.error('ERROR_RoleModule_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj

        rolemodule_data = RoleModuleResponse()
        rolemodule_data.set_id(rolemodule.id)
        rolemodule_data.set_role_id(rolemodule.role_id)
        rolemodule_data.set_module_id(rolemodule.module_id)
        return rolemodule_data

    def fetch_rolemodule_list(self):
        rolemodulelist = RoleModule.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id())
        list_length = len(rolemodulelist)
        if list_length <= 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_MODULEROLE_ID)
            error_obj.set_description(ErrorDescription.INVALID_MODULEROLE_ID)
            return error_obj
        else:
            rolemodule_list_data = NWisefinList()
            for rolemoduleobj in rolemodulelist:
                rolemodule_data = RoleModuleResponse()
                rolemodule_data.set_id(rolemoduleobj.id)
                rolemodule_data.set_role_id(rolemoduleobj.role_id)
                rolemodule_data.set_module_id(rolemoduleobj.module_id)
                rolemodule_list_data.append(rolemodule_data)
            return rolemodule_list_data

    def fetch_role(self, module_id):
        try:
            role_cache_key = "rolemodule_" + "moduleid_" + str(module_id)
            role_obj = cachecontroller.get_cache(role_cache_key)
            if role_obj == None:
                role_obj = RoleModule.objects.using(self._current_app_schema()).values_list('role_id',flat=True).filter(module_id=module_id, entity_id=self._entity_id())
                cachecontroller.set_cache(role_cache_key, role_obj)
            return role_obj

        except RoleModule.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_MODULEROLE_ID)
            error_obj.set_description(ErrorDescription.INVALID_MODULEROLE_ID)
            return error_obj

    def delete_role(self, module_id):
        rolemodule = RoleModule.objects.using(self._current_app_schema()).filter(id=module_id, entity_id=self._entity_id()).delete()
        # rolemodule cache delete
        rolemodule_cache_key = "rolemodule_" + "moduleid_" + str(module_id)
        cachecontroller.delete_cache(rolemodule_cache_key)

        if rolemodule[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_MODULEROLE_ID)
            error_obj.set_description(ErrorDescription.INVALID_MODULEROLE_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj


    def fetch_module(self, role_id):
        try:
            role_cache_key = "rolemodule_" + "roleid_" + str(role_id)
            role_obj = cachecontroller.get_cache(role_cache_key)
            if role_obj == None:
                role_obj = RoleModule.objects.using(self._current_app_schema()).values_list('module_id', flat=True).filter(role_id=role_id, entity_id=self._entity_id())
                cachecontroller.set_cache(role_cache_key, role_obj)

            return role_obj
        except RoleModule.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_MODULEROLE_ID)
            error_obj.set_description(ErrorDescription.INVALID_MODULEROLE_ID)
            return error_obj

    def delete_module(self, role_id):
        rolemodule = RoleModule.objects.using(self._current_app_schema()).filter(id=role_id, entity_id=self._entity_id()).delete()
        # rolemodule cache delete
        rolemodule_cache_key = "rolemodule_" + "roleid_" + str(role_id)
        cachecontroller.delete_cache(rolemodule_cache_key)

        if rolemodule[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_MODULEROLE_ID)
            error_obj.set_description(ErrorDescription.INVALID_MODULEROLE_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj
