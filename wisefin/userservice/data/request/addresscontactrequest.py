import json
import string

class ContactRequest:
    id = None
    type_id = None
    name = None
    designation_id = None
    landline = None
    landline2 = None
    mobile = None
    mobile2 = None
    email = None
    dob = None
    wedding_date = None

    def __init__(self, contact_obj):
        if 'id' in contact_obj:
            self.id = contact_obj['id']
        if 'type_id' in contact_obj:
            self.type_id = contact_obj['type_id']
        if 'name' in contact_obj:
            self.name = contact_obj['name']
        if 'designation_id' in contact_obj:
            self.designation_id = contact_obj['designation_id']
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

    def get_id(self):
        return self.id

    def get_type_id(self):
        return self.type_id

    def get_name(self):
        return self.name

    def get_designation_id(self):
        return self.designation_id

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

class AddressRequest:
    id = None
    line1 = None
    line2 = None
    line3 = None
    pincode_id = None
    city_id = None
    district_id = None
    state_id = None

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

class ContactSyncRequest:
    id = None
    type_id = None
    name = None
    designation_id = None
    landline = None
    landline2 = None
    mobile = None
    mobile2 = None
    email = None
    dob = None
    wedding_date = None

    def __init__(self, contact_obj):
        if 'id' in contact_obj:
            self.id = contact_obj['id']
        if 'contact_contacttypegid' in contact_obj:
            self.type_id = contact_obj['contact_contacttypegid']
        if 'contact_personname' in contact_obj:
            self.name = contact_obj['contact_personname']
        if 'contact_designation_gid' in contact_obj:
            self.designation_id = contact_obj['contact_designationgid']
        if 'contact_landline1' in contact_obj:
            self.landline = contact_obj['contact_landline1']
        if 'contact_landline2' in contact_obj:
            self.landline2 = contact_obj['contact_landline2']
        if 'contact_mobile1' in contact_obj:
            self.mobile = contact_obj['contact_mobile1']
        if 'contact_mobile2' in contact_obj:
            self.mobile2 = contact_obj['contact_mobile2']
        if 'contact_email' in contact_obj:
            self.email = contact_obj['contact_email']
        if 'contact_dob' in contact_obj:
            self.dob = contact_obj['contact_dob']
        if 'contact_wd' in contact_obj:
            self.wedding_date = contact_obj['contact_wd']

    def get_id(self):
        return self.id

    def get_type_id(self):
        return self.type_id

    def get_name(self):
        return self.name

    def get_designation_id(self):
        return self.designation_id

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

class AddressSyncRequest:
    id = None
    line1 = None
    line2 = None
    line3 = None
    pincode_id = None
    city_id = None
    district_id = None
    state_id = None

    def __init__(self, address_obj):
        if 'id' in address_obj:
            self.id = address_obj['id']
        if 'adds_1' in address_obj:
            self.line1 = address_obj['adds_1']
        if 'adds_2' in address_obj:
            self.line2 = address_obj['adds_2']
        if 'adds_3' in address_obj:
            self.line3 = address_obj['adds_3']
        if 'adds_pincode' in address_obj:
            self.pincode_id = address_obj['adds_pincode']
        if 'adds_citygid' in address_obj:
            self.city_id = address_obj['adds_citygid']
        if 'adds_districtgid' in address_obj:
            self.district_id = address_obj['adds_districtgid']
        if 'adds_stategid' in address_obj:
            self.state_id = address_obj['adds_stategid']


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

from masterservice.service.designationservice import DesignationService
class BranchContactSyncRequest:
    id = None
    type_id = None
    name = None
    designation_id = None
    landline = None
    landline2 = None
    mobile = None
    mobile2 = None
    email = None
    dob = None
    wedding_date = None

    def __init__(self, contact_obj):
        if 'id' in contact_obj:
            self.id = contact_obj['id']
        if 'type_id' in contact_obj:
            self.type_id = contact_obj['type_id']
        if 'CONTACT_PERSON' in contact_obj:
            if contact_obj['CONTACT_PERSON'] == '':
                self.name = None
            else:
                self.name = contact_obj['CONTACT_PERSON']
        if 'CONTACT_PERSON_DESIGNATION' in contact_obj and contact_obj['CONTACT_PERSON_DESIGNATION'] is not None:
            if contact_obj['CONTACT_PERSON_DESIGNATION'] != "":
                self.designation_id = contact_obj['CONTACT_PERSON_DESIGNATION']
                designation_serv = DesignationService()
                self.designation_id = designation_serv.get_state_by_designation(self.designation_id)

        if 'LANDLINE1' in contact_obj :
            if contact_obj['LANDLINE1'] == '':
                self.landline = None
            else:
                self.landline = contact_obj['LANDLINE1']
        if 'LANDLINE2' in contact_obj:
            if contact_obj['LANDLINE2'] == '':
                self.landline2 = None
            else:
                self.landline2 = contact_obj['LANDLINE2']
        if 'MOBILE1' in contact_obj:
            if contact_obj['MOBILE1'] == '':
                self.mobile = None
            else:
                self.mobile = contact_obj['MOBILE1']
        if 'MOBILE2' in contact_obj:
            if contact_obj['MOBILE2'] == '':
                self.mobile2 = None
            else:
                self.mobile2 = contact_obj['MOBILE2']
        if 'EMAIL' in contact_obj:
            if contact_obj['EMAIL'] == '':
                self.email = None
            else:
                self.email = contact_obj['EMAIL']
        if 'dob' in contact_obj:
            self.dob = contact_obj['dob']
        if 'wedding_date' in contact_obj:
            self.wedding_date = contact_obj['wedding_date']

    def get_id(self):
        return self.id

    def get_type_id(self):
        return self.type_id

    def get_name(self):
        return self.name

    def get_designation_id(self):
        return self.designation_id

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

from masterservice.service.cityservice import CityService
from masterservice.service.districtservice import DistrictService
from masterservice.service.stateservice import StateService
from masterservice.service.pincodeservice import PincodeService
class BranchAddressSyncRequest:
    id = None
    line1 = None
    line2 = None
    line3 = None
    pincode_id = None
    city_id = None
    district_id = None
    state_id = None

    def __init__(self, address_obj):
        state = None
        city =None
        district = None

        if 'id' in address_obj:
            self.id = address_obj['id']
        if 'ADDRESS1' in address_obj:
            if address_obj['ADDRESS1'] == '':
                self.line1 = None
            else:
                self.line1 = address_obj['ADDRESS1']

        if 'ADDRESS2' in address_obj:
            if address_obj['ADDRESS2'] == '':
                self.line2 = None
            else:
                self.line2 = address_obj['ADDRESS2']
        if 'ADDRESS3' in address_obj:
            if address_obj['ADDRESS3'] == '':
                self.line3 = None
            else:
                self.line3 = address_obj['ADDRESS3']

        if 'STATE' in address_obj and address_obj['STATE'] is not None :
            if address_obj['STATE'] != "" and address_obj['ADDRESS1'] != '':
                state = string.capwords(address_obj['STATE'])
                state_serv = StateService()
                self.state_id = state_serv.get_state_by_name(state)

        if 'DISTRICT' in address_obj and address_obj['DISTRICT'] is not None:
            if address_obj['DISTRICT'] != "" and address_obj['ADDRESS1'] != '':
                district  = string.capwords(address_obj['DISTRICT'])
                district_serv = DistrictService()
                self.district_id = district_serv.get_district_by_name(district,self.state_id,state)

        if 'CITY' in address_obj and address_obj['CITY'] is not None:
            if address_obj['CITY'] != "" and address_obj['ADDRESS1'] != '':
                city = string.capwords(address_obj['CITY'])
                city_serv = CityService()
                self.city_id = city_serv.get_city_by_name(city,self.state_id,state)

        if 'PINCODE' in address_obj and address_obj['PINCODE'] is not None:
            if address_obj['PINCODE'] != "" and address_obj['ADDRESS1'] != '':
                pincode = address_obj['PINCODE']
                pincode_serv = PincodeService()
                self.pincode_id = pincode_serv.get_pincode_by_no(pincode,self.district_id,self.city_id,district,city)



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