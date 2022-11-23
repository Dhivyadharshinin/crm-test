import json

class AddressRequest:
    id = None
    line1 = None
    line2 = None
    line3 = None
    pincode_id = None
    city_id = None
    district_id = None
    state_id = None
    portal_flag = 0

    def __init__(self, address_obj):
        if 'id' in address_obj:
            self.id = address_obj['id']
        if 'line1' in address_obj:
            self.line1 = address_obj['line1']
        if 'line2' in address_obj:
            self.line2 = address_obj['line2']
        if 'line3' in address_obj:
            self.line3 = address_obj['line3']
        if 'pincode_id' in address_obj:
            self.pincode_id = address_obj['pincode_id']
        if 'city_id' in address_obj:
            self.city_id = address_obj['city_id']
        if 'district_id' in address_obj:
            self.district_id = address_obj['district_id']
        if 'state_id' in address_obj:
            self.state_id = address_obj['state_id']
        if 'portal_flag' in address_obj:
            self.portal_flag = address_obj['portal_flag']


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

    def get_portal_flag(self):
        return self.portal_flag
