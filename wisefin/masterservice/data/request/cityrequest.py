import json


class CityRequest:
    id = None
    code = None
    name = None
    state_id = None
    district=None
    state_code = None
    status = None
    no=None

    def __init__(self, city_obj):
        if 'id' in city_obj:
            self.id = city_obj['id']
        if 'code' in city_obj:
            self.code = city_obj['code']
        if 'name' in city_obj:
            self.name = city_obj['name']
        if 'district' in city_obj:
            self.district = city_obj['district']
        if 'state_id' in city_obj:
            self.state_id = city_obj['state_id']
        if 'state_code' in city_obj:
            self.state_code = city_obj['state_code']

        if 'status' in city_obj:
            self.status = city_obj['status']
        if 'no' in city_obj:
            self.no = city_obj['no']


    def get_id(self):
        return self.id
    def get_district(self):
        return self.district
    def get_code(self):
        return self.code

    def get_name(self):
        return self.name

    def get_state(self):
        return self.state_id

    def get_state_code(self):
        return self.state_code

    def get_status(self):
        return self.status
    def get_no(self):
        return self.no
