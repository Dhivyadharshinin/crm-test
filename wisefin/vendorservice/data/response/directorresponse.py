import json


class DirectorResponse:
    vendor_id = None
    id = None
    name = None
    d_sign = None
    d_pan = None
    d_sanctions = False
    d_match = False
    portal_flag = 0

    def get(self):
      return json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=True, indent=4)

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def set_id(self, id):
        self.id = id

    def get_id(self):
        return self.id

    def set_vendor_id(self, id):
        self.vendor_id = id

    def get_vendor_id(self):
        return self.vendor_id

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

    def get_d_sign(self):
        return self.d_sign

    def get_d_pan(self):
        return self.d_pan

    def get_d_sanctions(self):
        return self.d_sanctions

    def get_d_match(self):
        return self.d_match

    def set_portal_flag(self, portal_flag):
        self.portal_flag = portal_flag

    def get_portal_flag(self):
        return self.portal_flag
