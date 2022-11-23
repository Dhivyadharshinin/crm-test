from userservice.service.roleemployeeservice import RoleEmployeeService
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace


class ModulePermission(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)

    # def employee_modulerole(self, employee_id, module):
    #     roleemployee_service = RoleEmployeeService()
    #     user_id_flag = False
    #     role_obj = roleemployee_service.fetch_employee_submodule(employee_id, user_id_flag)
    #     emprole_obj = role_obj.data
    #     role_Arr = []
    #     if len(emprole_obj) > 0:
    #         for i in emprole_obj:
    #
    #             modulename = i.name
    #             if modulename == module:
    #                 role = i.role
    #                 for j in role:
    #                     rolename = j.name
    #                     role_Arr.append(rolename)
    #                 return role_Arr
    #     return role_Arr

    def employee_modulerole(self, employee_id, module):
        roleemployee_service = RoleEmployeeService(self._scope())
        role_Arr = roleemployee_service.fetch_employee_role(employee_id, module)
        return role_Arr
