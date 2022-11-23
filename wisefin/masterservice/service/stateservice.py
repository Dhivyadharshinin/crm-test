import traceback
from django.db import IntegrityError
from masterservice.models import State,Country
from masterservice.data.response.stateresponse import StateResponse
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror  import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage,ErrorDescription
from utilityservice.data.response.nwisefinsuccess  import NWisefinSuccess,SuccessMessage,SuccessStatus
from utilityservice.data.response.nwisefinlist import NWisefinList
from django.utils import timezone
from masterservice.data.request.masterauditrequest import MasterAuditRequest
from masterservice.service.masterauditservice import MasterAuditService
from masterservice.data.response.masterauditresponse import MasterAuditResponse
from masterservice.util.masterutil import ModifyStatus, MasterRefType, RequestStatusUtil, MasterStatus
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from masterservice.service.Codegenerator import CodeGen


class StateService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_state(self, State_obj, user_id):
        if not State_obj.get_id() is None:
            try:
                logger.error('STATE: State Update Started')
                state_update = State.objects.using(self._current_app_schema()).filter(id=State_obj.get_id(),
                                                                                      entity_id=self._entity_id()).update(
                    # code=State_obj.get_code(),
                    name=State_obj.get_name(),
                    country_id=State_obj.get_country_id(),
                    updated_by=user_id,
                    updated_date=timezone.now())
                state = State.objects.using(self._current_app_schema()).get(id=State_obj.get_id(),
                                                                            entity_id=self._entity_id())
                logger.error('STATE: State Update Success' + str(state_update))
                state_auditdata = {'id': State_obj.get_id(),
                                   # 'code': State_obj.get_code(),
                                   'name': State_obj.get_name(),
                                   'country_id': State_obj.get_country_id(),
                                   'updated_date': timezone.now(),
                                   'updated_by': user_id}
                self.audit_function(state_auditdata, user_id, state.id, ModifyStatus.update)

            except IntegrityError as error:
                logger.error('ERROR_State_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except State.DoesNotExist:
                logger.error('ERROR_State_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_District_ID)
                error_obj.set_description(ErrorDescription.INVALID_District_ID)
                return error_obj
            except:
                logger.error('ERROR_State_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                logger.error('STATE: State Creation Started')
                data_len = State.objects.using(self._current_app_schema()).filter(
                    name=State_obj.get_name()).values()
                if (len(data_len) > 0):
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVALID_DATA)
                    error_obj.set_description(ErrorDescription.DUPLICATE_NAME)
                    return error_obj
                state = State.objects.using(self._current_app_schema()).create(  # code=State_obj.get_code(),
                    name=State_obj.get_name(),
                    country_id=State_obj.get_country_id(), created_by=user_id, entity_id=self._entity_id())

                # code = "ISCT" + str(state.id)
                try:
                    max_cat_code = State.objects.using(self._current_app_schema()).filter(code__icontains='SN').order_by('-code')[0].code
                    rnsl = int(max_cat_code[2:])
                except:
                    rnsl = 0
                new_rnsl = rnsl + 1
                code = "SN" + str(new_rnsl).zfill(5)
                state.code = code
                state.save()
                self.audit_function(state, user_id, state.id, ModifyStatus.create)
                logger.error('STATE: State Creation Success' + str(state))

            except IntegrityError as error:
                logger.error('ERROR_State_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                logger.error('ERROR_State_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        State_data = StateResponse()
        State_data.set_id(state.id)
        State_data.set_code(state.code)
        State_data.set_name(state.name)
        State_data.set_status(state.status)
        State_data.set_country_id(state.country_id)
        State_data.set_created_by(state.created_by)
        State_data.set_updated_by(state.updated_by)

        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        return success_obj


    def fetchstate(self, state_id):
        try:
            state = State.objects.using(self._current_app_schema()).get(id=state_id, entity_id=self._entity_id())
            State_data = StateResponse()
            State_data.set_id(state.id)
            State_data.set_code(state.code)
            State_data.set_name(state.name)
            State_data.set_status(state.status)
            State_data.set_country_id(state.country_id)
            State_data.set_created_by(state.created_by)
            State_data.set_updated_by(state.updated_by)
            return State_data
        except State.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_STATE_ID)
            error_obj.set_description(ErrorDescription.INVALID_STATE_ID)
            return error_obj

    def hrms_get_addressstate(self,statearr):
         state = State.objects.using(self._current_app_schema()).filter(id__in=statearr)
         state_list = []
         for state_data in state:
             State_data = StateResponse()
             State_data.set_id(state_data.id)
             State_data.set_name(state_data.name)
             state_list.append(State_data)
         return state_list


    def fetch_state_list(self, vys_page):
        try:
            stateList = State.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).order_by(
                'created_date')[
                        vys_page.get_offset():vys_page.get_query_limit()]
            list_length = len(stateList)
            state_list_data = NWisefinList()
            if list_length <= 0:
                pass
            else:
                for state in stateList:
                    State_data = StateResponse()
                    State_data.set_id(state.id)
                    State_data.set_code(state.code)
                    State_data.set_name(state.name)
                    State_data.set_status(state.status)
                    State_data.set_country_id(state.country_id)
                    State_data.set_created_by(state.created_by)
                    State_data.set_updated_by(state.updated_by)
                    state_list_data.append(State_data)
                    vpage = NWisefinPaginator(stateList, vys_page.get_index(), 10)
                    state_list_data.set_pagination(vpage)
            return state_list_data
        except:
            logger.error('ERROR_State_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_STATE_ID)
            error_obj.set_description(ErrorDescription.INVALID_STATE_ID)
            return error_obj

    def fetch_state_download(self, request):
        try:
            stateList = State.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).order_by(
                'created_date')
            list_length = len(stateList)
            state_list_data = NWisefinList()
            if list_length <= 0:
                pass
            else:
                for state in stateList:
                    State_data = StateResponse()
                    State_data.Code=(state.code)
                    State_data.Name=(state.name)
                    status = MasterStatus()
                    if state.status == status.Active:
                        State_data.Status = status.Active_VALUE
                    if state.status == status.Inactive:
                        State_data.Status = status.Inactive_VALUE
                    # State_data.Status=(state.status)
                    State_data.country_id=(state.country_id)
                    state_list_data.append(State_data)

            return state_list_data
        except:
            logger.error('ERROR_State_Excel_Download_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_STATE_ID)
            error_obj.set_description(ErrorDescription.INVALID_STATE_ID)
            return error_obj


    def delete_state(self, state_id, user_id):
        state = State.objects.using(self._current_app_schema()).filter(id=state_id,
                                                                       entity_id=self._entity_id()).delete()
        self.audit_function(state, user_id, state_id, ModifyStatus.delete)

        if state[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DISTRICT_ID)
            error_obj.set_description(ErrorDescription.INVALID_DISTRICT_ID)
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
        audit_obj.set_relreftype(MasterRefType.STATE)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)
        return

    def fetch_state_search(self, query, vys_page):
        if query is None:
            stateList = State.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).order_by(
                'created_date')[
                        vys_page.get_offset():vys_page.get_query_limit()]
        else:
            stateList = State.objects.using(self._current_app_schema()).filter(name__icontains=query).order_by('created_date')[
                         vys_page.get_offset():vys_page.get_query_limit()]

        state_list_data = NWisefinList()
        for state in stateList:
            State_data = StateResponse()
            State_data.set_id(state.id)
            State_data.set_code(state.code)
            State_data.set_name(state.name)
            State_data.set_status(state.status)
            State_data.set_country_id(state.country_id)
            # countryid=state.country_id
            # country=Country.objects.using(self._current_app_schema()).get(id=countryid)
            # State_data.set_country_name(country.name)

            state_list_data.append(State_data)
            vpage = NWisefinPaginator(stateList, vys_page.get_index(), 10)
            state_list_data.set_pagination(vpage)
        return state_list_data

    def get_state_by_name(self,name):
        state_obj = State.objects.filter(name=name).order_by('created_date')
        if len(state_obj)==0:
            state = State.objects.create(name=name)
            return state.id
        else :
            state =state_obj[0]
            return state.id
            # return None

    def create_state_mtom(self, State_obj, user_id):
        if not State_obj.get_id() is None:
            try:
                state_update = State.objects.using(self._current_app_schema()).filter(id=State_obj.get_id(),
                                                                                      entity_id=self._entity_id()).update(
                    code=State_obj.get_code(),
                    name=State_obj.get_name(),
                    country_id=State_obj.get_country_id(),
                    updated_by=user_id,
                    updated_date=timezone.now())
                state = State.objects.using(self._current_app_schema()).get(id=State_obj.get_id(),
                                                                            entity_id=self._entity_id())
                state_auditdata = {'id': State_obj.get_id(),
                                   'code': State_obj.get_code(),
                                   'name': State_obj.get_name(),
                                   'country_id': State_obj.get_country_id(),
                                   'updated_date': timezone.now(),
                                   'updated_by': user_id}
                self.audit_function(state_auditdata, user_id, state.id, ModifyStatus.update)

            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except State.DoesNotExist:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_District_ID)
                error_obj.set_description(ErrorDescription.INVALID_District_ID)
                return error_obj
            except:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                state = State.objects.using(self._current_app_schema()).create(code=State_obj.get_code(),
                                                                               name=State_obj.get_name(),
                                                                               country_id=State_obj.get_country_id(),
                                                                               created_by=user_id,
                                                                               entity_id=self._entity_id())

                self.audit_function(state, user_id, state.id, ModifyStatus.create)

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
        State_data = StateResponse()
        State_data.set_id(state.id)
        State_data.set_code(state.code)
        State_data.set_name(state.name)
        State_data.set_status(state.status)
        State_data.set_country_id(state.country_id)
        State_data.set_created_by(state.created_by)

        return State_data

    def fetch_stateone(request, state_id):
        state = State.objects.using(request._current_app_schema()).get(id=state_id, entity_id=request._entity_id())
        state_data = {"id": state.id, "code": state.code, "name": state.name}
        # state_dic = json.dumps(state_data, indent=4)
        return state_data

    def fetch_statelist(request, state_data):
        # state_ids = json.loads(request.body)
        state_id2 = state_data['state_id']
        obj = State.objects.using(request._current_app_schema()).filter(id__in=state_id2,
                                                                        entity_id=request._entity_id()).values('id',
                                                                                                               'name')
        state_list_data = NWisefinList()
        for i in obj:
            data = {"id": i['id'], "name": i['name']}
            state_list_data.append(data)
        return state_list_data

    def state_scroll(self, country_id, vys_page, data):
        statelist = State.objects.using(self._current_app_schema()).filter(country__id=country_id, status=1, name__icontains=data).order_by('created_date')[
                       vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(statelist)
        state_list_data = NWisefinList()
        try:
            if list_length <= 0:
                pass
            else:
                for state in statelist:
                    State_data = StateResponse()
                    State_data.set_id(state.id)
                    State_data.set_code(state.code)
                    State_data.set_name(state.name)
                    State_data.set_status(state.status)
                    State_data.set_country_id(state.country_id)
                    State_data.set_created_by(state.created_by)
                    state_list_data.append(State_data)
                vpage = NWisefinPaginator(statelist, vys_page.get_index(), 10)
                state_list_data.set_pagination(vpage)
            return state_list_data

        except State.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_STATE_ID)
            error_obj.set_description(ErrorDescription.INVALID_STATE_ID)
            return error_obj

    def create_sync_state(self,state_name,country_id,Entity):
        state = State.objects.using(self._current_app_schema()).filter(name=state_name)
        if len(state) > 0:
            state_id = state[0].id
            return state_id
        else:
            state = State.objects.using(self._current_app_schema()).create(entity_id=Entity,name=state_name,country_id=country_id)
            rnsl = 0
            new_rnsl = rnsl + 1
            code = "SN" + str(new_rnsl).zfill(5)
            state.code = code
            state.save()
            return state.id