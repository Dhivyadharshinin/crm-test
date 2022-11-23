import json
from productservice.util.product_util import Relationship,common_util_fetch,ContactUtil

class LeadFamilyInfoResponse:
    id,  name, relationship, dob = (None,)*4

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_name(self, name):
        self.name = name

    def set_relationship(self, number):
        lead_relationship = common_util_fetch(Relationship.var,number)
        self.relationship = lead_relationship

    def set_dob(self, dob):
        self.dob = str(dob)

class LeadContactInfoResponse:
    id, c_value, type = (None,)*3

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_c_value(self, c_value):
        self.c_value = c_value

    def set_type(self, type):
        lead_type = common_util_fetch(ContactUtil.var, type)
        self.type = lead_type

class BankAccountResponse:
    id,  bank_id, branch_id, account_number,ifsc_code = (None,)*5

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_bank_id(self, bank_id):
        self.bank_id = bank_id

    def set_branch_id(self, branch_id):
        self.branch_id = branch_id

    def set_account_number(self, account_number):
        self.account_number = account_number

    def set_ifsc_code(self, ifsc_code):
        self.ifsc_code = ifsc_code


class CrmAddressResponse:
    id,  line1, line2, line3, pincode_id, city_id, district_id, state_id = (None,)*8

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

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
        self.city_id = city_id

    def set_district_id(self, district_id):
        self.district_id = district_id

    def set_state_id(self, state_id):
        self.state_id = state_id

