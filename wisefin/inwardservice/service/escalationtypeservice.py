from django.db import IntegrityError
from django.db.models import Q

from inwardservice.data.response.escalatontyperesponse import EscalationTypeResponse
from inwardservice.models import EscalationType
from django.utils.timezone import now

from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


class EscalationTypeService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.INWARD_SERVICE)
    def create_escaltiontype(self, escaltiontype_obj, user_id):
        escalation = EscalationType.objects.filter(name=escaltiontype_obj.get_name(), status=1)
        if len(escalation) > 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.DUPLICATE_NAME)
            return error_obj
        if not escaltiontype_obj.get_id() is None:
            try:
                escalationtype = EscalationType.objects.filter(id=escaltiontype_obj.get_id()).update(name=escaltiontype_obj.get_name(),
                                                                                     updated_date=now(),
                                                                                     updated_by=user_id,
                                                                                     )
                escalationtype = EscalationType.objects.get(id=escaltiontype_obj.get_id())
            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except EscalationType.DoesNotExist:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_ESCATIONTYPE_ID)
                error_obj.set_description(ErrorDescription.INVALID_ESCATIONTYPE_ID)
                return error_obj
            except:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                escalationtype = EscalationType.objects.create(name=escaltiontype_obj.get_name(),
                                                    created_by=user_id)

                code = "IETP" + str(escalationtype.id)
                escalationtype.code = code
                escalationtype.save()
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
        escalation_data = EscalationTypeResponse()
        escalation_data.set_id(escalationtype.id)
        escalation_data.set_code(escalationtype.code)
        escalation_data.set_name(escalationtype.name)
        return escalation_data

    def fetch_escalation_list(self,query, vys_page):
        escalation_list = EscalationType.objects.all()[vys_page.get_offset():vys_page.get_query_limit()]
        if query is None:
            objj = EscalationType.objects.filter(status=1)[vys_page.get_offset():vys_page.get_query_limit()]
        else:
            condition = Q(name__icontains=query) & Q(status=1)
            print(condition)
            objj = EscalationType.objects.filter(condition)[vys_page.get_offset():vys_page.get_query_limit()]

        list_length = len(escalation_list)
        #print(list_length)
        escalation_list_data = NWisefinList()       ##
        if list_length <= 0:
            error_obj = NWisefinError()             ##
            error_obj.set_code(ErrorMessage.INVALID_INWARDHEADER_ID)
            error_obj.set_description(ErrorDescription.INVALID_INWARDHEADER_ID)
            return error_obj
        else:
            for escalation in objj:
                escalation_data = EscalationTypeResponse()
                escalation_data.set_id(escalation.id)
                escalation_data.set_name(escalation.name)
                escalation_data.set_code(escalation.code)
                escalation_list_data.append(escalation_data)
            vpage = NWisefinPaginator(escalation_list, vys_page.get_index(), 10)
            escalation_list_data.set_pagination(vpage)
            return escalation_list_data

    def fetch_escalation(self,escalationtype_id):
        try:
            escalation = EscalationType.objects.get(id=escalationtype_id)
            escalation_data = EscalationTypeResponse()
            escalation_data.set_id(escalation.id)
            escalation_data.set_name(escalation.name)
            escalation_data.set_code(escalation.code)
            return escalation_data
        except EscalationType.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_ESCATIONTYPE_ID)
            error_obj.set_description(ErrorDescription.INVALID_ESCATIONTYPE_ID)
            return error_obj

    def delete_escalation(self, escalation_id):
        escalation = EscalationType.objects.filter(id=escalation_id).delete()
        if escalation[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_ESCATIONTYPE_ID)
            error_obj.set_description(ErrorDescription.INVALID_ESCATIONTYPE_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

    def search_escalation(self, request, query, vys_page):
        condition = None
        if query is not None:
            condition = Q(name__icontains=query) | Q(code__icontains = query)
        if condition is not None:
            escalationList = EscalationType.objects.values('id', 'name', 'code').filter(condition)[
                           vys_page.get_offset():vys_page.get_query_limit()]
        else:
            escalationList = EscalationType.objects.values('id','name', 'code').all()[
                           vys_page.get_offset():vys_page.get_query_limit()]
        vlist = NWisefinList()
        for escal in escalationList:
            escalation_res = EscalationTypeResponse()
            disp_name = '(' + escal['code'] + ') ' + escal['name']
            escalation_res.set_name(disp_name)
            escalation_res.set_id(escal['id'])
            escalation_res.set_name(escal['name'])
            vlist.append(escalation_res)
        vpage = NWisefinPaginator(escalationList, vys_page.get_index(), 10)
        vlist.set_pagination(vpage)
        return vlist