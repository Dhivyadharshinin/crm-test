import json
import datetime


class AddressResponse:
    id = None
    line1 = None
    line2 = None
    line3 = None
    pincode_id = None
    city_id = None
    district_id = None
    state_id = None

    def get(self):
      return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_line1(self, line1):
        self.line1 = line1

    def set_line2(self, line2):
        self.line2 = line2

    def set_line3(self, line3):
        self.line3 = line3

    def set_pincode_id(self, pincode_id):
        self.pincode_id = pincode_id

    def set_city_id(self, city_id):
        self.city_id = city_id

    def set_district_id(self, district_id):
        self.district_id = district_id

    def set_state_id(self, state_id):
        self.state_id = state_id


class MasterAddressResponse:
    id = None
    line1 = None
    line2 = None
    line3 = None
    pincode = None
    city = None
    district = None
    state = None

    def get(self):
      return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_line1(self, line1):
        self.line1 = line1

    def set_line2(self, line2):
        self.line2 = line2

    def set_line3(self, line3):
        self.line3 = line3

    def set_pincode(self, pincode):
        self.pincode=None
        if pincode is not None:
            self.pincode = {"no":pincode.no}


    def set_city(self, city):
        self.city = None
        if city is not None:
            self.city = {"name": city.name,"code":city.code}

    def set_district(self, district):
        self.district = None
        if district is not None:
            self.district = {"name": district.name, "code": district.code}

    def set_state(self, state):
        self.state = None
        if state is not None:
            self.state = {"name": state.name, "code": state.code}
