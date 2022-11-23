import json


class PincodeResquest:
    id = None
    district_id = None
    city_id = None
    no = None
    district_code = None
    city_code = None
    state_code = None
    status = None


    def __init__(self, pincode_obj):
        if 'id' in pincode_obj:
            self.id = pincode_obj['id']
        if 'district_id' in pincode_obj:
            self.district_id = pincode_obj['district_id']
        if 'city_id' in pincode_obj:
            self.city_id = pincode_obj['city_id']
        if 'no' in pincode_obj:
            self.no = pincode_obj['no']
        if 'district_code' in pincode_obj:
            self.district_code = pincode_obj['district_code']
        if 'city_code' in pincode_obj:
            self.city_code = pincode_obj['city_code']
        if 'state_code' in pincode_obj:
            self.state_code = pincode_obj['state_code']

        if 'status' in pincode_obj:
            self.status = pincode_obj['status']



    def get_id(self):
        return self.id

    def get_district(self):
        return self.district_id

    def get_city(self):
        return self.city_id

    def get_district_code(self):
        return self.district_code

    def get_city_code(self):
        return self.city_code

    def get_no(self):
        return self.no

    def get_state_code(self):
        return self.state_code

    def get_status(self):
        return self.status
