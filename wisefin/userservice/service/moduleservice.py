import traceback

from django.db import IntegrityError

from nwisefin.settings import logger
from userservice.models import Module
from userservice.data.response.moduleresponse import ModuleResponse
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinsuccess import SuccessStatus,SuccessMessage,NWisefinSuccess
from django.utils import timezone
from utilityservice.data.response.nwisefinlist import NWisefinList
# from django.core.cache import cache
from django.db.models import Q
from userservice.controller import cachecontroller
from utilityservice.permissions.util.dbutil import Status
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace


class ModuleService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.USER_SERVICE)

    def create_module(self, module_obj,user_id):
        if not module_obj.get_id() is None:
            try:
                logger.error('MODULE: Module Update Started')
                module = Module.objects.using(self._current_app_schema()).filter(id=module_obj.get_id(), entity_id=self._entity_id()).update(name =module_obj.get_name(),
                logo = module_obj.get_logo(),url =module_obj.get_url(),refid = module_obj.get_refid(),
                updated_by=user_id,updated_date=timezone.now())

                module = Module.objects.using(self._current_app_schema()).get(id=module_obj.get_id(), entity_id=self._entity_id())

                # module catche update
                module_id = module_obj.get_id()
                module_catche_key = "module_moduleid_" + str(module_id)
                cachecontroller.update_cache(module_catche_key,module)
                logger.error('MODULE: Module Update Success' + str(module))
            except IntegrityError as error:
                logger.info('ERROR_Module_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except Module.DoesNotExist:
                logger.info('ERROR_Module_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_MODULE_ID)
                error_obj.set_description(ErrorDescription.INVALID_MODULE_ID)
                return error_obj
            except:
                logger.info('ERROR_Module_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                logger.error('MODULE: Module Creation Started')
                module = Module.objects.using(self._current_app_schema()).create(name =module_obj.get_name(),
                logo  =module_obj.get_logo(),url =module_obj.get_url(),refid_id = module_obj.get_refid(),
                created_by=user_id, entity_id=self._entity_id())
                logger.error('MODULE: Module Creation Success' + str(module))
            except IntegrityError as error:
                logger.error('ERROR_Module_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                logger.error('ERROR_Module_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj

        module_data = ModuleResponse()
        module_data.set_id(module.id)
        module_data.set_name(module.name)
        module_data.set_logo(module.logo)
        module_data.set_url(module.url)
        module_data.set_refid(module.refid_id)
        return module_data

    def fetch_module_list(self):
        # condition = Q (status=Status.create )& Q(refid_id =None)
        modulelist = Module.objects.using(self._current_app_schema()).filter(status=Status.create, entity_id=self._entity_id())
        list_length = len(modulelist)
        if list_length <= 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_MODULE_ID)
            error_obj.set_description(ErrorDescription.INVALID_MODULE_ID)
            return error_obj
        else:
            module_list_data = NWisefinList()
            submodule =[]
            for module in modulelist:
                module_data = ModuleResponse()
                module_data.set_id(module.id)
                module_data.set_name(module.name)
                module_data.set_logo(module.logo)
                module_data.set_url(module.url)
                if module.refid_id is None:
                    module_data.submodule = []
                    module_list_data.append(module_data)
                else:
                    module_data.set_refid(module.refid_id)
                    submodule.append(module_data)

            for mod in module_list_data.data:
                for sub in submodule :
                    if sub.refid  == mod.id  :
                        del sub.refid
                        mod.submodule.append(sub)





            return module_list_data

    def fetch_module(self, module_id):
        try:
            module_cache_key = "module_moduleid_" + str(module_id)
            module_obj = cachecontroller.get_cache(module_cache_key)

            if module_obj == None:
                module_obj = Module.objects.using(self._current_app_schema()).get(Q(id=module_id)&Q(status=Status.create)&Q(entity_id=self._entity_id()))
                cachecontroller.set_cache(module_cache_key, module_obj)

            # module = Module.objects.get(id=module_id)
            module_data = ModuleResponse()
            module_data.set_id(module_obj.id)
            module_data.set_name(module_obj.name)
            module_data.set_logo(module_obj.logo)
            module_data.set_url(module_obj.url)
            module_data.set_refid(module_obj.refid_id)
            return module_data

        except Module.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_MODULE_ID)
            error_obj.set_description(ErrorDescription.INVALID_MODULE_ID)
            return error_obj

    def delete_module(self, module_id):
        module = Module.objects.using(self._current_app_schema()).filter(Q(id=module_id) & Q(issys=False) & Q(entity_id=self._entity_id())).update(status=Status.delete)
        # module catche update
        # module_catche = "module_moduleid_" + str(module_id)
        # if module_catche in cache:
        #     cache.delete(module_catche)

        if module == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_MODULE_ID)
            error_obj.set_description(ErrorDescription.INVALID_MODULE_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

    def module_isactive(self,module_id):
        try:
            module_obj = Module.objects.using(self._current_app_schema()).get(id=module_id, entity_id=self._entity_id())
            if module_obj.status == Status.create :
                active = True
            else :
                active = False
            return active
        except:
            active = False
            return active

    def fetch_submodule(self, module_id):
        try:
            module_obj = Module.objects.using(self._current_app_schema()).filter(refid_id=module_id, entity_id=self._entity_id())
            module_arr=NWisefinList()
            for obj in module_obj :
                module_data = ModuleResponse()
                module_data.set_id(obj.id)
                module_data.set_name(obj.name)
                module_data.set_logo(obj.logo)
                module_data.set_url(obj.url)
                module_arr.append(module_data)
            return module_arr

        except Module.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_MODULE_ID)
            error_obj.set_description(ErrorDescription.INVALID_MODULE_ID)
            return error_obj


    def get_module_id(self,module_id):
        module_obj = Module.objects.using(self._current_app_schema()).filter(id__in=module_id)
        arr = []
        for obj in module_obj:
            module_data = ModuleResponse()
            module_data.set_id(obj.id)
            module_data.set_name(obj.name)
            arr.append(module_data)
        return arr

    def get_single_module(self,module_id):
        module_obj = Module.objects.using(self._current_app_schema()).filter(id=module_id)
        if len(module_obj) !=0:
            module_data = ModuleResponse()
            module_data.set_id(module_obj[0].id)
            module_data.set_name(module_obj[0].name)
            return module_data

