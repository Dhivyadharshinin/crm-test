import traceback

from django.db import IntegrityError
from django.db.models import Q
from django.utils.timezone import now

from nwisefin.settings import logger
from userservice.data.response.departmentresponse import EmployeeDepartmentResponse
from userservice.models import EmployeeDepartment ,EmployeeDepartmentPermission ,Department,Employee
from userservice.service.employeeservice import EmployeeService
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinsuccess import SuccessStatus,SuccessMessage,NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from userservice.data.response.departmentresponse import DepartmentResponse
from userservice.data.response.employeeresponse import EmployeeResponse
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace


class EmployeeDepartmentService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.USER_SERVICE)

    def create_department(self, dept_obj, user_id):
        dept_resp = EmployeeDepartmentResponse()
        if not dept_obj.get_id() is None:
            try:
                logger.error('EMPLOYEEDEPARTMENT: EmployeeDepartment Update Started')
                department = EmployeeDepartment.objects.using(self._current_app_schema()).filter(id=dept_obj.get_id(),entity_id=self._entity_id()).update(name=dept_obj.get_name(),
                         code=dept_obj.get_code(),updated_by=user_id,updated_date=now())
                department = EmployeeDepartment.objects.using(self._current_app_schema()).get(id=dept_obj.get_id())
                logger.error('EMPLOYEEDEPARTMENT: EmployeeDepartment Update Success' + str(department))
            except IntegrityError as error:
                logger.info('ERROR_EmployeeDepartment_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                logger.info('ERROR_EmployeeDepartment_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj

        else:
            try:
                logger.error('EMPLOYEEDEPARTMENT: EmployeeDepartment Creation Started')
                department = EmployeeDepartment.objects.using(self._current_app_schema()).create(name=dept_obj.get_name(), code=dept_obj.get_code(),
                                                               created_by=user_id,entity_id=self._entity_id())
                logger.error('EMPLOYEEDEPARTMENT: EmployeeDepartment Creation Success' + str(department))
            except IntegrityError as error:
                logger.error('ERROR_EmployeeDepartment_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                logger.error('ERROR_EmployeeDepartment_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj

        dept_resp.set_id(department.id)
        dept_resp.set_name(department.name)
        dept_resp.set_code(department.code)
        return dept_resp

    def fetch_department(self, dept_id, user_id):
        department = EmployeeDepartment.objects.using(self._current_app_schema()).get(id=dept_id)
        dept_resp = EmployeeDepartmentResponse()
        dept_resp.set_id(department.id)
        dept_resp.set_name(department.name)
        dept_resp.set_code(department.code)
        return dept_resp

    def fetch_department_list(self, vys_page, user_id):
        departmentList = EmployeeDepartment.objects.using(self._current_app_schema()).all()[vys_page.get_offset():vys_page.get_query_limit()]
        vlist = NWisefinList()
        for department in departmentList:
            dept_resp = EmployeeDepartmentResponse()
            dept_resp.set_id(department.id)
            dept_resp.set_name(department.name)
            dept_resp.set_code(department.code)
            vlist.append(dept_resp)
        vpage = NWisefinPaginator(departmentList, vys_page.get_index(), 10)
        vlist.set_pagination(vpage)
        return vlist


    def emp_to_dep_permission(self,empid,deparr,user_id):
        depid_arr = deparr.get('department_id')
        isadmin = deparr.get('isadmin')
        can_create = deparr.get('can_create')
        emp_service = EmployeeService(self._scope())

        cond = None
        for depid in depid_arr:
            if cond is None:
                cond = Q(employee_id=user_id) & Q(isadmin=True) & Q(department_id=depid)
            else:
                cond |= Q(employee_id=user_id) & Q(isadmin=True) & Q(department_id=depid)

        user_depid_arr = EmployeeDepartmentPermission.objects.using(self._current_app_schema()).filter(cond).values_list('department_id',flat=True)

        if len(user_depid_arr) >0 :

            admin_depid_arr = list(set(depid_arr) & set(user_depid_arr))
            if deparr.get('method') == 'add':

                condition = None
                for id in depid_arr:
                    if condition is None:
                        condition = Q(employee_id=empid) & Q(department_id=id)
                    else:
                        condition |= Q(employee_id=empid) & Q(department_id=id)

                empdep_created = EmployeeDepartmentPermission.objects.using(self._current_app_schema()).filter(condition).values_list('department_id', flat=True)

                #  ADMIN
                cond_update = None
                admin_arr = []
                for id in admin_depid_arr:
                    if id in empdep_created:
                        if cond_update is None:
                            cond_update = Q(employee_id=empid) & Q(department_id=id)
                        else:
                            cond_update |= Q(employee_id=empid) & Q(department_id=id)
                    else:
                        obj = EmployeeDepartmentPermission(employee_id=empid, department_id=id,
                                                           isadmin=isadmin, can_create=can_create)
                        admin_arr.append(obj)

                if cond_update is not None:
                    EmployeeDepartmentPermission.objects.using(self._current_app_schema()).filter(cond_update).update(isadmin=isadmin,
                                                                                         can_create=can_create)
                if len(admin_arr) > 0:
                    EmployeeDepartmentPermission.objects.using(self._current_app_schema()).bulk_create(admin_arr)

                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
                return success_obj

            elif deparr.get('method') == 'remove':
                    arr=[]
                    last_admin=[]
                    for id in admin_depid_arr:
                        cond = EmployeeDepartmentPermission.objects.using(self._current_app_schema()).filter(department_id=id).exclude(employee_id=empid)
                        if len(cond) > 0 :
                            arr.append(id)
                        else:
                            last_admin.append(id)

                    condition = None
                    for id in arr:
                        if condition is None:
                            condition = Q(employee_id=empid)& Q(department_id=id)
                        else:
                            condition |= Q(employee_id=empid)& Q(department_id=id)

                    if condition == None :
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.EMPLOYEE_ADMIN)
                        error_obj.set_description(ErrorDescription.EMPLOYEE_ADMIN)
                        return error_obj
                    else:
                        EmployeeDepartmentPermission.objects.using(self._current_app_schema()).filter(condition).delete()

                        success_obj = NWisefinSuccess()
                        success_obj.set_status(SuccessStatus.SUCCESS)
                        success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
                        return success_obj

        else:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.EMPLOYEE_ADMIN)
            error_obj.set_description(ErrorDescription.EMPLOYEE_ADMIN)
            return error_obj

    def emp_dep_perm_from_department(self,user_id,depid):
        emp_service = EmployeeService(self._scope())
        EmployeeDepartmentPermission.objects.using(self._current_app_schema()).create(employee_id=user_id,
            department_id=depid, isadmin=True)
        return

    def admin_check(self,empid,depid):
        cond = Q(employee_id=empid) & Q(isadmin=True) & Q(department_id=depid)
        user_empid_arr = EmployeeDepartmentPermission.objects.using(self._current_app_schema()).filter(cond).values_list('employee_id', flat=True)
        isadmin_value = False
        if len(user_empid_arr) > 0:
            isadmin_value = True
        return isadmin_value

    def is_sys_check(self,depid):
        dep_sys = Department.objects.using(self._current_app_schema()).get(id=depid)
        is_sys=dep_sys.is_sys
        return is_sys

    def add_emp_to_dep(self,empid_arr,depid,isadmin,can_create):
        arr=[]
        for id in empid_arr:
            obj = EmployeeDepartmentPermission(employee_id=id, department_id=depid,
                                               isadmin=isadmin, can_create=can_create)
            arr.append(obj)
        if len(arr) > 0:
            EmployeeDepartmentPermission.objects.using(self._current_app_schema()).bulk_create(arr)
        return

    def del_emp_to_dep(self,empid_arr,depid):
        condition = None
        for id in empid_arr:
            if condition is None:
                condition = Q(employee_id=id) & Q(department_id=depid)
            else:
                condition |= Q(employee_id=id) & Q(department_id=depid)
        EmployeeDepartmentPermission.objects.using(self._current_app_schema()).filter(condition).delete()
        return

    def update_emp_to_dep(self,empid_arr,depid,isadmin,can_create):
        condition = None
        for id in empid_arr:
            if condition is None:
                condition = Q(employee_id=id) & Q(department_id=depid)
            else:
                condition |= Q(employee_id=id) & Q(department_id=depid)
        EmployeeDepartmentPermission.objects.using(self._current_app_schema()).filter(condition).update(isadmin=isadmin ,can_create=can_create)
        return

    def get_depid_by_depname(self,dep_name):
        try:
            department= Department.objects.using(self._current_app_schema()).get(name=dep_name)
            dep_id = department.id
            return dep_id
        except:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.Department_ID)
            error_obj.set_description(ErrorDescription.Department_ID)
            return error_obj

    def department_admin_check(self,empid_arr,depid):
        cond =Q(isadmin=True) & Q(department_id=depid)
        dep_admin_list=EmployeeDepartmentPermission.objects.using(self._current_app_schema()).filter(cond).values_list('employee_id',flat=True)

        admin = set(dep_admin_list) - set(empid_arr)
        last_admin = True
        if len(admin) > 0 :
            last_admin = False
        return last_admin



    def dep_to_emp_permission(self,depid,emparr,user_empid):
        empid_arr = emparr.get('employee_id')
        isadmin = emparr.get('isadmin')
        can_create = emparr.get('can_create')
        admin_check = self.admin_check(user_empid,depid)
        if admin_check:
            is_sys_check=self.is_sys_check(depid)
            if is_sys_check is False :

                if emparr.get('method') == 'add':

                    self.del_emp_to_dep(empid_arr,depid)
                    self.add_emp_to_dep(empid_arr,depid,isadmin,can_create)
                    success_obj = NWisefinSuccess()
                    success_obj.set_status(SuccessStatus.SUCCESS)
                    success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
                    return success_obj

                elif emparr.get('method') == 'remove':
                    last_admin = self.department_admin_check(empid_arr, depid)
                    if last_admin is False:
                        self.del_emp_to_dep(empid_arr, depid)
                        success_obj = NWisefinSuccess()
                        success_obj.set_status(SuccessStatus.SUCCESS)
                        success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
                        return success_obj
                    else:
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.EMPLOYEE_ADMIN)
                        error_obj.set_description(ErrorDescription.EMPLOYEE_ADMIN)
                        return error_obj


            elif is_sys_check is True :

                if emparr.get('method') == 'add':
                    self.del_emp_to_dep(empid_arr, depid)
                    self.add_emp_to_dep(empid_arr, depid, False, False)
                    success_obj = NWisefinSuccess()
                    success_obj.set_status(SuccessStatus.SUCCESS)
                    success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
                    return success_obj

                elif emparr.get('method') == 'remove':
                    last_admin = self.department_admin_check
                    if last_admin is False:
                        self.update_emp_to_dep(empid_arr, depid , False,False)
                        success_obj = NWisefinSuccess()
                        success_obj.set_status(SuccessStatus.SUCCESS)
                        success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
                        return success_obj
                    else:
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.EMPLOYEE_ADMIN)
                        error_obj.set_description(ErrorDescription.EMPLOYEE_ADMIN)
                        return error_obj

        else:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.EMPLOYEE_ADMIN)
            error_obj.set_description(ErrorDescription.EMPLOYEE_ADMIN)
            return error_obj

    def search_department_list(self, vys_page, query):
        if query is not None:
            con = Q(name__contains=query) & Q(status=1)
            departmentList = Department.objects.using(self._current_app_schema()).filter(con)[vys_page.get_offset():vys_page.get_query_limit()]
        else:
            con = Q(status=1)
            departmentList = Department.objects.using(self._current_app_schema()).filter(con).order_by('created_date')[vys_page.get_offset():vys_page.get_query_limit()]
        vlist = NWisefinList()
        for department in departmentList:
            dept_resp = DepartmentResponse()
            dept_resp.set_id(department.id)
            dept_resp.set_name(department.name)
            dept_resp.set_code(department.code)
            dept_resp.set_description(department.description)
            dept_resp.set_short_notation(department.short_notation)
            dept_resp.is_sys = department.is_sys
            vlist.append(dept_resp)
        vpage = NWisefinPaginator(departmentList, vys_page.get_index(), 10)
        vlist.set_pagination(vpage)
        return vlist


    def get_department_by_empid(self,emp_id):
        emp_dept_obj =EmployeeDepartmentPermission.objects.using(self._current_app_schema()).filter(employee_id=emp_id)
        arr = []
        for obj in emp_dept_obj:
            department =obj.department
            dept_data = {"name":department.name,"code":department.code,"id":department.id}
            arr.append(dept_data)
        return arr

    def get_department_by_branchid(self,branch_id):
        dept_data= Department.objects.using(self._current_app_schema()).filter(branch_id=branch_id,name=None,is_sys=True)

        if len(dept_data)>0:
            department=dept_data[0]
            dept_data = {"name": department.name, "code": department.code, "id": department.id}
        else:
            dept_data = {"name": None, "code": None, "id": None}
        return dept_data

    def get_department_by_empbranchid(self,emp_id):
        emp_branch =Employee.objects.using(self._current_app_schema()).get(id=emp_id).employee_branch_id
        if emp_branch == None:
            return

        dept_data = Department.objects.using(self._current_app_schema()).filter(branch_id=emp_branch, name=None, is_sys=True)
        if len(dept_data) > 0:
            department = dept_data[0]
            dept_data = {"name": department.name, "code": department.code, "id": department.id}
        else:
            dept_data = {"name": None, "code": None, "id": None}
        return dept_data
