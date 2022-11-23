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
    portal_flag = 0

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

    def get_id(self):
        return self.id

    def get_line1(self):
        return self.line1

    def get_line2(self):
        return self.line2

    def get_line3(self):
        return self.line3

    def get_pincode_id(self):
        return self.pincode_id

    def get_city_id(self):
        return self.city_id

    def get_district_id(self):
        return self.district_id

    def get_state_id(self):
        return self.state_id

    def set_portal_flag(self, portal_flag):
        self.portal_flag = portal_flag

    def get_portal_flag(self):
        return self.portal_flag
