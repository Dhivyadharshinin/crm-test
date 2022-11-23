from datetime import datetime,timedelta

from django.db import IntegrityError
from django.db.models import Q

from masterservice.data.response.masterauditresponse import MasterAuditResponse

from masterservice.data.response.statezonecityresponse import StatezonecityResponse

from masterservice.service.masterauditservice import MasterAuditService

from utilityservice.data.response.nwisefinerror  import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage,ErrorDescription
from utilityservice.data.response.nwisefinsuccess  import NWisefinSuccess,SuccessMessage,SuccessStatus
from utilityservice.data.response.nwisefinlist import NWisefinList
from masterservice.models import NewStateZoneMapping,NewStateZone
from django.utils import timezone

from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from masterservice.util.masterutil import ModifyStatus, MasterRefType, RequestStatusUtil
from  masterservice.util.masterutil import getzoneType
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread

now = datetime.now()
now = str(now)


class statezoneService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_statezonecity(self, exuom_obj, user_id):
        if not exuom_obj.get_id() is None:
            try:
                statezone = NewStateZoneMapping.objects.using(self._current_app_schema()).filter(id=exuom_obj.get_id(),
                                                                                                 entity_id=self._entity_id()).update(
                    state_id=exuom_obj.get_statemap_id(),
                    zone=exuom_obj.get_zone(),
                    # effectivefrom=exuom_obj.get_effectivefrom(),
                    # effectiveto=exuom_obj.get_effectiveto(),
                    updated_by=user_id,
                    updated_date=now
                )
                statezone = NewStateZoneMapping.objects.using(self._current_app_schema()).get(id=exuom_obj.get_id(),
                                                                                              entity_id=self._entity_id())
                statezonecity_auditdata = {'id': exuom_obj.get_id(),

                                           'state_id': exuom_obj.get_statemap_id(),
                                           'statename': exuom_obj.get_statename(),
                                           'zone': exuom_obj.get_zone(),
                                           'effectivefrom': exuom_obj.get_effectivefrom(),
                                           'effectiveto': exuom_obj.get_effectiveto(),
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
            statezone_map_id = exuom_obj.get_statemap_id()
            m = NewStateZone.objects.using(self._current_app_schema()).get(id=statezone_map_id,
                                                                           entity_id=self._entity_id())
            zone_count = m.noofzones
            condition = Q(state_id__exact=statezone_map_id) & Q(entity_id=self._entity_id())
            s = NewStateZoneMapping.objects.using(self._current_app_schema()).filter(condition)
            if (len(s) < zone_count) or (zone_count == 0 and len(s) == 0):
                statezone = NewStateZoneMapping.objects.using(self._current_app_schema()).create(
                    state_id=exuom_obj.get_statemap_id(),
                    zone=exuom_obj.get_zone(),
                    # effectivefrom=exuom_obj.get_effectivefrom(),
                    # effectiveto=exuom_obj.get_effectiveto(),
                    created_by=user_id,
                    created_date=timezone.now(), entity_id=self._entity_id()
                    )
                self.audit_function(statezone, user_id, statezone.id, ModifyStatus.create)

            else:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_ZONE)
                error_obj.set_description(ErrorDescription.INVALID_ZONE)
                return error_obj
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
            return success_obj

    def statezonecity_list(self, vys_page, statemap_id):
        if statemap_id != None:
            statezonelist = NewStateZoneMapping.objects.using(self._current_app_schema()).filter(state_id=statemap_id,
                                                                                                 entity_id=self._entity_id())[
                            vys_page.get_offset():vys_page.get_query_limit()]
        else:
            statezonelist = NewStateZoneMapping.objects.using(self._current_app_schema()).filter(
                entity_id=self._entity_id())[
                            vys_page.get_offset():vys_page.get_query_limit()]

        statezone_list_data = NWisefinList()
        for state in statezonelist:
            state_data = StatezonecityResponse()
            state_data.set_id(state.id)
            state_data.set_state_id(state.state)
            state_data.set_zone(state.zone)
            # state_data.set_effectivefrom(state.effectivefrom)
            # state_data.set_effectiveto(state.effectiveto)
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
        audit_service = MasterAuditService(self._scope())  # changed
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

    def search_statezone_list(self, vys_page, state):
        if state != None:
            statezonemappinglist = NewStateZone.objects.using(self._current_app_schema()).filter(name__icontains=state,
                                                                                                 entity_id=self._entity_id()).values(
                'id', 'effectivefrom', 'name', 'code')[
                                   vys_page.get_offset():vys_page.get_query_limit()]
        else:
            statezonemappinglist = NewStateZone.objects.using(self._current_app_schema()).values('id', 'effectivefrom',
                                                                                                 'name', 'code')[
                                   vys_page.get_offset():vys_page.get_query_limit()]

        state_map_arr = [i['id'] for i in statezonemappinglist]
        zonelist = NewStateZoneMapping.objects.using(self._current_app_schema()).filter(state_id__in=state_map_arr,
                                                                                        entity_id=self._entity_id()).values(
            'zone', 'id', 'state_id')
        statezone_list_data = NWisefinList()
        for state in statezonemappinglist:
            state_data = StatezonecityResponse()
            state_data.set_id(state['id'])
            state_data.name = state['name']
            state_data.code = state['code']
            zonelist_data = self.filter_mapped_zone(zonelist, state['id'])
            arr = []
            for i in zonelist_data:
                zone = getzoneType(i['zone'])
                arr.append(zone)
            state_data.zone = arr
            state_data.set_effectivefrom(state['effectivefrom'])
            statezone_list_data.append(state_data)
            vpage = NWisefinPaginator(statezonemappinglist, vys_page.get_index(), 10)
            statezone_list_data.set_pagination(vpage)
        return statezone_list_data

    def filter_mapped_zone(self, obj, statezone_mapid):
        arr = [i for i in obj if i['state_id'] == statezone_mapid]
        return arr

    def stateandzone_mapping(self, data, emp_id):
        state_id = data.get_state_id()
        count = data.get_count()
        zone = data.get_zone()
        effectivefrom = data.get_effectivefrom()
        code = data.get_code()
        name = data.get_name()
        # effectiveto=None
        obj = NewStateZone.objects.using(self._current_app_schema()).filter(code=code,
                                                                            entity_id=self._entity_id()).order_by(
            '-created_date')
        if len(obj) > 0:
            previous_effectivefrom = obj[0].effectivefrom
            # previous_state_id=obj[0].state_id
            active_effectivefrom = datetime.strptime(effectivefrom, '%Y-%m-%d').date()
            if previous_effectivefrom >= active_effectivefrom:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_ZONE)
                error_obj.set_description(ErrorDescription.INVALID_ZONE)
                return error_obj
            active_effectivefrom = active_effectivefrom - timedelta(days=1)
            NewStateZone.objects.using(self._current_app_schema()).filter(code=code,
                                                                          entity_id=self._entity_id()).update(
                effectiveto=active_effectivefrom)

        statezone_count = NewStateZone.objects.using(self._current_app_schema()).create(noofzones=count,
                                                                                        created_by=emp_id,
                                                                                        created_date=timezone.now()
                                                                                        , effectivefrom=effectivefrom,
                                                                                        name=name, code=code,
                                                                                        entity_id=self._entity_id())
        print(statezone_count, zone, count)
        if (len(zone) == count) or (count == 0 and len(zone) == 1):
            for i in zone:
                NewStateZoneMapping.objects.using(self._current_app_schema()).create(state_id=statezone_count.id,
                                                                                     zone=i,
                                                                                     created_by=emp_id,
                                                                                     created_date=timezone.now(),
                                                                                     entity_id=self._entity_id())

            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
            return success_obj
        else:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_ZONE)
            error_obj.set_description(ErrorDescription.INVALID_ZONE)
            return error_obj

    def statezonemapping_list(self, vys_page, state):
        if state != None:
            statezonemappinglist = NewStateZone.objects.using(self._current_app_schema()).filter(name__icontains=state,
                                                                                                 entity_id=self._entity_id()).order_by(
                '-created_date')[
                                   vys_page.get_offset():vys_page.get_query_limit()]
        else:
            statezonemappinglist = NewStateZone.objects.using(self._current_app_schema()).filter(
                entity_id=self._entity_id()).order_by('-created_date')[
                                   vys_page.get_offset():vys_page.get_query_limit()]

        state_map_arr = [i.id for i in statezonemappinglist]
        zonelist = NewStateZoneMapping.objects.using(self._current_app_schema()).filter(state_id__in=state_map_arr,
                                                                                        entity_id=self._entity_id()).values(
            'zone', 'id', 'state_id')
        statezone_list_data = NWisefinList()
        for obj in statezonemappinglist:
            state_data = StatezonecityResponse()
            state_data.set_id(obj.id)
            state_data.set_state(obj.state)
            state_data.name = obj.name
            state_data.code = obj.code
            zonelist_data = self.filter_mapped_zone(zonelist, obj.id)
            arr = []
            for i in zonelist_data:
                zone = getzoneType(i['zone'])
                arr.append(zone)
            state_data.zone = arr
            state_data.set_effectivefrom(obj.effectivefrom)
            state_data.set_effectiveto(obj.effectiveto)
            state_data.set_count(obj.noofzones)

            statezone_list_data.append(state_data)
        vpage = NWisefinPaginator(statezonemappinglist, vys_page.get_index(), 10)
        statezone_list_data.set_pagination(vpage)

        return statezone_list_data
