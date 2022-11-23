import json


class DirectorRequest:
    id = None
    vendor_id = None
    name = None
    d_sign = None
    d_pan = None
    d_sanctions = False
    d_match = False
    portal_flag = 0

    def __init__(self, director_obj):
        if 'id' in director_obj:
            self.id = director_obj['id']
        if 'vendor_id' in director_obj:
            self.vendor_id = director_obj['vendor_id']
        if 'name' in director_obj:
            self.name = director_obj['name']
        if 'd_sign' in director_obj:
            self.d_sign = director_obj['d_sign']
        if 'd_pan' in director_obj:
            self.d_pan = director_obj['d_pan']
        if 'd_sanctions' in director_obj:
            if director_obj['d_sanctions'] == 'Y':
                self.d_sanctions = 1
            # self.d_sanctions = director_obj['d_sanctions']
        if 'd_match' in director_obj:
            if director_obj['d_match'] == 'Y':
                self.d_match = 1
            # self.d_match = director_obj['d_match']
        if 'portal_flag' in director_obj:
            self.portal_flag = director_obj['portal_flag']

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_vendor_id(self, vendor_id):
        self.vendor_id = vendor_id

    def set_name(self, name):
        self.name = name

    def set_d_sign(self, d_sign):
        self.d_sign = d_sign

    def set_d_pan(self, d_pan):
        self.d_pan = d_pan

    def set_d_sanctions(self, d_sanctions):
        if d_sanctions == True:
            value = {'id': 'Y', 'name': 'YES'}
        else:
            value = {'id': 'N', 'name': 'NO'}
        self.d_sanctions = value

    def set_d_match(self, d_match):
        if d_match == True:
            value = {'id': 'Y', 'name': 'YES'}
        else:
            value = {'id': 'N', 'name': 'NO'}
        self.d_match = value

    def get_id(self):
        return self.id

    def get_vendor_id(self):
        return self.vendor_id

    def get_name(self):
        return self.name

    def get_d_sign(self):
        return self.d_sign

    def get_d_pan(self):
        return self.d_pan

    def get_d_sanctions(self):
        return self.d_sanctions

    def get_d_match(self):
        return self.d_match

    def get_portal_flag(self):
        return self.portal_flag

    def set_portal_flag(self, portal_flag):
        self.portal_flag = portal_flag
