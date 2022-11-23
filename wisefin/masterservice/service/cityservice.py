import traceback

from django.db import IntegrityError

from masterservice.models import City, State ,Pincode
from masterservice.data.response.cityresponse import CityResponse,CitySearchResponse
from masterservice.service.Codegenerator import CodeGen
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror  import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage,ErrorDescription
from utilityservice.data.response.nwisefinsuccess  import NWisefinSuccess,SuccessMessage,SuccessStatus
from utilityservice.data.response.nwisefinlist import NWisefinList
from django.utils import timezone
from masterservice.data.request.masterauditrequest import MasterAuditRequest
from masterservice.service.masterauditservice import MasterAuditService
from masterservice.data.response.masterauditresponse import MasterAuditResponse
from masterservice.util.masterutil import ModifyStatus, MasterRefType, RequestStatusUtil, Code_Gen_Type, Code_Gen_Value, \
    MasterStatus
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from masterservice.service.pincodeservice import PincodeService
from masterservice.service.stateservice import StateService
from django.db.models import Q

from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


class CityService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_city(self, city_obj, user_id,id=None):
        if not city_obj.get_id() is None:
            try:
                logger.error('CITY: city Update Started')
                city_update = City.objects.using(self._current_app_schema()).filter(id=city_obj.get_id(),
                                                                                    entity_id=self._entity_id()).update(
                    # code =city_obj.get_code(),
                    name=city_obj.get_name(), state_id=city_obj.get_state(),
                    updated_by=user_id, updated_date=timezone.now())
                city = City.objects.get(id=city_obj.get_id(), entity_id=self._entity_id())
                logger.error('CITY: city Update Success' + str(city_update))
                city_auditdata = {'id': city_obj.get_id(),
                                  # 'code': city_obj.get_code(),
                                  'name': city_obj.get_name(), 'state_id': city_obj.get_state(),
                                  'updated_date': timezone.now(),
                                  'updated_by': user_id}

                self.audit_function(city_auditdata, user_id, city.id, ModifyStatus.update)

            except IntegrityError as error:
                logger.error('ERROR_city_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except City.DoesNotExist:
                logger.error('ERROR_city_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_CITY_ID)
                error_obj.set_description(ErrorDescription.INVALID_CITY_ID)
                return error_obj
            except:
                logger.error('ERROR_city_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                data_len = City.objects.using(self._current_app_schema()).filter(
                    name=city_obj.get_name()).values()
                if (len(data_len) > 0):
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVALID_DATA)
                    error_obj.set_description(ErrorDescription.DUPLICATE_NAME)
                    return error_obj
                logger.error('CITY: city Creation Started')
                city = City.objects.using(self._current_app_schema()).create(  # code =city_obj.get_code(),
                    name=city_obj.get_name(), state_id=city_obj.get_state(),
                    created_by=user_id, entity_id=self._entity_id())

                try:
                    max_cat_code = City.objects.using(self._current_app_schema()).filter(code__icontains='CY').order_by('-code')[0].code
                    rnsl = int(max_cat_code[2:])
                except:
                    rnsl = 0
                new_rnsl = rnsl + 1
                code = "CY" + str(new_rnsl).zfill(5)# code = "ISCT" + str(city.id)
                city.code = code
                city.save()
                logger.error('CITY: city Creation Success' + str(city))
                self.audit_function(city, user_id, city.id, ModifyStatus.create)
            except IntegrityError as error:
                logger.error('ERROR_city_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                logger.error('ERROR_city_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        if id!=None:
            city_data = CityResponse()
            city_data.set_id(city.id)
            city_data.set_code(city.code)
            city_data.set_name(city.name)
            city_data.set_state(city.state_id)
            # city_data.set_district_id(city.disrict_id)
            return city_data
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj

    def fetch_city_list(self, user_id, vys_page):
        try:
            citylist = City.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).order_by(
                'created_date')[
                       vys_page.get_offset():vys_page.get_query_limit()]
            list_length = len(citylist)
            if list_length <= 0:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_CITY_ID)
                error_obj.set_description(ErrorDescription.INVALID_CITY_ID)
                return error_obj
            else:
                city_list_data = NWisefinList()
                for city in citylist:
                    city_data = CityResponse()
                    city_data.set_id(city.id)
                    city_data.set_code(city.code)
                    city_data.set_name(city.name)
                    city_data.set_state(city.state_id)
                    city_list_data.append(city_data)
                    vpage = NWisefinPaginator(citylist, vys_page.get_index(), 10)
                    city_list_data.set_pagination(vpage)
                return city_list_data
        except:
            logger.error('ERROR_City_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_CITY_ID)
            error_obj.set_description(ErrorDescription.INVALID_CITY_ID)
            return error_obj
    def fetch_city_download(self, user_id):
        try:
            citylist = City.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).order_by(
                'created_date')
            list_length = len(citylist)
            if list_length <= 0:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_CITY_ID)
                error_obj.set_description(ErrorDescription.INVALID_CITY_ID)
                return error_obj
            else:
                city_list_data = NWisefinList()
                for city in citylist:
                    city_data = CityResponse()
                    city_data.Code=(city.code)
                    city_data.Name=(city.name)
                    city_data.state_id=(city.state_id)
                    status = MasterStatus()
                    if city.status == status.Active:
                        city_data.Status = status.Active_VALUE
                    if city.status == status.Inactive:
                        city_data.Status = status.Inactive_VALUE
                    city_list_data.append(city_data)
                return city_list_data
        except:
            logger.error('ERROR_City_Excel_Download_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_CITY_ID)
            error_obj.set_description(ErrorDescription.INVALID_CITY_ID)
            return error_obj

    def fetch_city(self, city_id, user_id):
        try:
            city = City.objects.using(self._current_app_schema()).get(id=city_id,status=1)
            city_data = CityResponse()
            city_data.set_id(city.id)
            city_data.set_code(city.code)
            city_data.set_name(city.name)
            city_data.set_state(city.state_id)
            return city_data

        except City.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_CITY_ID)
            error_obj.set_description(ErrorDescription.INVALID_CITY_ID)
            return error_obj

    def hrms_get_addresscity(self,cityarr):
        city = City.objects.using(self._current_app_schema()).filter(id__in=cityarr)
        city_list_data = []
        for city_data in city:
            data = CityResponse()
            data.set_id(city_data.id)
            data.set_name(city_data.name)
            city_list_data.append(data)
        return city_list_data

    def delete_city(self, city_id, user_id):
        city = City.objects.using(self._current_app_schema()).filter(id=city_id, entity_id=self._entity_id()).delete()
        self.audit_function(city, user_id, city_id, ModifyStatus.delete)

        if city[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_CITY_ID)
            error_obj.set_description(ErrorDescription.INVALID_CITY_ID)
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
        audit_obj.set_relreftype(MasterRefType.CITY)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)
        return

    def fetch_city_search(self, query, vys_page, state_id):
        if query is None and state_id is None:
            citylist = City.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).order_by(
                'created_date')[
                       vys_page.get_offset():vys_page.get_query_limit()]
        else:
            condition = Q(entity_id=self._entity_id())
            if query is None:
                condition &= Q(state_id=state_id)
            elif state_id is None:
                condition &= Q(name__icontains=query)
            else:
                condition &= Q(name__icontains=query) & Q(state_id=state_id)
            citylist = City.objects.using(self._current_app_schema()).filter(condition).order_by('created_date')[
                       vys_page.get_offset():vys_page.get_query_limit()]

        pincode_serv = PincodeService(self._scope())  # changed
        city_list_data = NWisefinList()
        for city in citylist:
            city_data = CitySearchResponse()
            city_data.set_id(city.id)
            city_data.set_code(city.code)
            city_data.set_name(city.name)
            city_data.set_state(city.state)

            pincode_obj = pincode_serv.get_pincode_by_cityid(city.id)
            if pincode_obj is not None:
                city_data.district = pincode_obj.district
                city_data.pincode = pincode_obj.pincode
            else:
                city_data.pincode = None
                city_data.district = None

            city_list_data.append(city_data)
            vpage = NWisefinPaginator(citylist, vys_page.get_index(), 10)
            city_list_data.set_pagination(vpage)
        return city_list_data
    def fetch_city_search_new(self, query, vys_page, state_id):
        if query is None and state_id is None:
            citylist = City.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).order_by(
                'created_date')[
                       vys_page.get_offset():vys_page.get_query_limit()]
        else:
            condition = Q(entity_id=self._entity_id())
            if query is None:
                condition &= Q(state_id=state_id)
            elif state_id is None:
                condition &= Q(name__icontains=query)
            else:
                condition &= Q(name__icontains=query) & Q(state_id=state_id)
            citylist = City.objects.using(self._current_app_schema()).filter(condition).order_by('created_date')[
                       vys_page.get_offset():vys_page.get_query_limit()]

        pincode_serv = PincodeService(self._scope())
        # state_serv = StateService(self._scope())
        # changed
        city_list_data = NWisefinList()
        for city in citylist:
            city_data = CitySearchResponse()
            city_data.set_id(city.id)
            city_data.set_code(city.code)
            city_data.set_name(city.name)
            city_data.state_id={"id":city.state.id,"name":city.state.name}
            pincode_obj = pincode_serv.get_pincode_by_cityid(city.id)
            if pincode_obj is not None:
                city_data.district = pincode_obj.district
                city_data.pincode = pincode_obj.pincode
            else:
                city_data.pincode = None
                city_data.district = None

            city_list_data.append(city_data)
            vpage = NWisefinPaginator(citylist, vys_page.get_index(), 10)
            city_list_data.set_pagination(vpage)
        return city_list_data

    def fetch_new_city_search(self, query, vys_page, state_id):
        if query is None and state_id is None:
            citylist = Pincode.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).order_by(
                'city__created_date')[
                       vys_page.get_offset():vys_page.get_query_limit()]
        else:
            condition = Q(entity_id=self._entity_id())
            if query is None:
                condition &= Q(city__state_id=state_id)
            elif state_id is None:
                condition &= Q(city__name__icontains=query) | Q(no__icontains=query)
            else:
                condition &= (Q(city__name__icontains=query) | Q(no__icontains=query)) & Q(city__state_id=state_id)
            citylist = Pincode.objects.using(self._current_app_schema()).filter(condition).order_by(
                'city__created_date')[
                       vys_page.get_offset():vys_page.get_query_limit()]

        city_list_data = NWisefinList()
        for i in citylist:
            city_data = CitySearchResponse()
            city_data.set_id(i.city.id)
            city_data.set_code(i.city.code)
            city_data.city_name = i.city.name
            city_data.set_state(i.city.state)
            city_data.pincode = {"id": i.id, "no": i.no}
            city_data.set_district(i.district)
            city_data.set_name(i.city.name + "-" + i.no)

            city_list_data.append(city_data)
            vpage = NWisefinPaginator(citylist, vys_page.get_index(), 10)
            city_list_data.set_pagination(vpage)
        return city_list_data

    def get_city_by_name(self, name,state_id,state_name):
        city_obj = City.objects.filter(name=name,state_id=state_id,status=1).order_by('created_date')
        if len(city_obj ) == 0:
            city = City.objects.create(name=name, state_id=state_id)
            return city.id
        else:
            city=city_obj[0]
            return city.id
            # return None


    def create_city_mtom(self, city_obj,action,user_id):

        if action=='update':
            try:
                state_id = State.objects.using(city_obj._current_app_schema()).get(code=city_obj.get_state_code()).id
                city_update = City.objects.filter(code =city_obj.get_code()).update(code =city_obj.get_code(),
                name  =city_obj.get_name(),state_id =state_id,status =city_obj.get_status(),
                updated_by=user_id,updated_date=timezone.now())
                city = City.objects.get(code =city_obj.get_code())

                city_auditdata = {'id': city.id,
                                  'code': city_obj.get_code(),
                                  'name': city_obj.get_name(),'state_id': state_id,
                                  'updated_date': timezone.now(),
                                  'updated_by': user_id}

                self.audit_function(city_auditdata, user_id, city.id, ModifyStatus.update)

            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except City.DoesNotExist:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_CITY_ID)
                error_obj.set_description(ErrorDescription.INVALID_CITY_ID)
                return error_obj
            except:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        elif action=='create':
            try:
                state_id = State.objects.using(city_obj._current_app_schema()).get(code=city_obj.get_state_code()).id
                city = City.objects.using(city_obj._current_app_schema()).create(code =city_obj.get_code(),
                name  =city_obj.get_name(),state_id =state_id,
                created_by=user_id)

                self.audit_function(city, user_id, city.id, ModifyStatus.create)
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

        city_data = CityResponse()
        city_data.set_id(city.id)
        city_data.set_code(city.code)
        city_data.set_name(city.name)
        city_data.set_state(city.state_id)

        return city_data


    def fetch_cityone(request, city_id):
        state = City.objects.using(request._current_app_schema()).get(id=city_id)
        state_data = {"id": state.id, "code": state.code, "name": state.name}
        return state_data

    def fetch_city_scroll(self, state_id, vys_page, data):
        cityList = City.objects.using(self._current_app_schema()).filter(state__id=state_id, status=1, name__icontains=data).order_by('created_date')[
                       vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(cityList)
        # print(cityList)
        city_list_data = NWisefinList()
        try:
            if list_length <= 0:
                pass
            else:
                for city in cityList:
                    city_data = CityResponse()
                    city_data.set_id(city.id)
                    city_data.set_code(city.code)
                    city_data.set_name(city.name)
                    city_data.set_state(city.state_id)
                    city_list_data.append(city_data)
                vpage = NWisefinPaginator(cityList, vys_page.get_index(), 10)
                city_list_data.set_pagination(vpage)
            return city_list_data

        except City.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_STATE_ID)
            error_obj.set_description(ErrorDescription.INVALID_STATE_ID)
            return error_obj

    def create_sync_city(self,city_name,state_id,Entity):
        city = City.objects.using(self._current_app_schema()).filter(name=city_name)
        if len(city) > 0:
            city_id = city[0].id
            return city_id
        else:
            city = City.objects.using(self._current_app_schema()).create(entity_id=Entity,name=city_name,state_id=state_id)
            rnsl = 0
            new_rnsl = rnsl + 1
            code = "CY" + str(new_rnsl).zfill(5)
            city.code = code
            city.save()
            return city.id
