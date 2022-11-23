from datetime import datetime

from django.db import IntegrityError

from masterservice.data.response.minwagestatezoneresponse import minwageResponse
from utilityservice.data.response.nwisefinerror  import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage,ErrorDescription
from utilityservice.data.response.nwisefinsuccess  import NWisefinSuccess,SuccessMessage,SuccessStatus
from utilityservice.data.response.nwisefinlist import NWisefinList
from masterservice.models import NewStateZone
from django.utils import timezone
from masterservice.service.masterauditservice import MasterAuditService
from masterservice.data.response.masterauditresponse import MasterAuditResponse
from masterservice.util.masterutil import ModifyStatus,MasterRefType,RequestStatusUtil
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread

now = datetime.now()
now = str(now)


class minwageService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_minwage(self, exuom_obj, user_id):
        if not exuom_obj.get_id() is None:
            try:
                minwage = NewStateZone.objects.using(self._current_app_schema()).filter(id=exuom_obj.get_id(),
                                                                                        entity_id=self._entity_id()).update(
                    noofzones=exuom_obj.get_noofzones(),
                    updated_by=user_id,
                    updated_date=now

                )
                minwage = NewStateZone.objects.using(self._current_app_schema()).get(id=exuom_obj.get_id(),
                                                                                     entity_id=self._entity_id())
                minwage_auditdata = {'id': exuom_obj.get_id(),

                                     'state_id': exuom_obj.get_state_id(),
                                     'noofzones': exuom_obj.get_noofzones(),
                                     'updated_by': user_id,
                                     'updated_date': now

                                     }
                self.audit_function(minwage_auditdata, user_id, minwage.id, ModifyStatus.update)
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
            state_zone_count = NewStateZone.objects.using(self._current_app_schema()).filter(
                state_id=exuom_obj.get_state_id(), entity_id=self._entity_id())
            if len(state_zone_count) <= 0:
                minwage = NewStateZone.objects.using(self._current_app_schema()).create(
                    state_id=exuom_obj.get_state_id(),
                    noofzones=exuom_obj.get_noofzones(), created_by=user_id, created_date=timezone.now(),
                    entity_id=self._entity_id())
                self.audit_function(minwage, user_id, minwage.id, ModifyStatus.create)

            else:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description("Already zone assigned to this state")
                return error_obj

        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj

    def minwagestate_list(self, vys_page):
        state_zone = NewStateZone.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id())[
                     vys_page.get_offset():vys_page.get_query_limit()]
        state_zone_list = NWisefinList()
        for obj in state_zone:
            state_zone_date = minwageResponse()
            state_zone_date.set_id(obj.id)
            state_zone_date.set_state_id(obj.state)
            state_zone_date.set_noofzones(obj.noofzones)
            state_zone_list.append(state_zone_date)
            vpage = NWisefinPaginator(state_zone, vys_page.get_index(), 10)
            state_zone_list.set_pagination(vpage)
        return state_zone_list

    def audit_function(self, data_obj, user_id, id, action):
        if action == ModifyStatus.delete:
            data = None
        elif action == ModifyStatus.update:
            data = data_obj
        else:
            data = data_obj.__dict__
            del data['_state']
        audit_service = MasterAuditService(self._scope())  # changes
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
