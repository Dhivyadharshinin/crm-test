import traceback
from django.db.models import Q

from masterservice.models import Uom
from masterservice.data.response.uomresponse import UomResponse
from django.db import IntegrityError

from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessMessage, SuccessStatus
from utilityservice.data.response.nwisefinlist import NWisefinList
from django.utils import timezone
from masterservice.data.request.masterauditrequest import MasterAuditRequest
from masterservice.service.masterauditservice import MasterAuditService
from masterservice.data.response.masterauditresponse import MasterAuditResponse
from masterservice.util.masterutil import ModifyStatus,MasterRefType,RequestStatusUtil

from masterservice.data.request.masterauditrequest import MasterAuditRequest
from masterservice.service.masterauditservice import MasterAuditService
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


class UomService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_uom(self, uom_obj, user_id):
        if not uom_obj.get_id() is None:
            try:
                logger.error('UOM: Uom Update Started')
                uom_update = Uom.objects.using(self._current_app_schema()).filter(id=uom_obj.get_id()).update(
                    #code=uom_obj.get_code(),
                              name=uom_obj.get_name(),
                              updated_by=user_id,updated_date=timezone.now()

                )
                uom = Uom.objects.using(self._current_app_schema()).get(id=uom_obj.get_id())
                uom_auditdata = {'id': uom_obj.get_id(),
                                   #'code': uom_obj.get_code(),
                                   'name': uom_obj.get_name(),
                                   'updated_date': timezone.now(),
                                   'updated_by': user_id}
                self.audit_function(uom_auditdata, user_id, uom.id, ModifyStatus.update)
                logger.error('UOM: Uom Update Success' + str(uom_update))

            except IntegrityError as error:
                logger.error('ERROR_Uom_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except Uom.DoesNotExist:
                logger.error('ERROR_Uom_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_UOM_ID)
                error_obj.set_description(ErrorDescription.INVALID_UOM_ID)
                return error_obj
            except:
                logger.error('ERROR_Uom_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                logger.error('UOM: Uom Creation Started')
                data_len = Uom.objects.using(self._current_app_schema()).filter(
                    name=uom_obj.get_name()).values()
                if (len(data_len) > 0):
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVALID_DATA)
                    error_obj.set_description(ErrorDescription.DUPLICATE_NAME)
                    return error_obj

                uom = Uom.objects.using(self._current_app_schema()).create(
                    # code=uom_obj.get_code(),
                    name=uom_obj.get_name(), created_by=user_id, entity_id=self._entity_id())
                # max_cat_code = Uom.objects.filter(code__icontains='ISCT').order_by('-code')[0].code
                # rnsl = int(max_cat_code[3:])
                # new_rnsl = rnsl + 1
                # code = "ISCT" + str(new_rnsl).zfill(5)
                try:
                    max_cat_code = Uom.objects.using(self._current_app_schema()).filter(code__icontains='U').order_by('-code')[0].code
                    rnsl = int(max_cat_code[3:])
                except:
                    rnsl = 0
                new_rnsl = rnsl + 1
                code = "U" + str(new_rnsl).zfill(3)
                uom.code = code
                uom.save()
                self.audit_function(uom, user_id, uom.id, ModifyStatus.create)
                logger.error('UOM: Uom Creation Success' + str(uom))

            except IntegrityError as error:
                logger.error('ERROR_Uom_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                logger.error('ERROR_Uom_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        uom_data = UomResponse()
        uom_data.set_id(uom.id)
        uom_data.set_code(uom.code)
        uom_data.set_name(uom.name)

        # return uom_data
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        return success_obj

    def fetch_uom_list(self, vys_page):
        try:
            uomList = Uom.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).order_by(
                'created_date')[
                      vys_page.get_offset():vys_page.get_query_limit()]
            list_length = len(uomList)
            if list_length <= 0:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_UOM_ID)
                error_obj.set_description(ErrorDescription.INVALID_UOM_ID)
                return error_obj
            else:
                uom_list_data = NWisefinList()
                for uom in uomList:
                    uom_data = UomResponse()
                    uom_data.set_id(uom.id)
                    uom_data.set_code(uom.code)
                    uom_data.set_name(uom.name)
                    uom_list_data.append(uom_data)
                    vpage = NWisefinPaginator(uomList, vys_page.get_index(), 10)
                    uom_list_data.set_pagination(vpage)
                return uom_list_data
        except:
            logger.error('ERROR_UOM_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_UOM_ID)
            error_obj.set_description(ErrorDescription.INVALID_UOM_ID)
            return error_obj


    def fetch_uom(self, uom_id, user_id):
        try:
            uom = Uom.objects.using(self._current_app_schema()).get(id=uom_id, entity_id=self._entity_id())
            uom_data = UomResponse()
            uom_data.set_id(uom.id)
            uom_data.set_code(uom.code)
            uom_data.set_name(uom.name)
            return uom_data
        except Uom.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_UOM_ID)
            error_obj.set_description(ErrorDescription.INVALID_UOM_ID)
            return error_obj

    def delete_uom(self, uom_id, user_id):
        uom = Uom.objects.using(self._current_app_schema()).filter(id=uom_id, entity_id=self._entity_id()).delete()
        self.audit_function(uom, user_id, uom_id, ModifyStatus.delete)

        if uom[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_UOM_ID)
            error_obj.set_description(ErrorDescription.INVALID_UOM_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

    def audit_function(self, data_obj, user_id, id, action):
        if action == ModifyStatus.delete:
            data = None
        elif action == ModifyStatus.update:
            data = data_obj
        else:
            data = data_obj.__dict__
            del data['_state']
        audit_service = MasterAuditService(self._scope())  # changed
        audit_obj = MasterAuditResponse()
        audit_obj.set_refid(-1)
        audit_obj.set_reftype(MasterRefType.MASTER)
        audit_obj.set_userid(user_id)
        audit_obj.set_reqstatus(RequestStatusUtil.ONBOARD)
        audit_obj.set_relrefid(id)
        audit_obj.set_relreftype(MasterRefType.UOM)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)
        return

    def fetch_uom_search(self, vys_page, query):
        conditions = Q(status=1) & Q(entity_id=self._entity_id())
        if query:
            conditions &= Q(name__icontains=query)
        uomList = Uom.objects.using(self._current_app_schema()).filter(conditions).order_by('created_date')[
                  vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(uomList)
        uom_list_data = NWisefinList()
        if list_length > 0:
            for uom in uomList:
                uom_data = UomResponse()
                uom_data.set_id(uom.id)
                uom_data.set_code(uom.code)
                uom_data.set_name(uom.name)
                uom_list_data.append(uom_data)
                vpage = NWisefinPaginator(uomList, vys_page.get_index(), 10)
                uom_list_data.set_pagination(vpage)
        return uom_list_data

    def create_uom_mtom(self, uom_obj,action, user_id):
        if action=='update':
            try:
                uom_update = Uom.objects.using(self._current_app_schema()).filter(code=uom_obj.get_code()).update(
                             status=uom_obj.get_status(),
                              name=uom_obj.get_name(),
                              updated_by=user_id,updated_date=timezone.now()

                )
                uom = Uom.objects.using(self._current_app_schema()).get(code=uom_obj.get_code())
                uom_auditdata = {'id': uom.id,
                                   #'code': uom_obj.get_code(),
                                   'name': uom_obj.get_name(),
                                   'updated_date': timezone.now(),
                                   'updated_by': user_id}
                self.audit_function(uom_auditdata, user_id, uom.id, ModifyStatus.update)

            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except Uom.DoesNotExist:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_UOM_ID)
                error_obj.set_description(ErrorDescription.INVALID_UOM_ID)
                return error_obj
            except:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        elif action=='create':
            try:

                uom = Uom.objects.using(self._current_app_schema()).create(
                    name=uom_obj.get_name(),
                    code =uom_obj.get_code() , created_by=user_id, entity_id=self._entity_id())

                self.audit_function(uom, user_id, uom.id, ModifyStatus.create)

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
        uom_data = UomResponse()
        uom_data.set_id(uom.id)
        uom_data.set_code(uom.code)
        uom_data.set_name(uom.name)

        return uom_data


    def fetch_uomdata(self, uom_id):
        logger.error("catelog_id : " + str(uom_id))
        try:
            catelog = Uom.objects.using(self._current_app_schema()).get(id=uom_id,entity_id=1)
            catelog_data = {"id": catelog.id, "name": catelog.name}
            return catelog_data
        except Uom.DoesNotExist as e:
            print(e)
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(e) + ' : ' + str(uom_id))
            return error_obj

    def fetch_uom_download(self, vys_page):
        try:
            uomList = Uom.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).order_by('created_date')
            list_length = len(uomList)
            if list_length <= 0:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_UOM_ID)
                error_obj.set_description(ErrorDescription.INVALID_UOM_ID)
                return error_obj
            else:
                uom_list_data = NWisefinList()
                for uom in uomList:
                    uom_data = UomResponse()
                    uom_data.set_id(uom.id)
                    uom_data.set_code(uom.code)
                    uom_data.set_name(uom.name)
                    uom_list_data.append(uom_data)
                return uom_list_data
        except:
            logger.error('ERROR_UOM_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_UOM_ID)
            error_obj.set_description(ErrorDescription.INVALID_UOM_ID)
            return error_obj
