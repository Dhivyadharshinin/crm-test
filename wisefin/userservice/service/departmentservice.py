import traceback

from django.db import IntegrityError
from django.db.models import Q
from django.utils.timezone import now

from masterservice.util.masterutil import MasterStatus
from userservice.data.response.departmentresponse import DepartmentResponse
from userservice.models import Department ,EmployeeDepartmentPermission,Employee
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from userservice.controller import cachecontroller
from utilityservice.permissions.util.dbutil import Status
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinsuccess import SuccessStatus,SuccessMessage,NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from userservice.service.employeedepartmentservice import EmployeeDepartmentService
from userservice.service.employeeservice import EmployeeService
from userservice.service.branchservice import EmployeeBranchService
from nwisefin.settings import logger
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace


class DepartmentService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.USER_SERVICE)

    def create_department(self, dept_obj, user_id):
        dept_resp = DepartmentResponse()
        if not dept_obj.get_id() is None:
            try:
                logger.error('DEPARTMENT: Department Update Started')
                department = Department.objects.using(self._current_app_schema()).filter(id=dept_obj.get_id()).update(name=dept_obj.get_name(),
                                                                             description=dept_obj.get_description(),
                                                                             short_notation=dept_obj.get_short_notation(),
                                                                             updated_by=user_id,
                                                                             updated_date=now())
                department = Department.objects.using(self._current_app_schema()).get(id=dept_obj.get_id())

                # department catche update
                dep_id = dept_obj.get_id()
                department_cache_key = "department_depid_" + str(dep_id)
                cachecontroller.update_cache(department_cache_key, department)
                logger.error('DEPARTMENT: Department Update Success' + str(department))

            except IntegrityError as error:
                logger.info('ERROR_Department_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj

            except Department.DoesNotExist:
                logger.info('ERROR_Department_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_Address_ID)
                error_obj.set_description(ErrorDescription.INVALID_Address_ID)
                return error_obj
            except:
                logger.info('ERROR_Department_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                logger.error('DEPARTMENT: Department Creation Started')
                # condition = Q(name__exact=dept_obj.get_name())
                # subcat = Department.objects.filter(condition)
                # if len(subcat) > 0:
                #     error_obj = Error()
                #     error_obj.set_code(ErrorDescription.DUPLICATE_NAME)
                #     error_obj.set_description(ErrorDescription.DUPLICATE_NAME)
                #     return error_obj
                try:
                    branchobj=Employee.objects.get(id=user_id)
                    branch_id=branchobj.employee_branch_id
                except:
                    branch_id=None
                data_len=Department.objects.using(self._current_app_schema()).filter(name=dept_obj.get_name()).values()
                if(len(data_len)>0):
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVALID_DATA)
                    error_obj.set_description(ErrorDescription.DUPLICATE_NAME)
                    return error_obj
                department = Department.objects.using(self._current_app_schema()).create(name=dept_obj.get_name(),
                            description=dept_obj.get_description(),short_notation=dept_obj.get_short_notation(),branch_id=branch_id,
                            created_by=user_id)
                code = "DGRP" + str(department.id)
                department.code = code
                department.save()
                logger.error('DEPARTMENT: Department Creation Success' + str(department))

                permission_service =EmployeeDepartmentService(self._scope())
                permission_service.emp_dep_perm_from_department(user_id,department.id)

                dept_resp.set_id(department.id)
                dept_resp.set_name(department.name)
                dept_resp.set_code(department.code)
                dept_resp.set_description(department.description)
                dept_resp.set_short_notation(department.short_notation)
                return dept_resp
            except IntegrityError as error:
                logger.error('ERROR_Department_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except :
                logger.error('ERROR_Department_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj


        return dept_resp


    def fetch_internal_department(self,dept_id):
        try:
            department = Department.objects.using(self._current_app_schema()).get(id=dept_id)
            dept_resp = DepartmentResponse()
            dept_resp.set_id(department.id)
            dept_resp.set_name(department.name)
            dept_resp.set_code(department.code)
            dept_resp.set_description(department.description)
            dept_resp.set_short_notation(department.short_notation)
            dept_resp.set_branch(department.branch_id)
            return dept_resp
        except:
            return None


    def fetch_department(self, dept_id, user_id):
        try:
            department_cache_key = "department_depid_" + str(dept_id)
            department = cachecontroller.get_cache(department_cache_key)
            logger.info('cache')
            if department == None:
                department = Department.objects.using(self._current_app_schema()).get(id=dept_id)
                cachecontroller.set_cache(department_cache_key, department)
                logger.info('db')

            emp_service = EmployeeService(self._scope())
            condition=Q(employee_id=user_id)&Q(department_id=dept_id)
            try:
                emp_dep = EmployeeDepartmentPermission.objects.using(self._current_app_schema()).get(condition)
                isadmin = emp_dep.isadmin
            except:
                isadmin = False

            # department = Department.objects.get(id=dept_id)
            dept_resp = DepartmentResponse()
            dept_resp.set_id(department.id)
            dept_resp.set_name(department.name)
            dept_resp.set_code(department.code)
            if department.branch_id is not None:
                branch_service = EmployeeBranchService(self._scope())
                branch_data = branch_service.fetch_branch(department.branch_id)
                dept_resp.set_branch(branch_data)
            else:
                dept_resp.set_branch(None)
            dept_resp.set_description(department.description)
            dept_resp.set_short_notation(department.short_notation)
            dept_resp.is_sys = department.is_sys
            dept_resp.isadmin = isadmin
            return dept_resp
        except IntegrityError as error:
            pass
        except Department.DoesNotExist:
            pass
        except:
            pass

    def fetch_department_list(self, vys_page, user_id,search_key):
        try:
            if search_key is not None:
                departmentList =  Department.objects.using(self._current_app_schema()).filter(name__contains=search_key)[vys_page.get_offset():vys_page.get_query_limit()]
            else :
                departmentList = Department.objects.using(self._current_app_schema()).all().order_by('created_date')[vys_page.get_offset():vys_page.get_query_limit()]
            vlist = NWisefinList()
            for department in departmentList:
                dept_resp = DepartmentResponse()
                dept_resp.set_id(department.id)
                dept_resp.set_name(department.name)
                dept_resp.set_code(department.code)
                if department.branch_id is not None:
                    branch_service = EmployeeBranchService(self._scope())
                    branch_data = branch_service.fetch_branch(department.branch_id)
                    dept_resp.set_branch(branch_data)
                else:
                    dept_resp.set_branch(None)
                dept_resp.set_description(department.description)
                dept_resp.set_short_notation(department.short_notation)
                dept_resp.is_sys = department.is_sys
                vlist.append(dept_resp)
            vpage = NWisefinPaginator(departmentList, vys_page.get_index(), 10)
            vlist.set_pagination(vpage)
            return vlist
        except:
            logger.error('ERROR Department Summary EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_DATA)
            return error_obj
    def fetch_department_download(self, user_id,search_key):
        try:
            if search_key is not None:
                departmentList = Department.objects.using(self._current_app_schema()).filter(name__contains=search_key)
            else:
                departmentList = Department.objects.using(self._current_app_schema()).all().order_by('created_date')
            vlist = NWisefinList()
            for department in departmentList:
                dept_resp = DepartmentResponse()
                try:
                    dept_resp.Name = department.name
                except:
                    dept_resp.Name = ""
                try:
                    dept_resp.Code = department.code
                except:
                    dept_resp.Code = ""
                if department.branch_id is not None:
                    branch_service = EmployeeBranchService(self._scope())
                    branch_data = branch_service.fetch_branch(department.branch_id)
                    dept_resp.Branch_Name = branch_data.name
                else:
                    dept_resp.Branch_Name = ""
                try:
                    dept_resp.Description = department.description
                except:
                    dept_resp.Description = ""
                try:
                    dept_resp.Short_Notation = department.short_notation
                except:
                    dept_resp.Short_Notation = ""
                status = MasterStatus()
                if department.status == status.Active:
                    dept_resp.Status = status.Active_VALUE
                if department.status == status.Inactive:
                    dept_resp.Status = status.Inactive_VALUE
                # dept_resp.is_sys = department.is_sys
                vlist.append(dept_resp)
            return vlist
        except:
            logger.error('ERROR Department Excel Download Summary EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_DATA)
            return error_obj


    def delete_department(self, dept_id):
        try :
            Department.objects.using(self._current_app_schema()).filter(id=dept_id).delete()
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

        except:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.Department_ID)
            error_obj.set_description(ErrorDescription.Department_ID)
            return error_obj




    def search_department(self, dept_id, user_id):
        department = Department.objects.using(self._current_app_schema()).values('id','code','name').get(id=dept_id)
        dept_resp = DepartmentResponse()
        dept_resp.set_name(department['name'])
        dept_resp.set_code(department['code'])
        dept_resp.set_id(department['id'])
        return dept_resp


    def search_department_list(self, request, query, vys_page, is_master):
        condition = None
        if query is not None:
            condition = (Q(name__icontains = query)|Q(branch__name__icontains=query)|Q(branch__code__icontains=query))
        if query=='':
            condition=None
        departmentList = None
        # memo dept search
        if is_master  is None:
            if condition is not None:
                condition &= Q(status=1)
                departmentList = Department.objects.using(self._current_app_schema()).values('id','code', 'name','branch_id').filter(condition).order_by('created_date')[
                                 vys_page.get_offset():vys_page.get_query_limit()]
            else:
                departmentList = Department.objects.using(self._current_app_schema()).values('id','code', 'name','branch_id').filter(status=1).order_by('created_date')[
                                 vys_page.get_offset():vys_page.get_query_limit()]
        # common dept search
        else :
            if condition is not None:
                departmentList = Department.objects.using(self._current_app_schema()).values('id', 'code', 'name', 'branch_id').filter(
                    condition).order_by('created_date')[
                                 vys_page.get_offset():vys_page.get_query_limit()]
            else:
                departmentList = Department.objects.using(self._current_app_schema()).values('id', 'code', 'name', 'branch_id').all().order_by(
                    'created_date')[
                                 vys_page.get_offset():vys_page.get_query_limit()]
        vlist = NWisefinList()
        for department in departmentList:
            dept_resp = DepartmentResponse()
            branch_service = EmployeeBranchService(self._scope())
            branch_id = department['branch_id']
            if branch_id==None:
                dept_resp.set_name(department['name'])
            else:
                branch_data = branch_service.fetch_branch(branch_id)
                branch_code = branch_data.code
                branch_name = branch_data.name
                branch_name1 = '(' + branch_code + ') ' + branch_name
                if department['name'] == None:
                    dept_name = branch_name1
                else:
                    dept_name = branch_name1 + ' (' + department['name'] + ')'
                dept_resp.set_name(dept_name)

            dept_resp.set_code(department['code'])
            dept_resp.set_id(department['id'])
            vlist.append(dept_resp)
        vpage = NWisefinPaginator(departmentList, vys_page.get_index(), 10)
        vlist.set_pagination(vpage)
        return vlist

    def get_department(self, dept_id):
        department_cache_key = "department_depid_" + str(dept_id)
        department = cachecontroller.get_cache(department_cache_key)
        logger.info('cache')
        if department == None:
            department = Department.objects.using(self._current_app_schema()).get(id=dept_id)
            cachecontroller.set_cache(department_cache_key, department)
            logger.info('db')

        return department

    def department_isactive(self, dep_id):
        try:
            department = Department.objects.using(self._current_app_schema()).get(id=dep_id)
            if department.status == Status.create:
                active = True
            else:
                active = False
            return active
        except:
            active = False
            return active

    def multi_department_isactive(self,dep_id):
        condition = None
        for id in dep_id:
            if condition is None:
                condition = Q(id__exact=id) & Q(status=Status.create)
            else:
                condition |= Q(id__exact=id)& Q(status=Status.create)

        department_status = Department.objects.using(self._current_app_schema()).values_list('id',flat=True).filter(condition)

        for i in dep_id:
            if i in department_status:
                active = True
            else:
                active = False
                break

        return active

    def create_department_sys(self,dept_obj,empid):
        department = Department.objects.using(self._current_app_schema()).create(name=dept_obj.get_name(),
                                               description=dept_obj.get_description(),
                                               short_notation=dept_obj.get_short_notation(),
                                               is_sys=True,
                                               created_by=empid)
        code = "DGRP" + str(department.id)
        department.code = code
        department.save()
        dept_resp = DepartmentResponse()
        dept_resp.set_id(department.id)
        dept_resp.set_name(department.name)
        dept_resp.set_code(department.code)
        dept_resp.set_description(department.description)
        dept_resp.set_short_notation(department.short_notation)
        dept_resp.is_sys = department.is_sys
        return dept_resp

    def search_department_type(self,employee_id,type,query,vys_page):

        if type == 'memo':
            if query is not None:
                condition = Q(can_create=True) & Q(employee_id=employee_id) & (Q(
                    department__name__icontains=query)|Q(department__branch__name__icontains=query)|Q(department__branch__code__icontains=query))&Q(department__status=1)
            else:
                condition = Q(can_create=True) & Q(employee_id=employee_id)&Q(department__status=1)
        elif type == 'admin':
            if query == None or query == '':
                condition = Q(isadmin=True) & Q(employee_id=employee_id)

            else:
                condition = Q(isadmin=True) & (Q(employee_id=employee_id) & Q(
                    department__name__icontains=query)|Q(department__branch__name__icontains=query)|Q(department__branch__code__icontains=query))
        elif type == 'all' or type == None:
            if query==None or query=='':
                condition = Q(employee_id=employee_id)
            else:
                condition = Q(employee_id=employee_id) & (Q(department__name__icontains=query)|Q(department__branch__name__icontains=query)|Q(department__branch__code__icontains=query))

        # else:
        #     condition = Q(employee_id=employee_id) & Q(department__name__icontains=query)

        departmentobj = EmployeeDepartmentPermission.objects.using(self._current_app_schema()).filter(condition)[vys_page.get_offset():vys_page.get_query_limit()]

        departmentList = []
        for i in departmentobj:
            if i.department_id is not None:
                dept = i.department
                dept.can_create = i.can_create
                dept.isadmin = i.isadmin
                departmentList.append(dept)

        vlist = NWisefinList()
        for department in departmentList:
            dept_resp = DepartmentResponse()
            dept_resp.set_id(department.id)
            branch_id = department.branch_id
            if branch_id==None:
                dept_resp.set_name(department.name)
            else:
                branch_service = EmployeeBranchService(self._scope())
                branch_data = branch_service.fetch_branch(branch_id)
                branch_code=branch_data.code
                branch_name=branch_data.name
                branch_name1='('+branch_code+') '+branch_name
                if department.name==None:
                    dept_name=branch_name1
                else:
                    dept_name = branch_name1+' ('+department.name+')'
                dept_resp.set_name(dept_name)
            dept_resp.set_code(department.code)
            dept_resp.set_description(department.description)
            dept_resp.set_short_notation(department.short_notation)
            dept_resp.isadmin = department.isadmin
            dept_resp.can_create = department.can_create
            vlist.append(dept_resp)
        vpage = NWisefinPaginator(departmentList, vys_page.get_index(), 10)
        vlist.set_pagination(vpage)

        return vlist


    def get_dept_branch_name(self,dept_id):
        department = Department.objects.using(self._current_app_schema()).get(id=dept_id)
        dept_name = department.name
        branch = department.branch
        if branch is not None:
            branch_code = branch.code
            branch_name = branch.name
            branch_name_code = '(' + branch_code + ') ' + branch_name
            if dept_name == None:
                dept_name = branch_name_code
            else:
                dept_name = branch_name_code + ' (' + dept_name + ')'
            dept = {'id': department.id, 'name': dept_name}

        else:
            dept = {'id': department.id, 'name': dept_name}

        return dept

    def fetch_department_name(self,name,Entity):
        dep = Department.objects.using(self._current_app_schema()).filter(name__iexact=name,entity_id=Entity)
        if len(dep) > 0:
            dept_id = dep[0].id
            return dept_id
        else:
            dep = Department.objects.using(self._current_app_schema()).create(name=name,entity_id=Entity)
            try:
                max_cat_code = Department.objects.using(self._current_app_schema()).filter(code__icontains='DGRP').order_by('-code')[0].code
                rnsl = int(max_cat_code[3:])
            except:
                rnsl = 0
            new_rnsl = rnsl + 1
            code = "DGRP" + str(new_rnsl).zfill(3)
            dep.code = code
            dep.save()
            return dep.id

