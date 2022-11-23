from rest_framework import permissions
from userservice.service.modulemappingservice import ModuleMappingService
from userservice.service.rolemoduleservice import RoleModuleService
from userservice.models import Module
from django.db.models import Q
from userservice.service.employeeservice import EmployeeService
from userservice.service.roleemployeeservice import RoleEmployeeService
from utilityservice.permissions.util.commonutil import AssignModule
from nwisefin.settings import SERVER_IP

class UrlPermission(permissions.BasePermission):

    def has_permission_1(self, request, view):
        return True

    def has_permission(self, request, view):
        if request.method == 'OPTIONS':
            print('options')
            return False
        user_id = request.employee_id
        scope = request.scope
        # user_id=1
        method = request.method
        # url = str(request._request)
        # url_name = url.split("'")
        # url_name=url_name[1]
        # url_name = url_name.split("?")
        # url_check_arr=url_name[0].split("/")

        path = request.build_absolute_uri()
        path = path.split("?")[0]
        url_name = path.replace(SERVER_IP, '')
        url_check_arr = url_name.split("/")

        module_url = url_check_arr[1]
        url_dict = {}
        url_dict['module'] = module_url
        url_dict['method'] = method

        del url_check_arr[0:2]
        # url_check_arr = url_check_arr.split("?")
        url=''
        for i in url_check_arr:
            if i.isnumeric() :
                i = '<int>'
            url = url + i +'/'
        text_url = url[:-1]
        url_dict['url'] = text_url

        # <WSGIRequest: GET '/mstserv/country/1'>
        # employee = Employee.objects.get(user_id=user_id)
        # employee_id = employee.id
        employee_service = EmployeeService(scope)
        employee_id = employee_service.get_empid_from_userid(user_id)
        module_name = url_dict.get('module')

        module_serv = AssignModule()
        check_url_dict = module_serv.module_mapping(module_name)

        url_key = url_dict.get('url')
        method_key = url_dict.get('method')
        method = check_url_dict.get(url_key)

        check_data = method.get(method_key)

        emp_permission_service =RoleEmployeeService(scope)
        module_role = emp_permission_service.fetch_employee_submodule(user_id,True)
        permission = False
        for i in module_role.data:
            module=i.name
            module_id = i.id
            role_obj = i.role
            # role=[]
            for r in role_obj:
                # role.append(r.name)
                role = r.name
                if module in  check_data.get('module'):
                    if role in check_data.get('module_role'):
                        permission = True
                        self.check_submodule(module_id, scope)

                        for sub in i.submodule:
                            permission = False
                            submodule = sub.name
                            subrole_obj = sub.role
                            for srole in subrole_obj :
                                subrole = srole.name
                                if submodule in check_data.get('submodule'):
                                    if subrole in check_data.get('submodule_role'):
                                        permission = True
                                        return permission

        return permission

    def check_submodule(self,module_id, scope):
        entity_id = scope['default']['entity']['id']
        submodule = Module.objects.filter(refid_id = module_id, entity_id=entity_id)
        permission = False
        if len(submodule) <= 0:
            permission = True
        return permission
