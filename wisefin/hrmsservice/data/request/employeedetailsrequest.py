import json
from django.utils.timezone import now
class EmployeeDetialsRequest:
    id = None
    employee_id = None
    nationality = None
    marital_status = None
    height = None
    weight = None
    blood_grp = None

    def __init__(self, emp_obj):
        if 'id' in emp_obj:
            self.id = emp_obj['id']
        if 'employee_id' in emp_obj:
            self.employee_id = emp_obj['employee_id']
        if 'nationality' in emp_obj:
            self.nationality = emp_obj['nationality']
        if 'marital_status' in emp_obj:
            self.marital_status = emp_obj['marital_status']
        if 'height' in emp_obj:
            self.height = emp_obj['height']
        if 'weight' in emp_obj:
            self.weight = emp_obj['weight']
        if 'blood_grp' in emp_obj:
            self.blood_grp = emp_obj['blood_grp']


    def get(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def get_id(self):
        return self.id
    def get_employee_id(self):
        return self.employee_id
    def get_nationality(self):
        return self.nationality
    def get_marital_status(self):
        return self.marital_status
    def get_height(self):
        return self.height
    def get_weight(self):
        return self.weight
    def get_blood_grp(self):
        return self.blood_grp

class EmployeeFamilyInfoRequest:

    def empfamilyinfo_request(self,employee_obj, user_id,employee_id):
        create_arr = []
        update_arr = []
        for emp_obj in employee_obj:
            data = dict()
            data['employee_id'] = employee_id
            if 'name' in emp_obj:
                data['name'] = emp_obj['name']
            if 'relationship' in emp_obj:
                data['relationship'] = emp_obj['relationship']
            if 'dob' in emp_obj:
                data['dob'] = emp_obj['dob']
            if 'no' in emp_obj:
                data['no'] = emp_obj['no']

            if 'id' in emp_obj:
                data['id'] = emp_obj['id']
                data['updated_by'] = user_id
                data['updated_date'] = now()
                update_arr.append(data)
            else:
                data['created_by'] = user_id
                create_arr.append(data)
        val = {'update_arr': update_arr, 'create_arr': create_arr}
        return val

class EmpEmergencyContactRequest:

    def empemergencycontact_request(self,employee_obj, user_id,employee_id):
        create_arr = []
        update_arr = []
        for emp_obj in employee_obj:
            data = dict()
            data['employee_id'] = employee_id
            if 'name' in emp_obj:
                data['name'] = emp_obj['name']
            if 'phone_no' in emp_obj:
                data['phone_no'] = emp_obj['phone_no']
            if 'relationship' in emp_obj:
                data['relationship'] = emp_obj['relationship']
            if 'address' in emp_obj:
                data['address'] = emp_obj['address']

            if 'id' in emp_obj:
                data['id'] = emp_obj['id']
                data['updated_by'] = user_id
                data['updated_date'] = now()
                update_arr.append(data)
            else:
                data['created_by'] = user_id
                create_arr.append(data)
        val = {'update_arr': update_arr, 'create_arr': create_arr}
        return val



class HrmsAddressRequest:
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

