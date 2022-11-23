from django.db import IntegrityError
from django.db.models import Q
from django.utils.timezone import now

from inwardservice.data.response.escalatontyperesponse import EscalationSubTypeResponse
from inwardservice.models import EscalationType, EscalationSubType
from inwardservice.service.escalationtypeservice import EscalationTypeService
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


class EscalationSubTypeService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.INWARD_SERVICE)
    def create_escaltionsubtype(self, escaltiontype_obj, user_id):
        if not escaltiontype_obj.get_id() is None:
            try:
                escalation = EscalationSubType.objects.filter(id=escaltiontype_obj.get_id()).update(name=escaltiontype_obj.get_name(),
                                                                                                escalationtype_id=escaltiontype_obj.get_escalationtype_id(),
                                                                                                    updated_date=now(),
                                                                                     updated_by=user_id
                                                                                     )
                escalation = EscalationSubType.objects.get(id=escaltiontype_obj.get_id())
            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except EscalationType.DoesNotExist:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_ESCATIONSUBTYPE_ID)
                error_obj.set_description(ErrorDescription.INVALID_ESCATIONSUBTYPE_ID)
                return error_obj
            except:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                escalation = EscalationSubType.objects.create(name=escaltiontype_obj.get_name(),
                                                               escalationtype_id=escaltiontype_obj.get_escalationtype_id(),
                                                    created_by=user_id)
                code = "IEST" + str(escalation.id)
                escalation.code = code
                escalation.save()
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
        escalation_data = EscalationSubTypeResponse()
        escal_service = EscalationTypeService()
        escalation_data.set_id(escalation.id)
        escalation_data.set_name(escalation.name)
        escalation_data.set_code(escalation.code)
        escalation_data.set_escalationtype(escal_service.fetch_escalation(escalation.escalationtype_id))
        return escalation_data

    def fetch_escalationsub_list(self,query, vys_page):
        escalation_list = EscalationSubType.objects.all()[vys_page.get_offset():vys_page.get_query_limit()]
        if query is None:
            objj = EscalationSubType.objects.filter(status=1)[vys_page.get_offset():vys_page.get_query_limit()]
        else:
            condition = Q(name__icontains=query) & Q(status=1)
            #print(condition)
            objj = EscalationSubType.objects.filter(condition)[vys_page.get_offset():vys_page.get_query_limit()]
        print('object')
        list_length = len(escalation_list)
        #print(list_length)
        escalation_list_data = NWisefinList()
        if list_length <= 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_INWARDHEADER_ID)
            error_obj.set_description(ErrorDescription.INVALID_INWARDHEADER_ID)
            return error_obj
        else:
            for escalation in objj:
                escal_service = EscalationTypeService()
                escalation_data = EscalationSubTypeResponse()
                escalation_data.set_id(escalation.id)
                escalation_data.set_name(escalation.name)
                escalation_data.set_code(escalation.code)
                escalation_data.set_escalationtype(escalation.escalationtype)
                if escalation.escalationtype == None:
                    escalation_data.set_escalationtype(None)
                elif escalation.escalationtype != None:
                    escalation_data.set_escalationtype(escal_service.fetch_escalation(escalation.escalationtype_id))
                    escalation_list_data.append(escalation_data)

            vpage = NWisefinPaginator(escalation_list, vys_page.get_index(), 10)
            escalation_list_data.set_pagination(vpage)
        return escalation_list_data

    def fetch_escalationsub(self,escalationtype_id):
        try:
            escalation = EscalationSubType.objects.get(id=escalationtype_id)
            escalation_data = EscalationSubTypeResponse()
            escal_service = EscalationTypeService()
            escalation_data.set_id(escalation.id)
            escalation_data.set_name(escalation.name)
            escalation_data.set_code(escalation.code)
            escalation_data.set_escalationtype(escal_service.fetch_escalation(escalation.escalationtype_id))
            return escalation_data
        except EscalationSubType.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_ESCATIONSUBTYPE_ID)
            error_obj.set_description(ErrorDescription.INVALID_ESCATIONSUBTYPE_ID)
            return error_obj

    def delete_escalationsub(self, escalationsub_id):
        escalation = EscalationSubType.objects.filter(id=escalationsub_id).delete()
        if escalation[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_ESCATIONSUBTYPE_ID)
            error_obj.set_description(ErrorDescription.INVALID_ESCATIONSUBTYPE_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj


    def search_escalationsub(self, request, query, vys_page):
        condition = None
        if query is not None:
            condition = Q(name__icontains = query) | Q(code__icontains = query)
        if condition is not None:
            escalationsubList = EscalationSubType.objects.values('id', 'name', 'code').filter(condition)[
                           vys_page.get_offset():vys_page.get_query_limit()]
        else:
            escalationsubList = EscalationSubType.objects.values('id','name', 'code').all()[
                           vys_page.get_offset():vys_page.get_query_limit()]
        vlist = NWisefinList()
        for escalsub in escalationsubList:
            escalationsub_res = EscalationSubTypeResponse()
            disp_name = '(' + escalsub['code'] + ') ' + escalsub['name']
            escalationsub_res.set_name(disp_name)
            escalationsub_res.set_id(escalsub['id'])
            escalationsub_res.set_name(escalsub['name'])
            vlist.append(escalationsub_res)
        vpage = NWisefinPaginator(escalationsubList, vys_page.get_index(), 10)
        vlist.set_pagination(vpage)
        return vlist
