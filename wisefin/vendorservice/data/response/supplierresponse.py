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
        self.city_id= city_id

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






class ContactResponse:
        id = None
        type_id = None
        name = None
        designation = None
        landline = None
        landline2 = None
        mobile = None
        mobile2 = None
        email= None
        dob =None
        wedding_date = ''
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
            dob=str(dob)
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


class ProfileResponse:
    id = None
    year = None
    associate_year = None
    award_details = None
    permanent_employee = None
    temporary_employee = None
    total_employee = None
    branch = None
    factory = None
    remarks = None
    modify_ref_id = None
    modify_status = None
    portal_flag = 0

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_year(self, year):
        self.year = year

    def set_associate_year(self, associate_year):
        self.associate_year = associate_year

    def set_award_details(self, award_details):
        self.award_details = award_details

    def set_permanent_employee(self, permanent_employee):
        self.permanent_employee = permanent_employee

    def set_temporary_employee(self, temporary_employee):
        self.temporary_employee = temporary_employee

    def set_total_employee(self, total_employee):
        self.total_employee = total_employee

    def set_branch(self, branch):
        self.branch = branch

    def set_factory(self, factory):
        self.factory = factory

    def set_remarks(self, remarks):
        self.remarks = remarks

    def set_modify_ref_id(self, modify_ref_id):
        self.modify_ref_id = modify_ref_id

    def set_modify_status(self, modify_status):
        self.modify_status = modify_status

    def get_id(self):
        return self.id

    def get_year(self):
        return self.year

    def get_associate_year(self):
        return self.associate_year

    def get_award_details(self):
        return self.award_details

    def get_permanent_employee(self):
        return self.permanent_employee

    def get_temporary_employee(self):
        return self.temporary_employee

    def get_total_employee(self):
        return self.total_employee

    def get_branch(self):
        return self.branch

    def get_factory(self):
        return self.factory

    def get_remarks(self):
        return self.remarks

    def get_portal_flag(self):
        return self.portal_flag

    def set_portal_flag(self, portal_flag):
        self.portal_flag = portal_flag

class ContractorResponse:
    id = None
    name = None
    service = None
    remarks = None
    vendor_id = None
    modify_ref_id = None
    modify_status = None
    created_by = None
    portal_flag = 0

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_name(self, name):
        self.name = name

    def set_service(self, service):
        self.service = service

    def set_remarks(self, remarks):
        self.remarks = remarks

    def set_vendor_id(self, vendor_id):
        self.vendor_id = vendor_id

    def set_created_by(self, created_by):
        self.created_by = created_by

    def set_modify_ref_id(self, modify_ref_id):
        self.modify_ref_id = modify_ref_id

    def set_modify_status(self, modify_status):
            self.modify_status = modify_status

    def get_name(self):
        return self.name

    def get_service(self):
        return self.service

    def get_remarks(self):
        return self.remarks

    def get_id(self):
        return self.id

    def get_portal_flag(self):
        return self.portal_flag

    def set_portal_flag(self, portal_flag):
        self.portal_flag = portal_flag



class ClientResponse:
    id = None
    name = None
    vendor_id = None
    modify_ref_id = None
    modify_status = None
    created_by = None
    portal_flag = 0

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_vendor_id(self,vendor_id):
        self.vendor_id=vendor_id

    def set_name(self, name):
        self.name = name

    def set_address_id(self, address_id):
        self.address_id = address_id

    def set_created_by(self,created_by):
        self.created_by =created_by

    def set_modify_ref_id(self, modify_ref_id):
        self.modify_ref_id = modify_ref_id

    def set_modify_status(self, modify_status):
        self.modify_status = modify_status

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_address_id(self):
        return self.address_id

    def set_portal_flag(self, portal_flag):
        self.portal_flag = portal_flag

    def get_portal_flag(self):
        return self.portal_flag


class BranchResponse:
    id = None
    vendor_id =None
    name = None
    remarks = None
    limitdays = None
    creditterms = None
    gst_number = None
    pan_no = None
    address_id =None
    contact_id =None
    created_by =None
    modify_ref_id = None
    modify_status = None
    code = None
    is_active = None
    portal_flag = 0

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_vendor_id(self,vendor_id):
        self.vendor_id = vendor_id

    def set_name(self, name):
        self.name = name

    def set_remarks(self, remarks):
        self.remarks = remarks

    def set_limitdays(self, limitdays):
        self.limitdays = limitdays

    def set_creditterms(self, creditterms):
        self.creditterms = creditterms

    def set_gstno(self, gstno):
        self.gstno = gstno

    def set_panno(self, panno):
        self.panno = panno

    def set_created_by(self,created_by):
        self.created_by =created_by

    def set_address_id(self, address_id):
        self.address_id = address_id

    def set_contact_id(self, contact_id):
        self.contact_id = contact_id

    def set_modify_ref_id(self, modify_ref_id):
        self.modify_ref_id = modify_ref_id

    def set_modify_status(self, modify_status):
        self.modify_status = modify_status
    def set_code(self,code):
        self.code=code
    def set_is_active(self, is_active):
        self.is_active = is_active
    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_limitdays(self):
        return self.limitdays

    def get_creditterms(self):
        return self.creditterms

    def get_panno(self):
        return self.panno

    def get_gstno(self):
        return self.gstno

    def get_remarks(self):
        return self.remarks

    def get_address_id(self):
        return self.address_id

    def get_contact_id(self):
        return self.contact_id

    def get_code(self):
        return self.code

    def get_portal_flag(self):
        return self.portal_flag

    def set_portal_flag(self, portal_flag):
        self.portal_flag = portal_flag



class ProductResponse:
    id = None
    name = None
    type = None
    age = None
    client1_id=None
    client2_id=None
    customer1_id=None
    customer2_id=None
    vendor_id=None
    created_by =None
    modify_ref_id = None
    modify_status = None
    portal_flag = 0

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_vendor_id(self,vendor_id):
        self.vendor_id=vendor_id

    def set_name(self, name):
        self.name = name

    def set_type(self, type):
        self.type = type

    def set_age(self, age):
        self.age = age

    def set_client1_id(self, client1_id):
        self.client1_id = client1_id

    def set_client2_id(self, client2_id):
        self.client2_id = client2_id

    def set_customer1_id(self, customer1_id):
        self.customer1_id = customer1_id

    def set_customer2_id(self, customer2_id):
        self.customer2_id = customer2_id

    def set_created_by(self,created_by):
        self.created_by =created_by

    def set_modify_ref_id(self, modify_ref_id):
        self.modify_ref_id = modify_ref_id

    def set_modify_status(self, modify_status):
        self.modify_status = modify_status

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_age(self):
        return self.age

    def get_type(self):
        return self.type

    def get_client1_id(self):
        return self.client1_id

    def get_client2_id(self):
        return self.client2_id

    def get_customer1_id(self):
        return self.customer1_id

    def get_customer2_id(self):
        return self.customer2_id

    def get_portal_flag(self):
        return self.portal_flag

    def set_portal_flag(self, portal_flag):
        self.portal_flag = portal_flag
