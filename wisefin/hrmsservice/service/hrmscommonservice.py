from django.utils import timezone
from hrmsservice.models import HrmsAddress
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from hrmsservice.data.response.employeedetailsresponse import AddressResponse
from masterservice.service.stateservice import StateService
from masterservice.service.cityservice import CityService
from masterservice.service.pincodeservice import PincodeService
from masterservice.service.districtservice import DistrictService
from utilityservice.data.response.nwisefinlist import NWisefinList
class HrmsCommonService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.HRMS_SERVICE)

    def create_hrmsaddress(self, address_obj, user_id):
        if not address_obj.get_id() is None:
            address_update = HrmsAddress.objects.using(self._current_app_schema()).filter(id=address_obj.get_id(),
                                                                                      entity_id=self._entity_id()).update(
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

        else:
            address_create = HrmsAddress.objects.using(self._current_app_schema()).create(
                line1=address_obj.get_line1(),
                line2=address_obj.get_line2(),
                line3=address_obj.get_line3(),
                pincode_id=address_obj.get_pincode_id(),
                city_id=address_obj.get_city_id(),
                district_id=address_obj.get_district_id(),
                state_id=address_obj.get_state_id(),
                created_by=user_id,
                entity_id=self._entity_id())
            addressid = address_create.id
            return addressid

    def address_get(self, addressarr):
        dataaddress = HrmsAddress.objects.using(self._current_app_schema()).filter(id__in=addressarr)
        pincodearr = [adddata.pincode_id for adddata in dataaddress]
        pincodedata = PincodeService(self._scope()).hrms_get_addresspincode(pincodearr)
        cityarr = [adddata.city_id for adddata in dataaddress]
        citydata = CityService(self._scope()).hrms_get_addresscity(cityarr)
        districtarr = [adddata.district_id for adddata in dataaddress]
        districtdata = DistrictService(self._scope()).hrms_get_addressdistrict(districtarr)
        statearr = [adddata.state_id for adddata in dataaddress]
        statedata = StateService(self._scope()).hrms_get_addressstate(statearr)
        list_dataaddress = []
        for adddata in dataaddress:
            data = AddressResponse()
            data.set_id(adddata.id)
            data.set_line1(adddata.line1)
            data.set_line2(adddata.line2)
            data.set_line3(adddata.line3)
            data.set_pincode(adddata.pincode_id, pincodedata)
            data.set_city(adddata.city_id, citydata)
            data.set_district(adddata.district_id, districtdata)
            data.set_state(adddata.state_id, statedata)
            list_dataaddress.append(data)
        return list_dataaddress

