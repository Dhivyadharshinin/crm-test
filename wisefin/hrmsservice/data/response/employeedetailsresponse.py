import json
from hrmsservice.util.hrmsutil import Relationship
from attendanceservice.util.attendanceutil import date_to_m_sec
class EmployeeDetialsResponse:
    id = None
    nationality = None
    marital_status = None
    height = None
    weight = None
    blood_grp = None

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_nationality(self, nationality):
        self.nationality = nationality

    def set_marital_status(self, marital_status):
        self.marital_status = marital_status

    def set_height(self, height):
        self.height = height

    def set_weight(self, weight):
        self.weight = weight

    def set_blood_grp(self, blood_grp):
        self.blood_grp = blood_grp


class EmployeeFamilyInfoResponse:
    id,  name, relationship, dob, no = (None,)*5

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_name(self, name):
        self.name = name

    def set_relationship(self,number):
        emp_relationship = Relationship().get_relationship_util(number)
        self.relationship = emp_relationship

    def set_dob(self, dob):
        self.dob = str(dob)

    def set_no(self, no):
        self.no = no


class EmpEmergencyContactResponse:
    id, name,phone_no, relationship,address_id = (None,)*5

    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def set_id(self, id):
        self.id = id

    def set_name(self, name):
        self.name = name

    def set_phone_no(self,phone_no):
        self.phone_no = phone_no

    def set_relationship(self, number):
        emp_relationship = Relationship().get_relationship_util(number)
        self.relationship = emp_relationship

    def set_address_id(self, address_id, arr):
        self.address_id = None
        for i in arr:
            if i.id ==address_id :
                self.address_id = i
                break

class AddressResponse:
    id = None
    line1 = None
    line2 = None
    line3 = None
    pincode = None
    city = None
    district = None
    state = None

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

    def set_pincode(self, pincode_id,arr):
        self.pincode = None
        for i in arr:
            if i.id == pincode_id:
                self.pincode = i
                break

    def set_city(self, city_id,arr):
        self.city = None
        for i in arr:
            if i.id == city_id:
                self.city = i
                break

    def set_district(self, district_id,arr):
        self.district = None
        for i in arr:
            if i.id == district_id:
                self.district = i
                break

    def set_state(self, state_id,arr):
        self.state = None
        for i in arr:
            if i.id == state_id:
                self.state = i
                break


class EmpShiftMappingResponse:
    employee_id = None
    shift_id = None
    effective_from = None
    effective_to = None
    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def set_employee_id(self, employee_id, arr):
        self.employee_id = None
        for i in arr:
            if i.id == employee_id:
                self.employee_id = i
                break
    def set_shift_id(self, shift_id,arr):
        self.shift_id = None
        for i in arr:
            if i.id == shift_id:
                self.shift_id = i
                break

    def set_effective_from(self, effective_from):
        self.effective_from = date_to_m_sec(effective_from)

    def set_effective_to(self, effective_to):
        self.effective_to = date_to_m_sec(effective_to)