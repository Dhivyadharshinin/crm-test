import json
from django.utils.timezone import now

class EmployeeEducationDetailsRequest:

    def empeducationdetails_request(self, employee_obj, user_id, employee_id):
        create_arr = []
        update_arr = []

        for emp_obj in employee_obj:
            data = dict()
            data['employee_id'] = employee_id
            if 'inst_name' in emp_obj:
                data['inst_name'] = emp_obj['inst_name']
            if 'passing_year' in emp_obj:
                data['passing_year'] = emp_obj['passing_year']
            if 'passing_month' in emp_obj:
                data['passing_month'] = emp_obj['passing_month']
            if 'percentage' in emp_obj:
                data['percentage'] = emp_obj['percentage']
            if 'city' in emp_obj:
                data['city'] = emp_obj['city']
            if 'title' in emp_obj:
                data['title'] = emp_obj['title']
            if 'stream' in emp_obj:
                data['stream'] = emp_obj['stream']

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


class EmployeeExperiencesRequest:

    def employeeexperiences_request(self, employee_obj, user_id, employee_id):
        create_arr = []
        update_arr = []
        for emp_obj in employee_obj:
            data = dict()
            data['employee_id'] = employee_id
            if 'company' in emp_obj:
                data['company'] = emp_obj['company']
            if 'work_experience' in emp_obj:
                data['work_experience'] = emp_obj['work_experience']
            if 'doj' in emp_obj:
                data['doj'] = emp_obj['doj']
            if 'dor' in emp_obj:
                data['dor'] = emp_obj['dor']
            if 'role' in emp_obj:
                data['role'] = emp_obj['role']
            if 'city' in emp_obj:
                data['city'] = emp_obj['city']

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
