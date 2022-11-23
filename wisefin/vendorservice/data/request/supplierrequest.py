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
            try:
                 if 'id' in address_obj['pincode_id']:
                    self.pincode_id = address_obj['pincode_id']['id']
            except:
                self.pincode_id = address_obj['pincode_id']
        if 'city_id' in address_obj:
            try:
                if 'id' in address_obj['city_id']:
                    self.city_id = address_obj['city_id']['id']
            except:
                self.city_id = address_obj['city_id']
        if 'district_id' in address_obj:
            try:
                if 'id' in address_obj['district_id']:
                    self.district_id = address_obj['district_id']['id']
            except:
                self.district_id = address_obj['district_id']
        if 'state_id' in address_obj:
            try:
                if 'id' in address_obj['state_id']:
                    self.state_id = address_obj['state_id']['id']
            except:
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

class ContactRequest:
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




class ProfileRequest:
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
    portal_flag = 0

    def __init__(self, profile_obj):
        if 'id' in profile_obj:
            self.id = profile_obj['id']
        if 'year' in profile_obj:
            self.year = profile_obj['year']
        if 'associate_year' in profile_obj:
            self.associate_year = profile_obj['associate_year']
        if 'award_details' in profile_obj:
            self.award_details = profile_obj['award_details']
        if 'permanent_employee' in profile_obj:
            self.permanent_employee = profile_obj['permanent_employee']
        if 'temporary_employee' in profile_obj:
            self.temporary_employee = profile_obj['temporary_employee']
        if 'total_employee' in profile_obj:
            self.total_employee = profile_obj['total_employee']
        if 'branch' in profile_obj:
            self.branch = profile_obj['branch']
        if 'factory' in profile_obj:
            self.factory = profile_obj['factory']
        if 'remarks' in profile_obj:
            self.remarks = profile_obj['remarks']
        if 'portal_flag' in profile_obj:
            self.portal_flag = profile_obj['portal_flag']

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





class ContractRequest:
    id = None
    name = None
    service = None
    remarks = None
    portal_flag = 0

    def __init__(self, contract_obj):
        if 'id' in contract_obj:
            self.id = contract_obj['id']
        if 'name' in contract_obj:
            self.name = contract_obj['name']
        if 'service' in contract_obj:
            self.service = contract_obj['service']
        if 'remarks' in contract_obj:
            self.remarks = contract_obj['remarks']
        if 'portal_flag' in contract_obj:
            self.portal_flag = contract_obj['portal_flag']

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


class ClientRequest:
    id = None
    name = None
    address_id = None
    portal_flag = 0

    def __init__(self, client_obj):
        if 'id' in client_obj:
            self.id = client_obj['id']
        if 'name' in client_obj:
            self.name = client_obj['name']
        if 'address_id' in client_obj:
            self.address_id = client_obj['address_id']
        if 'portal_flag' in client_obj:
            self.portal_flag = client_obj['portal_flag']


    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_address_id(self):
        return self.address_id

    def get_portal_flag(self):
        return self.portal_flag


class BranchRequest:
    id = None
    # vendor_id =None
    name = None
    remarks = None
    limitdays = None
    creditterms = None
    gstno = None
    panno = None
    address_id =None
    contact_id =None
    code =None
    portal_flag = 0

    def __init__(self, branch_obj):
        if 'id' in branch_obj:
            self.id = branch_obj['id']
        if 'name' in branch_obj:
            self.name = branch_obj['name']
        if 'remarks' in branch_obj:
            self.remarks = branch_obj['remarks']
        if 'limitdays' in branch_obj:
            self.limitdays = branch_obj['limitdays']
        if 'creditterms' in branch_obj:
            self.creditterms = branch_obj['creditterms']
        if 'gstno' in branch_obj:
            self.gstno = branch_obj['gstno']
        if 'panno' in branch_obj:
            self.panno = branch_obj['panno']
        if 'address_id' in branch_obj:
            self.address_id = branch_obj['address_id']
        if 'contact_id' in branch_obj:
            self.contact_id = branch_obj['contact_id']
        if 'code' in branch_obj:
            self.code=branch_obj['code']
        if 'is_active' in branch_obj :
            self.is_active = branch_obj [ 'is_active' ]
        if 'portal_flag' in branch_obj:
            self.portal_flag = branch_obj['portal_flag']

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name
    def get_is_active(self):
        return self.is_active

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



class ProductRequest:
    id = None
    name = None
    type = None
    age = None
    client1_id=None
    client2_id=None
    customer1_id=None
    customer2_id=None
    portal_flag = 0

    def __init__(self, product_obj):
        if 'id' in product_obj:
            self.id = product_obj['id']
        if 'name' in product_obj:
            self.name = product_obj['name']
        if 'type' in product_obj:
            self.type = product_obj['type']
        if 'age' in product_obj:
            if product_obj['age'] == "":
                self.age = None
            else:
                self.age = product_obj['age']
        if 'client1_id' in product_obj:
            self.client1_id = product_obj['client1_id']
        if 'client2_id' in product_obj:
            self.client2_id = product_obj['client2_id']
        if 'customer1_id' in product_obj:
            self.customer1_id = product_obj['customer1_id']
        if 'customer2_id' in product_obj:
            self.customer2_id = product_obj['customer2_id']
        if 'portal_flag' in product_obj:
            self.portal_flag = product_obj['portal_flag']

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

class Gstrequest:
    id=None
    state_id = None
    gstno = None

    def __init__(self, branch_obj):
        if 'id' in branch_obj:
            self.id = branch_obj['id']
        if 'state_id' in branch_obj:
            self.state_id = branch_obj['state_id']
        if 'gstno' in branch_obj:
            self.gstno = branch_obj['gstno']

    def set_id(self, id):
        self.id = id

    def get_id(self):
        return self.id

    def set_state_id(self, state_id):
        self.state_id = state_id

    def get_state_id(self):
        return self.state_id

    def set_gstno(self, gstno):
        self.gstno = gstno

    def get_gstno(self):
        return self.gstno

