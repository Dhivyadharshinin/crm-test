import json

from userservice.models import EmployeeBranch
from userservice.service.authservice import AuthService
from userservice.service.employeeservice import EmployeeService


class NWisefinUtilityService:
    def get_user_info(self, request, user_list):
        # authservice=AuthService()
        # user_resp = authservice.user(user_list)
        scope = request.scope
        emp_service = EmployeeService(scope)
        user_resp = emp_service.employee_info_by_id(user_list)
        user_data = json.loads(user_resp)
        return user_data

    def get_emp_info_by_id(self, request, user_list):
        scope = request.scope
        emp_service = EmployeeService(scope)
        user_resp = emp_service.employee_info_by_id(user_list)
        user_data = json.loads(user_resp)
        return user_data

    def get_employee_branch(self, id):
        obj = EmployeeBranch.objects.filter(id__in=id).values('code', 'name','id')
        arr = []
        for i in obj:
            data = {"id": i['id'], "code": i['code'], "name": i['name']}
            arr.append(data)
        return arr
