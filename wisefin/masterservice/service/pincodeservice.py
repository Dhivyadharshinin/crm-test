import json
import traceback

import pandas as pd
from django.db import IntegrityError


from masterservice.models import Pincode, City, District,State,Country

from masterservice.data.response.pincoderesponse import PincodeResponse,PincodeSearchResponse
from utilityservice.data.response.nwisefinerror  import NWisefinError
from utilityservice.data.response.nwisefinsuccess  import NWisefinSuccess,SuccessMessage,SuccessStatus
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage,ErrorDescription
from django.utils import timezone
from masterservice.data.request.masterauditrequest import MasterAuditRequest
from masterservice.service.masterauditservice import MasterAuditService
from masterservice.data.response.masterauditresponse import MasterAuditResponse
from masterservice.util.masterutil import ModifyStatus, MasterRefType, RequestStatusUtil, MasterStatus
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.data.response.nwisefinlist import NWisefinList
from nwisefin.settings import logger
from django.db.models.query import Q

from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


class PincodeService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def fetch_pincode_number(self, search, user_id):
        try:
            pincode = Pincode.objects.using(self._current_app_schema()).get(no=search, entity_id=self._entity_id())
            pincode_data = PincodeResponse()
            pincode_data.set_id(pincode.id)
            pincode_data.set_district(pincode.district_id)
            pincode_data.set_city(pincode.city_id)
            pincode_data.set_no(pincode.no)
            return pincode_data

        except Pincode.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_PINCODE_ID)
            error_obj.set_description(ErrorDescription.INVALID_PINCODE_ID)
            return error_obj

    def fetch_pincode_city(self, query, vys_page):
        # try:
        if query == '':
            pincodelist = City.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).order_by(
                'created_date')[
                          vys_page.get_offset():vys_page.get_query_limit()]
        else:
            pincodelist = list(City.objects.using(self._current_app_schema()).filter(name__icontains=query,
                                                                                     entity_id=self._entity_id()).order_by(
                'created_date')[
                               vys_page.get_offset():vys_page.get_query_limit()].values_list('id', flat=True))
        pincode_list_data = NWisefinList()
        pin = Pincode.objects.using(self._current_app_schema()).filter(city_id__in=pincodelist,
                                                                       entity_id=self._entity_id())
        # pincode_serv = PincodeService()
        for pincode in pin:
            pincode_data = PincodeSearchResponse()
            pincode_data.set_id(pincode.id)
            pincode_data.set_district(pincode.district)
            pincode_data.set_city(pincode.city)
            pincode_data.set_newpi(pincode.no, pincode.city, pincode.district)
            pincode_list_data.append(pincode_data)
            vpage = NWisefinPaginator(pincodelist, vys_page.get_index(), 10)
            pincode_list_data.set_pagination(vpage)

        return pincode_list_data

    #
    # except Pincode.DoesNotExist:
    #     error_obj = Error()
    #     error_obj.set_code(ErrorMessage.INVALID_PINCODE_ID)
    #     error_obj.set_description(ErrorDescription.INVALID_PINCODE_ID)
    #     return error_obj
    def create_pincode(self, pincode_obj, user_id):
        if not pincode_obj.get_id() is None:
            try:
                # data_len = Pincode.objects.using(self._current_app_schema()).filter(
                #     no=pincode_obj.get_no()).values()
                # if (len(data_len) > 0):
                #     error_obj = NWisefinError()
                #     error_obj.set_code(ErrorMessage.INVALID_DATA)
                #     error_obj.set_description(ErrorDescription.DUPLICATE_NAME)
                #     return error_obj
                logger.error('PINCODE: Pincode Update Started')
                pincode_update = Pincode.objects.using(self._current_app_schema()).filter(id=pincode_obj.get_id(),
                                                                                          entity_id=self._entity_id()).update(
                    district_id=pincode_obj.get_district(),
                    city_id=pincode_obj.get_city(), no=pincode_obj.get_no(),
                    updated_by=user_id, updated_date=timezone.now())

                pincode = Pincode.objects.using(self._current_app_schema()).get(id=pincode_obj.get_id(),
                                                                                entity_id=self._entity_id())
                pincode_auditdata = {'id': pincode_obj.get_id(), 'district_id': pincode_obj.get_district(),
                                     'city_id': pincode_obj.get_city(), 'no': pincode_obj.get_no(),
                                     'updated_by': user_id, 'updated_date': timezone.now()}
                logger.error('PINCODE: Pincode Update Success' + str(pincode_update))
                self.audit_function(pincode_auditdata, user_id, pincode.id, ModifyStatus.update)

            except IntegrityError as error:
                logger.error('ERROR_Pincode_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except Pincode.DoesNotExist:
                logger.error('ERROR_Pincode_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_PINCODE_ID)
                error_obj.set_description(ErrorDescription.INVALID_PINCODE_ID)
                return error_obj
            except:
                logger.error('ERROR_Pincode_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                # data_len = Pincode.objects.using(self._current_app_schema()).filter(
                #     no=pincode_obj.get_no()).values()
                # if (len(data_len) > 0):
                #     error_obj = NWisefinError()
                #     error_obj.set_code(ErrorMessage.INVALID_DATA)
                #     error_obj.set_description(ErrorDescription.DUPLICATE_NAME)
                #     return error_obj
                logger.error('PINCODE: Pincode Creation Started')
                pincode = Pincode.objects.using(self._current_app_schema()).create(
                    district_id=pincode_obj.get_district(),
                    city_id=pincode_obj.get_city(), no=pincode_obj.get_no(),
                    created_by=user_id, entity_id=self._entity_id())
                self.audit_function(pincode, user_id, pincode.id, ModifyStatus.create)
                logger.error('PINCODE: Pincode Creation Success' + str(pincode))

            except IntegrityError as error:
                logger.error('ERROR_Pincode_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                logger.error('ERROR_Pincode_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj

        pincode_data = PincodeResponse()
        pincode_data.set_id(pincode.id)
        pincode_data.set_district(pincode.district_id)
        pincode_data.set_city(pincode.city_id)
        pincode_data.set_no(pincode.no)

        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj

    def fetch_pincode_list(self, user_id, vys_page):
        try:
            pincodelist = Pincode.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).order_by(
                'created_date')[
                          vys_page.get_offset():vys_page.get_query_limit()]
            list_length = len(pincodelist)
            if list_length <= 0:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_PINCODE_ID)
                error_obj.set_description(ErrorDescription.INVALID_PINCODE_ID)
                return error_obj
            else:
                pincode_list_data = NWisefinList()
                for pincode in pincodelist:
                    pincode_data = PincodeResponse()
                    pincode_data.set_id(pincode.id)
                    pincode_data.set_district(pincode.district_id)
                    pincode_data.set_city(pincode.city_id)
                    pincode_data.set_no(pincode.no)
                    pincode_list_data.append(pincode_data)
                    vpage = NWisefinPaginator(pincodelist, vys_page.get_index(), 10)
                    pincode_list_data.set_pagination(vpage)
                return pincode_list_data
        except:
            logger.error('ERROR_Pincode_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_PINCODE_ID)
            error_obj.set_description(ErrorDescription.INVALID_PINCODE_ID)
            return error_obj
    def fetch_pincode_download(self, user_id):
        try:
            pincodelist = Pincode.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).order_by(
                'created_date')
            list_length = len(pincodelist)
            if list_length <= 0:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_PINCODE_ID)
                error_obj.set_description(ErrorDescription.INVALID_PINCODE_ID)
                return error_obj
            else:
                pincode_list_data = NWisefinList()
                for pincode in pincodelist:
                    pincode_data = PincodeResponse()
                    pincode_data.district_id=(pincode.district_id)
                    pincode_data.city_id=(pincode.city_id)
                    pincode_data.Pincode=(pincode.no)
                    status = MasterStatus()
                    if pincode.status == status.Active:
                        pincode_data.Status = status.Active_VALUE
                    if pincode.status == status.Inactive:
                        pincode_data.Status = status.Inactive_VALUE
                    pincode_list_data.append(pincode_data)
                return pincode_list_data
        except:
            logger.error('ERROR_Pincode_Excel_Download_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_PINCODE_ID)
            error_obj.set_description(ErrorDescription.INVALID_PINCODE_ID)
            return error_obj

    def fetch_pincode(self, pincode_id, user_id):
        try:
            pincode = Pincode.objects.using(self._current_app_schema()).get(id=pincode_id, entity_id=self._entity_id())
            pincode_data = PincodeResponse()
            pincode_data.set_id(pincode.id)
            pincode_data.set_district(pincode.district_id)
            pincode_data.set_city(pincode.city_id)
            pincode_data.set_no(pincode.no)
            return pincode_data

        except Pincode.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_PINCODE_ID)
            error_obj.set_description(ErrorDescription.INVALID_PINCODE_ID)
            return error_obj

    def hrms_get_addresspincode(self,arr):
        pincode = Pincode.objects.using(self._current_app_schema()).filter(id__in=arr)
        pincodelist = []
        for data in pincode:
            pincode_data = PincodeResponse()
            pincode_data.set_id(data.id)
            pincode_data.set_no(data.no)
            pincodelist.append(pincode_data)
        return pincodelist

    def delete_pincode(self, pincode_id, user_id):
        pincode = Pincode.objects.using(self._current_app_schema()).filter(id=pincode_id,
                                                                           entity_id=self._entity_id()).delete()
        self.audit_function(pincode, user_id, pincode_id, ModifyStatus.delete)

        if pincode[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_PINCODE_ID)
            error_obj.set_description(ErrorDescription.INVALID_PINCODE_ID)
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
        audit_obj.set_relreftype(MasterRefType.PINCODE)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)
        return

    def fetch_pincode_search(self, query, vys_page):
        if query is None:
            pincodelist = Pincode.objects.using(self._current_app_schema()).filter(
                entity_id=self._entity_id()).order_by('created_date')[
                          vys_page.get_offset():vys_page.get_query_limit()]
        else:
            pincodelist = Pincode.objects.using(self._current_app_schema()).filter(no__icontains=query,
                                                                                   entity_id=self._entity_id()).order_by(
                'created_date')[
                          vys_page.get_offset():vys_page.get_query_limit()]

        pincode_list_data = NWisefinList()
        for pincode in pincodelist:
            pincode_data = PincodeSearchResponse()
            pincode_data.set_id(pincode.id)
            pincode_data.set_district(pincode.district)
            pincode_data.set_city(pincode.city)
            pincode_data.set_newpi(pincode.no, pincode.city, pincode.district)
            pincode_list_data.append(pincode_data)
            vpage = NWisefinPaginator(pincodelist, vys_page.get_index(), 10)
            pincode_list_data.set_pagination(vpage)
        return pincode_list_data

    def get_pincode_by_cityid(self, city_id):
        try:
            pincode = Pincode.objects.using(self._current_app_schema()).get(city_id=city_id,
                                                                            entity_id=self._entity_id())
            pincode_data = PincodeSearchResponse()
            pincode_data.set_district(pincode.district)
            pcd = {"id": pincode.id, "no": pincode.no}
            pincode_data.pincode = pcd
            return pincode_data
        except:
            return None

    #  new function  to get pincode by city id
    def fetch_pincode_by_cityid(self, city_id):
        arr = []
        pincode_obj = Pincode.objects.using(self._current_app_schema()).filter(city_id=city_id,
                                                                               entity_id=self._entity_id())
        for pincode in pincode_obj:
            pincode_data = PincodeSearchResponse()
            pincode_data.set_district(pincode.district)
            pcd = {"id": pincode.id, "no": pincode.no}
            pincode_data.pincode = pcd
            arr.append(pincode_data)
        return arr

    def get_pincode_by_no(self,no,district_id,city_id,district,city):
        no = int(no)
        pincode_obj = Pincode.objects.using(self._current_app_schema()).filter(no=no,district_id=district_id,city_id=city_id,status=1).order_by('created_date')

        if len(pincode_obj) == 0:
                pincode = Pincode.objects.using(self._current_app_schema()).create(no=no, city_id=city_id, district_id=district_id)
                return pincode.id
        else:
            pincode = pincode_obj[0]
            return pincode.id

    def create_pincode_mtom(self, pincode_obj,action,user_id):
        try:
            state_id = State.objects.using(self._current_app_schema()).filter(code=pincode_obj.get_state_code())[0].id
            city_id = City.objects.using(self._current_app_schema()).filter(code=pincode_obj.get_city_code(),state_id=state_id)[0].id
            district_id = District.objects.using(self._current_app_schema()).filter(code=pincode_obj.get_district_code(),state_id=state_id)[0].id
            logger.error(str(pincode_obj.get_city_code()))
            logger.error(str(pincode_obj.get_district_code()))
            logger.error(str(city_id))
            logger.error(str(district_id))
        except Exception  as excep:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj

        if action=='update':
            try:
                pincode_update = Pincode.objects.using(self._current_app_schema()).filter(id=pincode_obj.get_id(),
                                                                                          entity_id=self._entity_id()).update(
                    district_id=district_id,
                    city_id=city_id, no=pincode_obj.get_no(),
                    updated_by=user_id, updated_date=timezone.now())

                pincode = Pincode.objects.using(self._current_app_schema()).get(id=pincode_obj.get_id(),
                                                                                entity_id=self._entity_id())
                pincode_auditdata = {'id': pincode_obj.get_id(), 'district_id': district_id,
                                     'city_id': city_id, 'no': pincode_obj.get_no(),
                                     'updated_by': user_id, 'updated_date': timezone.now()}
                self.audit_function(pincode_auditdata, user_id, pincode.id, ModifyStatus.update)

            except IntegrityError as error:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except Pincode.DoesNotExist:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_PINCODE_ID)
                error_obj.set_description(ErrorDescription.INVALID_PINCODE_ID)
                return error_obj
            except:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj

        elif action=='create':
            try:
                pincode = Pincode.objects.using(self._current_app_schema()).create(district_id=district_id,
                                                                                   city_id=city_id,
                                                                                   no=pincode_obj.get_no(),
                                                                                   created_by=user_id,
                                                                                   entity_id=self._entity_id())
                self.audit_function(pincode, user_id, pincode.id, ModifyStatus.create)

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

        pincode_data = PincodeResponse()
        pincode_data.set_id(pincode.id)
        pincode_data.set_district(pincode.district_id)
        pincode_data.set_city(pincode.city_id)
        pincode_data.set_no(pincode.no)

        return pincode_data

    def fetch_pincodeone(request, pincode_id, city_id):
        state = Pincode.objects.using(request._current_app_schema()).get(id=pincode_id, city=city_id,
                                                                         entity_id=request._entity_id())
        state_data = {"id": state.id, "code": state.code, "name": state.name}
        return state_data

    def fetch_pincode_state(self,request, data):
        condition=Q(status=1)
        if 'state_id' in data:
            district=District.objects.using(self._current_app_schema()).filter(state_id=data['state_id'])[0]
            condition&=Q(district_id=district.id)
        pincode = Pincode.objects.using(self._current_app_schema()).filter(condition)[0]
        out={
            "no":pincode.no
        }
        return out

    def create_sync_pincode(self,pincde_no,city_id,district_id,Entity):
        pcde = Pincode.objects.using(self._current_app_schema()).filter(no=pincde_no)
        if len(pcde) > 0:
            pcde_id = pcde[0].id
            return pcde_id
        else:
            pcde = Pincode.objects.using(self._current_app_schema()).create(entity_id=Entity,no=pincde_no,city_id=city_id,district_id=district_id)
            return pcde.id

    def pincode_dataframe(self,user_id):
        resp_obj = self.fetch_pincode_download(user_id)
        data = json.loads(resp_obj.get())
        df1 = pd.DataFrame(data['data'])
        # print(df1['city_id'])
        city = City.objects.using(self._current_app_schema()).filter(id__in=df1['city_id'])
        df2 = pd.DataFrame(city.values('id','name')).rename(
            columns={'id': 'city1_id','name':'City_Name'})
        district = District.objects.using(self._current_app_schema()).filter(id__in=df1['district_id'])
        df3 = pd.DataFrame(district.values('id', 'name','state_id')).rename(
            columns={'id': 'district1_id','name':'District_Name'})
        state = State.objects.using(self._current_app_schema()).filter(id__in=df3['state_id'])
        df4 = pd.DataFrame(state.values('id', 'name','country_id')).rename(
            columns={'id': 'state1_id','name':'State_Name'})
        coutry = Country.objects.using(self._current_app_schema()).filter(id__in=df4['country_id'])
        df5 = pd.DataFrame(coutry.values('id', 'name')).rename(
            columns={'id': 'country1_id','name':'Country_Name'})
        pincode = pd.merge(df1, df2, how='outer', left_on=['city_id'], right_on=['city1_id'])
        district = pd.merge(pincode, df3, how='outer', left_on=['district_id'], right_on=['district1_id'])
        state = pd.merge(district, df4, how='outer', left_on=['state_id'], right_on=['state1_id'])
        country = pd.merge(state, df5, how='outer', left_on=['country_id'], right_on=['country1_id'])
        reset_column=country.reset_index().drop(columns=['city1_id', 'district1_id', 'state1_id', 'country1_id','index'])
        return reset_column