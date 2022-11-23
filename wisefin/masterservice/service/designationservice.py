import traceback

from django.db import IntegrityError

from masterservice.models import Designation
from masterservice.data.response.designationresponse import DesignationResponse
from masterservice.service.Codegenerator import CodeGen
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror  import NWisefinError
from utilityservice.data.response.nwisefinsuccess  import NWisefinSuccess,SuccessMessage,SuccessStatus
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage,ErrorDescription
from utilityservice.data.response.nwisefinlist import NWisefinList
from django.utils import timezone
from masterservice.data.request.masterauditrequest import MasterAuditRequest
from masterservice.service.masterauditservice import MasterAuditService
from masterservice.data.response.masterauditresponse import MasterAuditResponse
from masterservice.util.masterutil import ModifyStatus, MasterRefType, RequestStatusUtil, Code_Gen_Type, Code_Gen_Value, \
    MasterStatus
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


class DesignationService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_designation(self, designation_obj, user_id):
        if not designation_obj.get_id() is None:
            try:
                logger.error('DESIGNATION: Designation Update Started')
                designation_update = Designation.objects.using(self._current_app_schema()).filter(
                    id=designation_obj.get_id(), entity_id=self._entity_id()).update(
                    # code =designation_obj.get_code (),
                    name=designation_obj.get_name(),
                    updated_by=user_id, updated_date=timezone.now())

                designation = Designation.objects.using(self._current_app_schema()).get(id=designation_obj.get_id(),
                                                                                        entity_id=self._entity_id())
                logger.error('DESIGNATION: Designation Update Success' + str(designation_update))
                designation_auditdata = {'id': designation_obj.get_id(),
                                         # 'code': designation_obj.get_code(),
                                         'name': designation_obj.get_name(),
                                         'updated_date': timezone.now(),
                                         'updated_by': user_id}
                self.audit_function(designation_auditdata, user_id, designation.id, ModifyStatus.update)
            except IntegrityError as error:
                logger.error('ERROR_Designation_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except Designation.DoesNotExist:
                logger.error('ERROR_Designation_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_designation_ID)
                error_obj.set_description(ErrorDescription.INVALID_designation_ID)
                return error_obj
            except:
                logger.error('ERROR_Designation_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                logger.error('DESIGNATION: Designation Creation Started')
                data_len=Designation.objects.using(self._current_app_schema()).filter(name=designation_obj.get_name()).values()
                if(len(data_len)>0):
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVALID_DATA)
                    error_obj.set_description(ErrorDescription.DUPLICATE_NAME)
                    return error_obj
                designation = Designation.objects.using(self._current_app_schema()).create(
                    # code =designation_obj.get_code (),
                    name=designation_obj.get_name(),
                    created_by=user_id, entity_id=self._entity_id()
                )
                try:
                    max_cat_code = Designation.objects.using(self._current_app_schema()).filter(code__icontains='DES').order_by('-code')[0].code
                    rnsl = int(max_cat_code[3:])
                except:
                    rnsl = 0
                new_rnsl = rnsl + 1
                code = "DES" + str(new_rnsl).zfill(3)# code = "ISCT" + str(designation.id)
                designation.code = code
                designation.save()
                logger.error('DESIGNATION: Designation Creation Success' + str(designation))
                self.audit_function(designation, user_id, designation.id, ModifyStatus.create)

            except IntegrityError as error:
                logger.error('ERROR_Designation_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                logger.error('ERROR_Designation_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj

        designation_data = DesignationResponse()
        designation_data.set_id(designation.id)
        designation_data.set_code(designation.code)
        designation_data.set_name(designation.name)

        return designation_data

    def fetch_designation_list(self, user_id, vys_page):
        try:
            designationlist = Designation.objects.using(self._current_app_schema()).filter(
                entity_id=self._entity_id()).order_by('id')[
                              vys_page.get_offset():vys_page.get_query_limit()]
            list_length = len(designationlist)
            if list_length <= 0:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_designation_ID)
                error_obj.set_description(ErrorDescription.INVALID_designation_ID)
                return error_obj
            else:
                designation_list_data = NWisefinList()
                for designation in designationlist:
                    designation_data = DesignationResponse()
                    designation_data.set_id(designation.id)
                    designation_data.set_code(designation.code)
                    designation_data.set_name(designation.name)
                    designation_list_data.append(designation_data)
                    vpage = NWisefinPaginator(designationlist, vys_page.get_index(), 10)
                    designation_list_data.set_pagination(vpage)
                return designation_list_data
        except:
            logger.error('ERROR_Designation_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_designation_ID)
            error_obj.set_description(ErrorDescription.INVALID_designation_ID)
            return error_obj

    def fetch_designation_download(self, user_id):
        try:
            designationlist = Designation.objects.using(self._current_app_schema()).filter(
                entity_id=self._entity_id()).order_by('id')
            list_length = len(designationlist)
            if list_length <= 0:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_designation_ID)
                error_obj.set_description(ErrorDescription.INVALID_designation_ID)
                return error_obj
            else:
                designation_list_data = NWisefinList()
                for designation in designationlist:
                    designation_data = DesignationResponse()
                    designation_data.Code=(designation.code)
                    designation_data.Name=(designation.name)
                    status = MasterStatus()
                    if designation.status == status.Active:
                        designation_data.Status = status.Active_VALUE
                    if designation.status == status.Inactive:
                        designation_data.Status = status.Inactive_VALUE
                    designation_list_data.append(designation_data)

                return designation_list_data
        except:
            logger.error('ERROR_Designation_Excel_Download_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_designation_ID)
            error_obj.set_description(ErrorDescription.INVALID_designation_ID)
            return error_obj

    def fetch_designation(self, designation_id):
        try:
            designation = Designation.objects.using(self._current_app_schema()).get(id=designation_id,
                                                                                    entity_id=self._entity_id())
            designation_data = DesignationResponse()
            designation_data.set_id(designation.id)
            designation_data.set_code(designation.code)
            designation_data.set_name(designation.name)
            return designation_data

        except Designation.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_designation_ID)
            error_obj.set_description(ErrorDescription.INVALID_designation_ID)
            return error_obj

    def delete_designation(self, designation_id, user_id):
        designation = Designation.objects.using(self._current_app_schema()).filter(id=designation_id,
                                                                                   entity_id=self._entity_id()).delete()
        self.audit_function(designation, user_id, designation_id, ModifyStatus.delete)

        if designation[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_designation_ID)
            error_obj.set_description(ErrorDescription.INVALID_designation_ID)
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
        audit_obj.set_relreftype(MasterRefType.DESIGNATION)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)
        return

    def fetch_designation_search(self, query, vys_page):
        if query is None:
            designationlist = Designation.objects.using(self._current_app_schema()).filter(
                entity_id=self._entity_id()).order_by('created_date')[
                              vys_page.get_offset():vys_page.get_query_limit()]
        else:
            designationlist = Designation.objects.using(self._current_app_schema()).filter(name__icontains=query,
                                                                                           entity_id=self._entity_id()).order_by(
                'created_date')[
                              vys_page.get_offset():vys_page.get_query_limit()]
        designation_list_data = NWisefinList()
        for designation in designationlist:
            designation_data = DesignationResponse()
            designation_data.set_id(designation.id)
            designation_data.set_code(designation.code)
            designation_data.set_name(designation.name)
            designation_list_data.append(designation_data)
            vpage = NWisefinPaginator(designationlist, vys_page.get_index(), 10)
            designation_list_data.set_pagination(vpage)
        return designation_list_data

    def get_state_by_designation(self, name):
        try:
            designation = Designation.objects.using(self._current_app_schema()).get(name=name,
                                                                                    entity_id=self._entity_id())
            return designation.id
        except:
            designation = Designation.objects.using(self._current_app_schema()).create(name=name,
                                                                                       entity_id=self._entity_id())
            return designation.id

    def fetch_by_designation_code(self, name,Entity):
        try:
            designation = Designation.objects.using(self._current_app_schema()).get(name=name,
                                                                                    entity_id=Entity)
            return designation.id
        except:
            designation = Designation.objects.using(self._current_app_schema()).create(name=name,
                                                                                       entity_id=Entity)
            try:
                max_cat_code = Designation.objects.using(self._current_app_schema()).filter(code__icontains='DES').order_by('-code')[0].code
                rnsl = int(max_cat_code[3:])
            except:
                rnsl = 0
            new_rnsl = rnsl + 1
            code = "DES" + str(new_rnsl).zfill(3)
            designation.code = code
            designation.save()
            return designation.id


    def create_designation_mtom(self, designation_obj,action,user_id):
        if action=='update':
            try:
                designation_update = Designation.objects.using(self._current_app_schema()).filter(code =designation_obj.get_code()).update(code =designation_obj.get_code (),
                name  =designation_obj.get_name(),
                status  =designation_obj.get_status(),
                updated_by=user_id,updated_date=timezone.now())

                designation = Designation.objects.using(self._current_app_schema()).get(code =designation_obj.get_code())
                designation_auditdata = {'id': designation.id,
                                              'code': designation_obj.get_code(),
                                              'name': designation_obj.get_name(),
                                              'updated_date': timezone.now(),
                                              'updated_by': user_id}
                self.audit_function(designation_auditdata, user_id, designation.id, ModifyStatus.update)
            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except Designation.DoesNotExist:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_designation_ID)
                error_obj.set_description(ErrorDescription.INVALID_designation_ID)
                return error_obj
            except:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        elif action=='create':
            try:
                designation = Designation.objects.using(self._current_app_schema()).create(code =designation_obj.get_code(),
                name=designation_obj.get_name(),
                created_by=user_id)

                self.audit_function(designation, user_id, designation.id, ModifyStatus.create)

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

        designation_data = DesignationResponse()
        designation_data.set_id(designation.id)
        designation_data.set_code(designation.code)
        designation_data.set_name(designation.name)

        return designation_data
