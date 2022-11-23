import json

class ContactRequest:
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

    def __init__(self, contact_obj):
        if 'id' in contact_obj:
            self.id = contact_obj['id']
        if 'type_id' in contact_obj:
            self.type_id = contact_obj['type_id']
        if 'name' in contact_obj:
            self.name = contact_obj['name']
        if 'designation' in contact_obj:
            self.designation = contact_obj['designation']
        if 'landline' in contact_obj:
            self.landline = contact_obj['landline']
        if 'landline2' in contact_obj:
            self.landline2 = contact_obj['landline2']
        if 'mobile' in contact_obj:
            self.mobile = contact_obj['mobile']
        if 'mobile2' in contact_obj:
            self.mobile2 = contact_obj['mobile2']
        if 'email' in contact_obj:
            self.email = contact_obj['email']
        if 'dob' in contact_obj:
            self.dob = contact_obj['dob']
        if 'wedding_date' in contact_obj:
            self.wedding_date = contact_obj['wedding_date']
        if 'portal_flag' in contact_obj:
            self.portal_flag = contact_obj['portal_flag']

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
