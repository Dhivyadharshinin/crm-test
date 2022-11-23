from datetime import datetime

from django.db import IntegrityError
from django.db.models import Q

from masterservice.data.response.masterauditresponse import MasterAuditResponse
from masterservice.data.response.statezonecitymasterresponse import statezoneResponse
from masterservice.service.masterauditservice import MasterAuditService

from utilityservice.data.response.nwisefinerror  import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage,ErrorDescription
from utilityservice.data.response.nwisefinsuccess  import NWisefinSuccess,SuccessMessage,SuccessStatus
from utilityservice.data.response.nwisefinlist import NWisefinList
from masterservice.models import  StateZoneCityMaster
from django.utils import timezone

from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from masterservice.util.masterutil import ModifyStatus, MasterRefType, RequestStatusUtil

now = datetime.now()
now = str(now)


class statezonecityService:
    def create_statezone(self, exuom_obj, user_id):
        if not exuom_obj.get_id() is None:
            try:
                state = StateZoneCityMaster.objects.filter(id=exuom_obj.get_id()).update(
                    state_id=exuom_obj.get_state_id(),
                    zone=exuom_obj.get_zone(),
                    city_id=exuom_obj.get_city_id(),
                    updated_by=user_id,
                    updated_date=now
                )
                statezone = StateZoneCityMaster.objects.get(id=exuom_obj.get_id())
                statezonecity_auditdata = {'id': exuom_obj.get_id(),

                                           'state_id': exuom_obj.get_state_id(),
                                           'zone': exuom_obj.get_zone(),
                                           'city_id': exuom_obj.get_city_id(),

                                           'updated_by': user_id,
                                           'updated_date': now
                                           }
                self.audit_function(statezonecity_auditdata, user_id, statezone.id, ModifyStatus.update)
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
                return success_obj
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
        else:

                state = StateZoneCityMaster.objects.create(state_id=exuom_obj.get_state_id(),
                    zone=exuom_obj.get_zone(),
                    city_id=exuom_obj.get_city_id(),
                                                         created_by=user_id,
                                                         created_date=timezone.now(),
                                                         )
                self.audit_function(state, user_id, state.id, ModifyStatus.create)



        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj

    def statezonecity_list(self, user_id, vys_page):
        statezonelist = StateZoneCityMaster.objects.all()[
                        vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(statezonelist)
        print(list_length)
        if list_length <= 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_DATA)
            return error_obj
        else:
            statezone_list_data = NWisefinList()
            for state in statezonelist:
                state_data = statezoneResponse()
                state_data.set_id(state.id)
                state_data.set_state_id(state.state_id)
                state_data.set_city_id(state.statename)
                state_data.set_zone(state.zone)
                statezone_list_data.append(state_data)
                vpage = NWisefinPaginator(statezonelist, vys_page.get_index(), 10)
                statezone_list_data.set_pagination(vpage)
            return statezone_list_data

    def audit_function(self, data_obj, user_id, id, action):
        if action == ModifyStatus.delete:
            data = None
        elif action == ModifyStatus.update:
            data = data_obj
        else:
            data = data_obj.__dict__
            del data['_state']
        audit_service = MasterAuditService()
        audit_obj = MasterAuditResponse()
        audit_obj.set_refid(-1)
        audit_obj.set_reftype(MasterRefType.MASTER)
        audit_obj.set_userid(user_id)
        audit_obj.set_reqstatus(RequestStatusUtil.ONBOARD)
        audit_obj.set_relrefid(id)
        audit_obj.set_relreftype(MasterRefType.CITY)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)
        return






















