import json
from masterservice.data.response.stateresponse import StateResponse
from masterservice.data.response.districtresponse import DistrictResponse
from masterservice.data.response.cityresponse import CityResponse


class PincodeResponse:
    id = None
    district = None
    city = None
    no = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_district(self, district):
        self.district_id = district

    def set_city(self, city):
        self.city_id = city

    def set_no(self, no):
        self.no = no

class PincodeSearchResponse:
    id = None
    district = None
    city = None
    state =None
    no = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_district(self, district):
        District_data = DistrictResponse()
        District_data.set_id(district.id)
        District_data.set_code(district.code)
        District_data.set_name(district.name)
        self.district = District_data
        State_data = StateResponse()
        state = district.state
        State_data.set_id(state.id)
        State_data.set_code(state.code)
        State_data.set_name(state.name)
        self.state = State_data

    def set_state(self,state):

        State_data = StateResponse()
        state = state.state
        State_data.set_id(state.id)
        State_data.set_code(state.code)
        State_data.set_name(state.name)
        self.state = State_data
    def set_cdistrict(self,district):
        District_data = DistrictResponse()
        District_data.set_id(district.id)
        District_data.set_code(district.code)
        District_data.set_name(district.name)
        self.district = District_data


    def set_city(self, city):
        city_data = CityResponse()
        city_data.set_id(city.id)
        city_data.set_code(city.code)
        city_data.set_name(city.name)
        self.city = city_data


    def set_no(self, no):
        self.no = no
    def set_newpi(self,no,city,district):
        self.no=no +'--'+ city.name+'--'+district.name