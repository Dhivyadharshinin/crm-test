import json
from inwardservice.data.response.inwardtemplateresponse import InwardTemplateResponse
from inwardservice.data.response.inwardauditresponse import InwardAuditResponse
from inwardservice.models import InwardTemplate
# from inwardservice.service.escalationsubtypeservice import EscalationSubTypeService
# from inwardservice.service.escalationtypeservice import EscalationTypeService
from inwardservice.service.inwardauditservice import InwardAuditService
# from inwardservice.data.response.escalatontyperesponse import EscalationTypeResponse
from inwardservice.util.inwardutil import InwardRefType, ModifyStatus, RequestStatusUtil
from django.db import IntegrityError
from django.utils import timezone

from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


class InwardTemplateService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.INWARD_SERVICE)
    def create_inward_template(self, template_obj, emp_id):
        if not template_obj.get_id() is None:
            try:
                temp_update = InwardTemplate.objects.filter(id=template_obj.get_id()).update(
                    template_name=template_obj.get_template_name(),
                    template_content=template_obj.get_template_content(),
                    escalationsubtype_id=template_obj.get_escalationsubtype_id(),
                    updated_date=timezone.now(),
                    updated_by=emp_id)
                temp_var = InwardTemplate.objects.get(id=template_obj.get_id())
                req_status = RequestStatusUtil.ONBORD
                self.inward_audit(temp_var.__dict__, temp_var.id, emp_id, req_status, temp_var.id,
                                  ModifyStatus.UPDATE, InwardRefType.INWARD_TEMPLATE)
            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except InwardTemplate.DoesNotExist:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_TEMP_ID)
                error_obj.set_description(ErrorDescription.INVALID_TEMP_ID)
                return error_obj
            except:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                temp_var = InwardTemplate.objects.create(template_name=template_obj.get_template_name(),
                                                         template_content=template_obj.get_template_content(),
                                                         escalationsubtype_id=template_obj.get_escalationsubtype_id(),
                                                         created_by=emp_id)
                req_status = RequestStatusUtil.ONBORD
                self.inward_audit(temp_var.__dict__, temp_var.id, emp_id, req_status, temp_var.id,
                                  ModifyStatus.CREATE, InwardRefType.INWARD_TEMPLATE)
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
        inward_temp_data = InwardTemplateResponse()
        inward_temp_data.set_id(temp_var.id)
        inward_temp_data.set_template_name(temp_var.template_name)
        inward_temp_data.set_template_content(temp_var.template_content)
        inward_temp_data.set_escalationsubtype(temp_var.escalationsubtype)
        return inward_temp_data

    def fetch_inward_temp_list(self, vys_page):
        templist = InwardTemplate.objects.all()[vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(templist)
        print(list_length)
        if list_length <= 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_TEMP_ID)
            error_obj.set_description(ErrorDescription.INVALID_TEMP_ID)
            return error_obj
        else:
            temp_list_data = NWisefinList()
            for template_obj in templist:
                inward_temp_data = InwardTemplateResponse()
                inward_temp_data.set_id(template_obj.id)
                inward_temp_data.set_template_name(template_obj.template_name)
                inward_temp_data.set_template_content(template_obj.template_content)
                inward_temp_data.set_escalationsubtype(template_obj.escalationsubtype)
                temp_list_data.append(inward_temp_data)
            vpage = NWisefinPaginator(templist, vys_page.get_index(), 10)
            temp_list_data.set_pagination(vpage)
            return temp_list_data

    def fetch_inward_temp(self, inwardtemp_id, emp_id):
        try:
            temp_var = InwardTemplate.objects.get(id=inwardtemp_id)
            inward_temp_data = InwardTemplateResponse()
            inward_temp_data.set_id(temp_var.id)
            inward_temp_data.set_template_name(temp_var.template_name)
            inward_temp_data.set_template_content(temp_var.template_content)
            inward_temp_data.set_escalationsubtype(temp_var.escalationsubtype)
            return inward_temp_data
        except InwardTemplate.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_TEMP_ID)
            error_obj.set_description(ErrorDescription.INVALID_TEMP_ID)
            return error_obj


    def delete_inward_temp(self, inwardtemp_id,emp_id):
        temp_inward = InwardTemplate.objects.filter(id=inwardtemp_id).delete()
        self.inward_audit(temp_inward, inwardtemp_id, emp_id, RequestStatusUtil.ONBORD, inwardtemp_id,
                          ModifyStatus.DELETE, InwardRefType.INWARD_TEMPLATE)

        if temp_inward[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_TEMP_ID)
            error_obj.set_description(ErrorDescription.INVALID_TEMP_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

    def inward_audit(self, inward_data, inward_id, user_id, req_status, inwardrel_id, action, inwardrel_type):
        if action == ModifyStatus.DELETE:
            data = None
        else:
            data = inward_data

        audit_service = InwardAuditService()
        audit_obj = InwardAuditResponse()
        audit_obj.set_refid(inward_id)
        audit_obj.set_reftype(InwardRefType.INWARD_HEADRER)
        audit_obj.set_userid(user_id)
        audit_obj.set_reqstatus(req_status)
        audit_obj.set_relrefid(inwardrel_id)
        audit_obj.set_relreftype(inwardrel_type)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)
        return
