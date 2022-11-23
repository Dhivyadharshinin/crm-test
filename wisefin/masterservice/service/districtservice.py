import traceback

from django.db import IntegrityError

from masterservice.data.response.cityresponse import CityResponse, CitySearchResponse
from masterservice.data.response.stateresponse import StateResponse
from masterservice.models import District, State, City, Pincode
from masterservice.data.response.districtresponse import DistrictResponse,DistrictSearchResponse
from masterservice.service.Codegenerator import CodeGen
from masterservice.service.pincodeservice import PincodeService
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror  import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage,ErrorDescription
from utilityservice.data.response.nwisefinsuccess  import NWisefinSuccess,SuccessMessage,SuccessStatus
from utilityservice.data.response.nwisefinlist import NWisefinList
from django.utils import timezone
from masterservice.data.request.masterauditrequest import MasterAuditRequest
from masterservice.service.masterauditservice import MasterAuditService
from masterservice.data.response.masterauditresponse import MasterAuditResponse
from masterservice.util.masterutil import ModifyStatus, MasterRefType, RequestStatusUtil, Code_Gen_Type, Code_Gen_Value
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from django.db.models import Q
from masterservice.service.cityservice import CityService
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


class DistrictService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_district(self, Dis_obj, user_id):
        if not Dis_obj.get_id() is None:
            try:
                logger.error('DISTRICT: District Update Started')
                district_update = District.objects.using(self._current_app_schema()).filter(id=Dis_obj.get_id(),
                                                                                            entity_id=self._entity_id()).update(
                    # code=Dis_obj.get_code(),
                    name=Dis_obj.get_name(),
                    state_id=Dis_obj.get_state_id(),
                    updated_by=user_id,
                    updated_date=timezone.now())
                district = District.objects.using(self._current_app_schema()).get(id=Dis_obj.get_id(),
                                                                                  entity_id=self._entity_id())
                logger.error('DISTRICT: District Update Success' + str(district_update))
                district_auditdata = {'id': Dis_obj.get_id(),
                                      # 'code': Dis_obj.get_code(),
                                      'name': Dis_obj.get_name(),
                                      'state_id': Dis_obj.get_state_id(),
                                      'updated_date': timezone.now(),
                                      'updated_by': user_id}
                self.audit_function(district_auditdata, user_id, district.id, ModifyStatus.update)

            except IntegrityError as error:
                logger.error('ERROR_District_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except District.DoesNotExist:
                logger.error('ERROR_District_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_District_ID)
                error_obj.set_description(ErrorDescription.INVALID_District_ID)
                return error_obj
            except:
                logger.error('ERROR_District_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                logger.error('DISTRICT: District Creation Started')
                data_len = District.objects.using(self._current_app_schema()).filter(
                    name=Dis_obj.get_name()).values()
                if (len(data_len) > 0):
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVALID_DATA)
                    error_obj.set_description(ErrorDescription.DUPLICATE_NAME)
                    return error_obj
                district = District.objects.using(self._current_app_schema()).create(  # code=Dis_obj.get_code(),
                    name=Dis_obj.get_name(), state_id=Dis_obj.get_state_id(),
                    created_by=user_id, entity_id=self._entity_id())
                try:
                    max_cat_code = District.objects.using(self._current_app_schema()).filter(code__icontains='DT').order_by('-code')[0].code
                    rnsl = int(max_cat_code[2:])
                except:
                    rnsl = 0
                new_rnsl = rnsl + 1
                code = "DT" + str(new_rnsl).zfill(5)# code = "ISCT" + str(district.id)
                district.code = code
                district.save()
                self.audit_function(district, user_id, district.id, ModifyStatus.create)
                logger.error('DISTRICT: District Creation Success' + str(district))

            except IntegrityError as error:
                logger.error('ERROR_District_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                logger.error('ERROR_District_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        District_data = DistrictResponse()
        District_data.set_id(district.id)
        District_data.set_code(district.code)
        District_data.set_name(district.name)
        District_data.set_status(district.status)
        District_data.set_state_id(district.state_id)
        District_data.set_created_by(district.created_by)
        District_data.set_updated_by(district.updated_by)

        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        return success_obj


    def fetchdistrict(self, district_id):
        try:
            district = District.objects.using(self._current_app_schema()).get(id=district_id,
                                                                              entity_id=self._entity_id())
            District_data = DistrictResponse()
            District_data.set_id(district.id)
            District_data.set_code(district.code)
            District_data.set_name(district.name)
            District_data.set_status(district.status)
            District_data.set_state_id(district.state_id)
            District_data.set_created_by(district.created_by)
            District_data.set_updated_by(district.updated_by)
            return District_data
        except District.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DISTRICT_ID)
            error_obj.set_description(ErrorDescription.INVALID_DISTRICT_ID)
            return error_obj

    def hrms_get_addressdistrict(self,districtarr):
        city = District.objects.using(self._current_app_schema()).filter(id__in=districtarr)
        district_list = []
        for district in city:
            District_data = DistrictResponse()
            District_data.set_id(district.id)
            District_data.set_name(district.name)
            district_list.append(District_data)
        return district_list
    def fetch_district_list(self, vys_page):
        try:
            districtList = District.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).order_by(
                'created_date')[
                           vys_page.get_offset():vys_page.get_query_limit()]
            list_length = len(districtList)
            district_list_data = NWisefinList()
            if list_length <= 0:
                pass
            else:
                for district in districtList:
                    District_data = DistrictResponse()
                    District_data.set_id(district.id)
                    District_data.set_code(district.code)
                    District_data.set_name(district.name)
                    District_data.set_status(district.status)
                    District_data.set_state_id(district.state_id)
                    District_data.set_created_by(district.created_by)
                    District_data.set_updated_by(district.updated_by)
                    district_list_data.append(District_data)
                    vpage = NWisefinPaginator(districtList, vys_page.get_index(), 10)
                    district_list_data.set_pagination(vpage)
            return district_list_data
        except:
            logger.error('ERROR_District_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DISTRICT_ID)
            error_obj.set_description(ErrorDescription.INVALID_DISTRICT_ID)
            return error_obj
    def fetch_district_dowload(self, request):
        try:
            districtList = District.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).order_by(
                'created_date')
            list_length = len(districtList)
            district_list_data = NWisefinList()
            if list_length <= 0:
                pass
            else:
                for district in districtList:
                    District_data = DistrictResponse()
                    # District_data.Id=(district.id)
                    District_data.Code=(district.code)
                    District_data.Name=(district.name)
                    from masterservice.util.masterutil import MasterStatus
                    status=MasterStatus()
                    if district.status == status.Active:
                        District_data.Status = status.Active_VALUE
                    if district.status == status.Inactive:
                        District_data.Status = status.Inactive_VALUE
                    if district.state_id is not None:
                        District_data.state_id = (district.state_id)
                    else:
                        District_data.state_id = None

                    from utilityservice.service.api_service import ApiService
                    # District_data.Created_By=district.created_by
                    # scope=request.scope
                    # empserv=ApiService(scope)
                    # emp=empserv.get_emp_id(request,district.created_by)
                    # if district.state_id is not None:
                    #     emp = empserv.get_emp_id(request, district.created_by)
                    #     District_data.Created_By = emp['full_name']
                    # else:
                    #     District_data.Created_By = None
                    # District_data.Updated_By=(district.updated_by)
                    district_list_data.append(District_data)
                return district_list_data
        except:
            logger.error('ERROR_District_Excel_Download_Download_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DISTRICT_ID)
            error_obj.set_description(ErrorDescription.INVALID_DISTRICT_ID)
            return error_obj

    def delete_district(self, district_id, user_id):
        district = District.objects.using(self._current_app_schema()).filter(id=district_id,
                                                                             entity_id=self._entity_id()).delete()
        self.audit_function(district, user_id, district_id, ModifyStatus.delete)

        if district[0] == 0:
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
        audit_obj.set_relreftype(MasterRefType.DISTRICT)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)
        return

    def fetch_district_search(self, query, vys_page, state_id):
        if query is None and state_id is None:
            districtList = District.objects.using(self._current_app_schema()).filter(
                entity_id=self._entity_id()).order_by('created_date')[
                           vys_page.get_offset():vys_page.get_query_limit()]
        else:
            condition = Q(entity_id=self._entity_id())
            if query is None:
                condition &= Q(state_id=state_id)
            elif state_id is None:
                condition &= Q(name__icontains=query)
            else:
                condition &= Q(name__icontains=query) & Q(state_id=state_id)
            districtList = District.objects.using(self._current_app_schema()).filter(condition).order_by(
                'created_date')[
                           vys_page.get_offset():vys_page.get_query_limit()]
        district_list_data = NWisefinList()
        for district in districtList:
            District_data = DistrictSearchResponse()
            District_data.set_id(district.id)
            District_data.set_code(district.code)
            District_data.set_name(district.name)
            District_data.set_state(district.state)
            district_list_data.append(District_data)
            vpage = NWisefinPaginator(districtList, vys_page.get_index(), 10)
            district_list_data.set_pagination(vpage)
        return district_list_data


    def fetch_district_Common(self,state_id):
        condition = Q(state_id=state_id,status=1)
        districtList = District.objects.using(self._current_app_schema()).filter(condition).order_by('created_date')
        district_list_data = NWisefinList()
        for district in districtList:
            District_data = DistrictSearchResponse()
            District_data.set_id(district.id)
            District_data.set_code(district.code)
            District_data.set_name(district.name)
            District_data.set_state(district.state)
            district_list_data.append(District_data)
        return district_list_data

    def fetch_distrcit_stateid(self, vys_page,state_id):
        condition = Q(state_id=state_id,status=1)
        districtList = District.objects.using(self._current_app_schema()).filter(condition).order_by('created_date')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        district_list_data = NWisefinList()
        for district in districtList:
            District_data = DistrictSearchResponse()
            District_data.set_id(district.id)
            District_data.set_code(district.code)
            District_data.set_name(district.name)
            District_data.set_state(district.state)
            district_list_data.append(District_data)
            vpage = NWisefinPaginator(districtList, vys_page.get_index(), 10)
            district_list_data.set_pagination(vpage)
        return district_list_data

    def get_district_by_name(self, name,state_id,state_name):
        district_obj = District.objects.using(self._current_app_schema()).filter(name=name,state_id=state_id,status=1).order_by('created_date')
        if len(district_obj) == 0:
            district = District.objects.using(self._current_app_schema()).create(name=name, state_id=state_id)
            return district.id
        else:
            district=district_obj[0]
            return district.id
            # return None



    def create_district_mtom(self, Dis_obj,action, user_id):
        state_id = State.objects.using(self._current_app_schema()).get(code=Dis_obj.get_state_code()).id
        if action=='update':
            try:
                district_update = District.objects.using(self._current_app_schema()).filter(code=Dis_obj.get_code()).update(code=Dis_obj.get_code(),
                                                                                 name=Dis_obj.get_name(),
                                                                                 status=Dis_obj.get_status(),
                                                                                 state_id=state_id,
                                                                                 updated_by=user_id,
                                                                                 updated_date=timezone.now())
                district = District.objects.using(self._current_app_schema()).get(code=Dis_obj.get_code())

                district_auditdata = {'id': district.id,
                                         'code': Dis_obj.get_code(),
                                         'name': Dis_obj.get_name(),
                                        'state_id' : state_id,
                                         'updated_date': timezone.now(),
                                         'updated_by': user_id}
                self.audit_function(district_auditdata, user_id, district.id, ModifyStatus.update)

            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except District.DoesNotExist:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_District_ID)
                error_obj.set_description(ErrorDescription.INVALID_District_ID)
                return error_obj
            except:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj

        elif action=='create':
            try:
                district = District.objects.using(self._current_app_schema()).create(code=Dis_obj.get_code(),
                                                   name=Dis_obj.get_name(),state_id=state_id,
                                                   created_by=user_id)

                self.audit_function(district, user_id, district.id, ModifyStatus.create)

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
        District_data = DistrictResponse()
        District_data.set_id(district.id)
        District_data.set_code(district.code)
        District_data.set_name(district.name)
        District_data.set_status(district.status)
        District_data.set_state_id(district.state_id)
        District_data.set_created_by(district.created_by)
        District_data.set_updated_by(district.updated_by)

        return District_data


    def fetch_city_Common(self,state_id):
        condition = Q(state_id=state_id,status=1)
        citylist = City.objects.using(self._current_app_schema()).filter(condition).order_by('created_date')
        pincode_serv =PincodeService(self._scope())
        city_list_data = NWisefinList()
        for city in citylist:
            city_data = CitySearchResponse()
            city_data.set_id(city.id)
            city_data.set_code(city.code)
            city_data.set_name(city.name)
            city_data.set_state(city.state)

            pincode_obj=pincode_serv.get_pincode_by_cityid(city.id)
            if pincode_obj is not None:
                city_data.district = pincode_obj.district
                city_data.pincode = pincode_obj.pincode
            else:
                city_data.pincode = None
                city_data.district = None

            city_list_data.append(city_data)
        return city_list_data

    def fetch_city_state(self,vys_page,state_id):
        condition = Q(district_id=state_id,status=1)
        citylist = Pincode.objects.using(self._current_app_schema()).filter(condition).order_by('created_date')[
                    vys_page.get_offset():vys_page.get_query_limit()]

        pincode_serv =PincodeService(self._scope())
        city_list_data = NWisefinList()
        for city in citylist:
            print(city)
            d=City.objects.using(self._current_app_schema()).get(id=city.city_id)
            e=District.objects.using(self._current_app_schema()).get(id=city.district_id)
            f=State.objects.using(self._current_app_schema()).get(id=e.state_id)

            city_data = CitySearchResponse()
            city_data.set_id(d.id)
            city_data.set_code(d.code)
            city_data.set_name(d.name)
            city_data.district=e.name
            city_data.no=city.no
            city_data.statename=f.name
            # city_data.set_state(city.state)
            # city_data.set_state(city.id)+

            # pincode_obj=pincode_serv.get_pincode_by_cityid(city.id)
            # if pincode_obj is not None:
            #     city_data.district = pincode_obj.district
            #     city_data.pincode = pincode_obj.pincode
            # else:
            #     city_data.pincode = None
            #     city_data.district = None

            city_list_data.append(city_data)
            vpage = NWisefinPaginator(citylist, vys_page.get_index(), 10)
            city_list_data.set_pagination(vpage)
        return city_list_data


    def fetch_state_district_city(self,vys_page):
        stateList = State.objects.using(self._current_app_schema()).filter(status=1).order_by('created_date')[
                    vys_page.get_offset():vys_page.get_query_limit()]
        # districtList = District.objects.filter(state_id=stateList.id).order_by('created_date')[
        #                  vys_page.get_offset():vys_page.get_query_limit()]
        # citylist = City.objects.filter(state_id=stateList.id).order_by('created_date')[
        #                  vys_page.get_offset():vys_page.get_query_limit()]

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
                State_data.set_district(self.fetch_district_Common(state.id))
                State_data.set_city(self.fetch_city_Common(state.id))
                state_list_data.append(State_data)
                vpage = NWisefinPaginator(stateList, vys_page.get_index(), 10)
                state_list_data.set_pagination(vpage)
        return state_list_data

    def fetch_district_scroll_list(self,state_id,vys_page,data):
        districtList = District.objects.using(self._current_app_schema()).filter(state__id=state_id, status=1, name__icontains=data).order_by('created_date')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(districtList)
        district_list_data = NWisefinList()
        try:
            if list_length <= 0:
                pass
            else:
                for district in districtList:
                    District_data = DistrictResponse()
                    District_data.set_id(district.id)
                    District_data.set_code(district.code)
                    District_data.set_name(district.name)
                    District_data.set_status(district.status)
                    District_data.set_state_id(district.state_id)
                    District_data.set_created_by(district.created_by)
                    District_data.set_updated_by(district.updated_by)
                    district_list_data.append(District_data)
                vpage = NWisefinPaginator(districtList, vys_page.get_index(), 10)
                district_list_data.set_pagination(vpage)
            return district_list_data

        except District.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DISTRICT_ID)
            error_obj.set_description(ErrorDescription.INVALID_DISTRICT_ID)
            return error_obj


    def create_sync_district(self,district_name,state_id,Entity):
        dt = District.objects.using(self._current_app_schema()).filter(name=district_name)
        if len(dt) > 0:
            dt_id = dt[0].id
            return dt_id
        else:
            dt = District.objects.using(self._current_app_schema()).create(entity_id=Entity,name=district_name,state_id=state_id)
            rnsl = 0
            new_rnsl = rnsl + 1
            code = "DT" + str(new_rnsl).zfill(5)
            dt.code = code
            dt.save()
            return dt.id