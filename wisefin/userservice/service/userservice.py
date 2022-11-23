from django.db.models import Q
from utilityservice.service.applicationconstants import ApplicationNamespace
from userservice.models import EmployeeEntityMapping, Employee, EmployeeDepartmentPermission,Vow_userEntityMapping,Vow_user
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.data.response.nwisefinlist import NWisefinList
from userservice.data.response.employeeresponse import EmployeeResponse
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator


class UserService:
    def get_default_entity_id(self, employee_id):
        condition = Q(employee_id__exact=employee_id) & Q(is_default__exact=True)
        map_obj = EmployeeEntityMapping.objects.using('default').filter(condition)
        if len(map_obj) > 0:
            map_obj = map_obj[0]
            return map_obj.entity_id
        else:
            return None

    def get_employee_entityids(self, employee_id):
        map_obj = EmployeeEntityMapping.objects.using('default').filter(employee_id=employee_id)
        entity_ids = []
        if len(map_obj) > 0:
            for map in map_obj:
                entity_ids.append(map.entity_id)
        return entity_ids

    def change_employee_entity_mapping(self, user_name, entity_id):
        employee = Employee.objects.filter(code=user_name)
        EmployeeEntityMapping.objects.using('default').filter(employee_id=employee[0].id).update(is_default=False)
        EmployeeEntityMapping.objects.using('default').filter(entity_id=entity_id, employee_id=employee[0].id)\
            .update(is_default=True)
    def change_vow_entity_mapping(self, user_name, entity_id):
        employee = Vow_user.objects.filter(code=user_name)
        Vow_userEntityMapping.objects.using('default').filter(employee_id=employee[0].id).update(is_default=False)
        Vow_userEntityMapping.objects.using('default').filter(entity_id=entity_id, employee_id=employee[0].id)\
            .update(is_default=True)


class Vendor_user_service(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.USER_SERVICE)

    def get_employee(self, employee_id):
        employee = Employee.objects.using('default').filter(id=employee_id)
        if len(employee) != 0:
            return employee[0]
        else:
            return

    def get_employee_with_dept(self, employee_id, query, vys_page):
        employee_department = EmployeeDepartmentPermission.objects.using('default').filter(department__dept_id=None,
                                                                                           employee_id=employee_id)
        if len(employee_department) != 0:
            department_id = employee_department[0].department_id

            # fetch employee with same department
            employee_list = EmployeeDepartmentPermission.objects.using('default').filter(
                department_id=department_id).values_list('employee_id', flat=True)
            employee_list = list(employee_list)
            condition = Q(entity_id=self._entity_id()) & Q(employee__status=1) & Q(employee__id__in=employee_list)

        else:
            condition = Q(entity_id=self._entity_id()) & Q(employee__status=1)

        if (query is not None) and (query != ''):
            condition &= (Q(employee__full_name__icontains=query) | Q(employee__code__icontains=query) | Q(
             employee__designation__icontains=query))
        employee_list = EmployeeEntityMapping.objects.values(
            'employee__id', 'employee__full_name', 'employee__code', 'employee__employee_branch_id',
            'employee__employee_branch__code', "employee__employee_branch__name"
        ).filter(condition)[vys_page.get_offset():vys_page.get_query_limit()]
        vlist = NWisefinList()

        for employee in employee_list:
            if employee['employee__id'] != employee_id:
                emp_resp = EmployeeResponse()
                disp_name = '(' + employee['employee__code'] + ') ' + employee['employee__full_name']
                emp_resp.set_full_name(disp_name)
                emp_resp.set_id(employee['employee__id'])
                emp_resp.branch_id = employee['employee__employee_branch_id']
                emp_resp.branch_code = employee['employee__employee_branch__code']
                emp_resp.branch_name = employee['employee__employee_branch__name']
                vlist.append(emp_resp)
        vpage = NWisefinPaginator(employee_list, vys_page.get_index(), 10)
        vlist.set_pagination(vpage)
        return vlist
