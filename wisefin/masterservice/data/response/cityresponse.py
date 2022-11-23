import json
from masterservice.data.response.stateresponse import StateResponse
from masterservice.data.response.districtresponse import DistrictResponse

class CityResponse:
    id = None
    code = None
    name = None
    pin_id=None
    state_id=None
    city= None
    district_id=None
    district=None
    no=None
    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
    def get_district(self):
        return self.district

    def get_city(self):
        return self.id
    def get_no(self):
        return self.no
    def set_id(self, id):
        self.id = id
    def get_id(self):
        return self.pin_id

    def set_code(self, code):
        self.code = code

    def set_name(self, name):
        self.name = name

    def set_state(self, state):
        self.state_id = state
    def set_district_id(self, district_id):
        self.district_id = district_id

    def set_city(self, city):
        self.city = city

class CitySearchResponse:
    id = None
    code = None
    name = None
    state = None
    district =None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_code(self, code):
        self.code = code

    def set_name(self, name):
        self.name = name

    def set_state(self, state):
        State_data = StateResponse()
        State_data.set_id(state.id)
        State_data.set_code(state.code)
        State_data.set_name(state.name)
        self.state = State_data

    def set_district(self, district):
        District_data = DistrictResponse()
        District_data.set_id(district.id)
        District_data.set_code(district.code)
        District_data.set_name(district.name)
        self.district = District_data
