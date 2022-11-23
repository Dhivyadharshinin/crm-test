from django.db import IntegrityError
from django.db.models import Q
from masterservice.models import CustomerCategory
from masterservice.data.response.customercategoryresponse import CustomerCategoryResponse
from masterservice.service.Codegenerator import CodeGen
from utilityservice.data.response.nwisefinerror  import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage,ErrorDescription
from utilityservice.data.response.nwisefinsuccess  import NWisefinSuccess,SuccessMessage,SuccessStatus
from utilityservice.data.response.nwisefinlist import NWisefinList
from django.utils import timezone
from masterservice.data.request.masterauditrequest import MasterAuditRequest
from masterservice.service.masterauditservice import MasterAuditService
from masterservice.data.response.masterauditresponse import MasterAuditResponse
from masterservice.util.masterutil import ModifyStatus, MasterRefType, RequestStatusUtil, Code_Gen_Value, Code_Gen_Type
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


class CustomerCategoryService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_customercategory(self, customercategory_obj, user_id):
        if not customercategory_obj.get_id() is None:
            try:
                customercategory_update = CustomerCategory.objects.using(self._current_app_schema()).filter(
                    id=customercategory_obj.get_id(), entity_id=self._entity_id()).update(
                    # code =customercategory_obj.get_code (),
                    name=customercategory_obj.get_name(),
                    updated_by=user_id, updated_date=timezone.now())

                customercategory = CustomerCategory.objects.using(self._current_app_schema()).get(
                    id=customercategory_obj.get_id(), entity_id=self._entity_id())

                customercategory_auditdata = {'id': customercategory_obj.get_id(),
                                              # 'code': customercategory_obj.get_code(),
                                              'name': customercategory_obj.get_name(),
                                              'updated_date': timezone.now(),
                                              'updated_by': user_id}
                self.audit_function(customercategory_auditdata, user_id, customercategory.id, ModifyStatus.update)

            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except CustomerCategory.DoesNotExist:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_customercategory_ID)
                error_obj.set_description(ErrorDescription.INVALID_customercategory_ID)
                return error_obj
            except:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                customercategory = CustomerCategory.objects.using(self._current_app_schema()).create(
                    # code =customercategory_obj.get_code (),
                    name=customercategory_obj.get_name(),
                    created_by=user_id, entity_id=self._entity_id())

                try:
                    max_cat_code = CustomerCategory.objects.using(self._current_app_schema()).filter(code__icontains='CUS').order_by('-code')[0].code
                    rnsl = int(max_cat_code[3:])
                except:
                    rnsl = 0
                new_rnsl = rnsl + 1
                code = "CUS" + str(new_rnsl).zfill(5)# code = "ISCT" + str(category_cust)
                customercategory.code = code
                customercategory.save()
                self.audit_function(customercategory, user_id, customercategory.id, ModifyStatus.create)

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

        customercategory_data = CustomerCategoryResponse()
        customercategory_data.set_id(customercategory.id)
        customercategory_data.set_code(customercategory.code)
        customercategory_data.set_name(customercategory.name)
        return customercategory_data

    def fetch_customercategory_list(self, vys_page):
        customercategorylist = CustomerCategory.objects.using(self._current_app_schema()).filter(
            entity_id=self._entity_id()).order_by('name')[vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(customercategorylist)
        if list_length >= 0:
            customercategory_list_data = NWisefinList()
            for customercategory in customercategorylist:
                customercategory_data = CustomerCategoryResponse()
                customercategory_data.set_id(customercategory.id)
                customercategory_data.set_code(customercategory.code)
                customercategory_data.set_name(customercategory.name)
                customercategory_list_data.append(customercategory_data)
            vpage = NWisefinPaginator(customercategorylist, vys_page.get_index(), 10)
            customercategory_list_data.set_pagination(vpage)
            return customercategory_list_data
        else:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_customercategory_ID)
            error_obj.set_description(ErrorDescription.INVALID_customercategory_ID)
            return error_obj

    def fetch_customercategory(self, customercategory_id, user_id):
        try:
            customercategory = CustomerCategory.objects.using(self._current_app_schema()).get(id=customercategory_id,
                                                                                              entity_id=self._entity_id())
            customercategory_data = CustomerCategoryResponse()
            customercategory_data.set_id(customercategory.id)
            customercategory_data.set_code(customercategory.code)
            customercategory_data.set_name(customercategory.name)
            return customercategory_data

        except CustomerCategory.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_customercategory_ID)
            error_obj.set_description(ErrorDescription.INVALID_customercategory_ID)
            return error_obj

    def delete_customercategory(self, customercategory_id, user_id):
        customercategory = CustomerCategory.objects.using(self._current_app_schema()).filter(id=customercategory_id,
                                                                                             entity_id=self._entity_id()).delete()
        self.audit_function(customercategory, user_id, customercategory_id, ModifyStatus.delete)
        if customercategory[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_customercategory_ID)
            error_obj.set_description(ErrorDescription.INVALID_customercategory_ID)
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
        audit_obj.set_relreftype(MasterRefType.CUSTOMERCATEGORY)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)
        return

    def fetch_customercategory_search(self, query, vys_page):
        condition = Q(status=1) & Q(entity_id=self._entity_id())

        if query:
            condition &= Q(name__icontains=query)

        # if query is None:
        customercategorylist = CustomerCategory.objects.using(self._current_app_schema()).filter(condition).order_by(
            'name')[
                               vys_page.get_offset():vys_page.get_query_limit()]

        customercategory_list_data = NWisefinList()
        for customercategory in customercategorylist:
            customercategory_data = CustomerCategoryResponse()
            customercategory_data.set_id(customercategory.id)
            customercategory_data.set_code(customercategory.code)
            customercategory_data.set_name(customercategory.name)
            customercategory_list_data.append(customercategory_data)
            vpage = NWisefinPaginator(customercategorylist, vys_page.get_index(), 10)
            customercategory_list_data.set_pagination(vpage)
        if len(customercategorylist) <= 0:
            vpage = NWisefinPaginator(customercategorylist, vys_page.get_index(), 10)
            customercategory_list_data.set_pagination(vpage)

        return customercategory_list_data
