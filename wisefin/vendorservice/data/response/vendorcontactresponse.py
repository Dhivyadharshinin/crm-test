import json
import datetime
class ContactResponse:
    id = None
    type_id = None
    name = None
    designation = None
    landline = None
    landline2 = None
    mobile = None
    mobile2 = None
    email = None
    dob = None
    wedding_date = None
    portal_flag = 0

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_type_id(self, type_id):
        self.type_id = type_id

    def set_name(self, name):
        self.name = name

    def set_designation(self, designation):
        self.designation = designation

    def set_landline(self, landline):
        self.landline = landline

    def set_landline2(self, landline2):
        self.landline2 = landline2

    def set_mobile(self, mobile):
        self.mobile = mobile

    def set_mobile2(self, mobile2):
        self.mobile2 = mobile2

    def set_email(self, email):
        self.email = email

    def set_dob(self, dob):
        dob = str(dob)
        self.dob = dob

    def set_wedding_date(self, wedding_date):
        wedding_date = str(wedding_date)
        self.wedding_date = wedding_date

    def get_id(self):
        return self.id

    def get_type_id(self):
        return self.type_id

    def get_name(self):
        return self.name

    def get_designation(self):
        return self.designation

    def get_landline(self):
        return self.landline

    def get_landline2(self):
        return self.landline2

    def get_mobile(self):
        return self.mobile

    def get_mobile2(self):
        return self.mobile2

    def get_email(self):
        return self.email

    def get_dob(self):
        return self.dob

    def get_wedding_date(self):
        return self.wedding_date

    def get_portal_flag(self):
        return self.portal_flag

    def set_portal_flag(self, portal_flag):
        self.portal_flag = portal_flag
