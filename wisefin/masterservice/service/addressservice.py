import traceback

from masterservice.models import Address
from masterservice.data.response.addressresponse import AddressResponse,MasterAddressResponse
from django.db import IntegrityError

from masterservice.service.cityservice import CityService
from masterservice.service.districtservice import DistrictService
from masterservice.service.pincodeservice import PincodeService
from masterservice.service.stateservice import StateService
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror  import NWisefinError
from utilityservice.data.response.nwisefinsuccess  import NWisefinSuccess,SuccessMessage,SuccessStatus
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage,ErrorDescription
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from django.utils import timezone
from masterservice.data.request.masterauditrequest import MasterAuditRequest
from masterservice.service.masterauditservice import MasterAuditService
from masterservice.data.response.masterauditresponse import MasterAuditResponse
from masterservice.util.masterutil import ModifyStatus,MasterRefType,RequestStatusUtil
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


class AddressService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_address(self, address_obj, user_id):
        if not address_obj.get_id() is None:
            try:
                logger.error('ADDRESS: Address Update Started')
                address_update = Address.objects.using(self._current_app_schema()).filter(id=address_obj.get_id(), entity_id=self._entity_id()).update(
                line1=address_obj.get_line1(),
                line2=address_obj.get_line2(),
                line3=address_obj.get_line3(),
                pincode_id=address_obj.get_pincode_id(),
                city_id=address_obj.get_city_id(),
                district_id=address_obj.get_district_id(),
                state_id=address_obj.get_state_id(),
                updated_by=user_id,
                updated_date=timezone.now(),
                entity_id=self._entity_id())
                logger.error('ADDRESS: Address Update Success' + str(address_update))

                address = Address.objects.using(self._current_app_schema()).get(id=address_obj.get_id(),entity_id=self._entity_id())

                address_auditdata = {'id': address_obj.get_id(), 'line1': address_obj.get_line1(),
                                     'line2': address_obj.get_line2(),
                                     'line3': address_obj.get_line3(), 'pincode_id': address_obj.get_pincode_id(),
                                     'city_id': address_obj.get_city_id(),'district_id': address_obj.get_district_id(),
                                     'state_id':address_obj.get_state_id(),
                                     'updated_by': user_id, 'updated_date': timezone.now()}
                self.audit_function(address_auditdata, user_id, address.id, ModifyStatus.update)

            except IntegrityError as error:
                logger.error('ERROR_Address_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except Address.DoesNotExist:
                logger.error('ERROR_Address_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_Address_ID)
                error_obj.set_description(ErrorDescription.INVALID_Address_ID)
                return error_obj
            except:
                logger.error('ERROR_Address_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                logger.error('ADDRESS: Address Creation Started')
                address = Address.objects.using(self._current_app_schema()).create(line1=address_obj.get_line1(),
                                                          line2=address_obj.get_line2(), line3=address_obj.get_line3(),
                                                          pincode_id=address_obj.get_pincode_id(),
                                                          city_id=address_obj.get_city_id(),
                                                          district_id=address_obj.get_district_id(),
                                                          state_id=address_obj.get_state_id(),
                                                          created_by=user_id,
                                                 entity_id=self._entity_id())
                logger.error('ADDRESS: Address Creation Success' + str(address))
                self.audit_function(address, user_id, address.id, ModifyStatus.create)

            except IntegrityError as error:
                logger.error('ERROR_Address_create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                logger.error('ERROR_Address_create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj

        add_data = AddressResponse()
        add_data.set_id(address.id)
        add_data.set_line1(address.line1)
        add_data.set_line2(address.line2)
        add_data.set_line3(address.line3)
        add_data.set_pincode_id(address.pincode_id)
        add_data.set_city_id(address.city_id)
        add_data.set_district_id(address.district_id)
        add_data.set_state_id(address.state_id)
        return add_data.id

    def fetch_address_list(self,user_id):
        addresslist = Address.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id())
        list_length = len(addresslist)
        if list_length <= 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_Address_ID)
            error_obj.set_description(ErrorDescription.INVALID_Address_ID)
            return error_obj
        else:
            add_list_data = NWisefinList()
            for address in addresslist:
                add_data = AddressResponse()
                add_data.set_id(address.id)
                add_data.set_line1(address.line1)
                add_data.set_line2(address.line2)
                add_data.set_line3(address.line3)
                add_data.set_pincode_id(address.pincode_id)
                add_data.set_city_id(address.city_id)
                add_data.set_district_id(address.district_id)
                add_data.set_state_id(address.state_id)

                add_list_data.append(add_data)
            return add_list_data

    def fetch_address(self,address_id,user_id):
        try:
            address = Address.objects.using(self._current_app_schema()).get(id=address_id, entity_id=self._entity_id())
            add_data = AddressResponse()
            pincode_serv=PincodeService(self._scope())    # changed
            city_serv=CityService(self._scope())    # changed
            distic_serv=DistrictService(self._scope())    # changed
            state_serv=StateService(self._scope())    # changed

            add_data.set_id(address.id)
            add_data.set_line1(address.line1)
            add_data.set_line2(address.line2)
            add_data.set_line3(address.line3)
            add_data.set_pincode_id(pincode_serv.fetch_pincode(address.pincode_id,address.created_by))
            add_data.set_city_id(city_serv.fetch_city(address.city_id,address.created_by))
            add_data.set_district_id(distic_serv.fetchdistrict(address.district_id))
            add_data.set_state_id(state_serv.fetchstate(address.state_id))

            return add_data
        except Address.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_Address_ID)
            error_obj.set_description(ErrorDescription.INVALID_Address_ID)
            return error_obj

    def fetch_master_address(self,address):
        add_data = MasterAddressResponse()
        add_data.set_id(address.id)
        add_data.set_line1(address.line1)
        add_data.set_line2(address.line2)
        add_data.set_line3(address.line3)
        add_data.set_pincode(address.pincode)
        add_data.set_city(address.city)
        add_data.set_district(address.district)
        add_data.set_state(address.state)
        return add_data

    def delete_address(self, address_id,user_id):
        address = Address.objects.using(self._current_app_schema()).filter(id=address_id, entity_id=self._entity_id()).delete()
        self.audit_function(address, user_id, address_id, ModifyStatus.delete)

        if address[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_Address_ID)
            error_obj.set_description(ErrorDescription.INVALID_Address_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

    def audit_function(self,data_obj,user_id,id,action):
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
        audit_obj.set_relreftype(MasterRefType.ADDRESS)
        audit_obj.set_action(action)
        audit_obj.set_data(data)
        audit_service.create_audit(audit_obj)
        return
