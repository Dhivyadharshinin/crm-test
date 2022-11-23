import traceback

import django
from django.db import IntegrityError
from userservice.models.usermodels import RoleEmployee, RoleModule, Module, Role, Employee, EmployeeEntityMapping
# from userservice.models import RoleEmployee,RoleModule,VysfinMigrations,Module,Role , Employee ,BranchType, \
#     EmployeeDepartmentPermission,EmployeeBranch
from userservice.data.response.roleresponse import RoleEmployeeResponse,RoleModuleResponse
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinsuccess import SuccessStatus,SuccessMessage,NWisefinSuccess
from utilityservice.data.response.nwisefinlist import NWisefinList
from datetime import datetime
from django.core.cache import cache
from django.db.models import Q
from userservice.service.roleservice import RoleService
from userservice.service.moduleservice import ModuleService
from userservice.controller import cachecontroller
from userservice.data.response.roleresponse import RoleResponse
from userservice.data.response.moduleresponse import ModuleResponse
from userservice.data.userutil import ModifyStatus, rems_premission_type
from userservice.service.employeeservice import EmployeeService
from nwisefin.settings import logger
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace


class RoleEmployeeService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.USER_SERVICE)

    def create_roleemployee(self, roleemployee_obj, user_id):
        if not roleemployee_obj.get_id() is None:
            try:
                logger.error('ROLEEMPLOYEE: RoleEmployee Update Started')
                roleemployee_update = RoleEmployee.objects.using(self._current_app_schema()).filter(id=roleemployee_obj.get_id(), entity_id=self._entity_id()).update(
                                role_id=roleemployee_obj.get_role_id(),
                                employee_id=roleemployee_obj.get_employee_id(),
                                updated_date=datetime.now(),
                                updated_by=user_id)

                roleemployee = RoleEmployee.objects.using(self._current_app_schema()).get(id=roleemployee_obj.get_id(), entity_id=self._entity_id())
                # roleemployee catche update
                role_id = roleemployee.role_id
                roleemployee_roleid_catche_key = "roleemployee_" + "roleid_" + str(role_id)
                cachecontroller.update_cache(roleemployee_roleid_catche_key, roleemployee)

                emp_id = roleemployee.employee_id
                roleemployee_empid_catche_key = "roleemployee_" + "empid_" + str(emp_id)
                cachecontroller.update_cache(roleemployee_empid_catche_key, roleemployee)
                logger.error('ROLEEMPLOYEE: RoleEmployee Update Success' + str(roleemployee_update))

            except IntegrityError as error:
                logger.info('ERROR_RoleEmployeer_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except RoleEmployee.DoesNotExist:
                logger.info('ERROR_RoleEmployee_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_EMPLOYEEROLE_ID)
                error_obj.set_description(ErrorDescription.INVALID_EMPLOYEEROLE_ID)
                return error_obj
            except:
                logger.info('ERROR_RoleEmployee_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                logger.error('ROLEEMPLOYEE: RoleEmployee Creation Started')
                roleemployee = RoleEmployee.objects.using(self._current_app_schema()).create(role_id=roleemployee_obj.get_role_id(),
                                                     employee_id=roleemployee_obj.get_employee_id(),
                                                     created_by=user_id, entity_id=self._entity_id())
                logger.error('ROLEEMPLOYEE: RoleEmployee Creation Success' + str(roleemployee))
            except IntegrityError as error:
                logger.error('ERROR_RoleEmployee_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                logger.error('ERROR_RoleEmployee_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj

        roleemployee_data = RoleEmployeeResponse()
        roleemployee_data.set_id(roleemployee.id)
        roleemployee_data.set_role_id(roleemployee.role_id)
        roleemployee_data.set_employee_id(roleemployee.employee_id)
        return roleemployee_data

    def fetch_roleemployee_list(self):
        roleemployeelist = RoleEmployee.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id())
        list_length = len(roleemployeelist)
        if list_length <= 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_EMPLOYEEROLE_ID)
            error_obj.set_description(ErrorDescription.INVALID_EMPLOYEEROLE_ID)
            return error_obj
        else:
            roleemployee_list_data = NWisefinList()
            for roleemployeeobj in roleemployeelist:
                roleemployee_data = RoleEmployeeResponse()
                roleemployee_data.set_role_id(roleemployeeobj.role_id)
                roleemployee_data.set_employee_id(roleemployeeobj.employee_id)
                roleemployee_list_data.append(roleemployee_data)
            return roleemployee_list_data

    def fetch_role(self, employee_id):
        try:
            role_cache_key = "roleemployee_" + "empid_" + str(employee_id)
            roleemployee_obj = cachecontroller.get_cache(role_cache_key)
            if roleemployee_obj == None:
                roleemployee_obj = RoleEmployee.objects.using(self._current_app_schema()).values_list('role_id',flat=True).filter(employee_id=employee_id, entity_id=self._entity_id())
                cachecontroller.set_cache(role_cache_key, roleemployee_obj)

            return roleemployee_obj

        except RoleEmployee.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_EMPLOYEEROLE_ID)
            error_obj.set_description(ErrorDescription.INVALID_EMPLOYEEROLE_ID)
            return error_obj

    def delete_role(self, employee_id):
        roleemployee = RoleEmployee.objects.using(self._current_app_schema()).filter(id=employee_id, entity_id=self._entity_id()).delete()
        # role employee cache  delete
        roleemployee_cache_key = "roleemployee_" + "empid_" + str(employee_id)
        cachecontroller.delete_cache(roleemployee_cache_key)

        if roleemployee[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_EMPLOYEEROLE_ID)
            error_obj.set_description(ErrorDescription.INVALID_EMPLOYEEROLE_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj



    def fetch_employee(self, role_id):
        try:
            role_cache_key = "roleemployee_" + "roleid_" + str(role_id)
            role_obj = cachecontroller.get_cache(role_cache_key)
            if role_obj == None:
                role_obj = RoleEmployee.objects.using(self._current_app_schema()).values_list('employee_id', flat=True).filter(role_id=role_id, entity_id=self._entity_id())
                cachecontroller.set_cache(role_cache_key, role_obj)

            return role_obj
        except RoleEmployee.DoesNotExist:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_EMPLOYEEROLE_ID)
            error_obj.set_description(ErrorDescription.INVALID_EMPLOYEEROLE_ID)
            return error_obj

    def delete_employee(self, role_id):
        roleemployee = RoleEmployee.objects.using(self._current_app_schema()).filter(id=role_id, entity_id=self._entity_id()).delete()
        # roleemployee cache delete
        roleemployee_cache_key = "roleemployee_" + "roleid_" + str(role_id)
        cachecontroller.delete_cache(roleemployee_cache_key)

        if roleemployee[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_EMPLOYEEROLE_ID)
            error_obj.set_description(ErrorDescription.INVALID_EMPLOYEEROLE_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

    def role_module_employee(self,roll_obj,user_id):
            module_id = roll_obj.get_module_id()
            roll_module_list=RoleModule.objects.using(self._current_app_schema()).filter(Q(role_id=roll_obj.get_role_id())&Q(module_id=module_id)&Q(entity_id=self._entity_id())).order_by('-created_by')
            len_list=len(roll_module_list)
            if len_list==0:
                roll_module=RoleModule.objects.using(self._current_app_schema()).create(role_id=roll_obj.get_role_id(),module_id=roll_obj.get_module_id(),created_by=user_id, entity_id=self._entity_id())
                rollmodule_id=roll_module.id

                self.check_submodule(roll_obj,user_id)
            else:
                self.check_submodule(roll_obj,user_id)

                roll_module=roll_module_list[0]
                rollmodule_id=roll_module.id
            if not roll_obj.get_add() is None:
                for emp_id in roll_obj.get_add():
                    condition = Q(role_id=rollmodule_id) & Q(employee_id=emp_id) & Q(status=ModifyStatus.create) & Q(entity_id=self._entity_id())
                    rolemodule = RoleEmployee.objects.using(self._current_app_schema()).filter(condition)
                    if len(rolemodule) == 0:
                        RoleEmployee.objects.using(self._current_app_schema()).create(role_id=rollmodule_id,employee_id=emp_id,created_by=user_id,entity_id=self._entity_id())
            if not roll_obj.get_remove() is None:
                self.remove_check(roll_obj)
                for emp_id in roll_obj.get_remove():
                    for i in roll_module_list:
                        cond = Q(role_id=i.id) &Q(employee_id=emp_id) &Q(entity_id=self._entity_id())
                        RoleEmployee.objects.using(self._current_app_schema()).filter(cond).update(status=ModifyStatus.delete)

            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
            return success_obj



    def check_submodule(self,roll_obj,user_id):
        if roll_obj.get_add() is not None:
            module_id = roll_obj.get_module_id()
            role_id = roll_obj.get_role_id()
            module = Module.objects.using(self._current_app_schema()).get(id=module_id, entity_id=self._entity_id())
            refid = module.refid_id
            if not refid is None:
                cond = Q(module_id=refid)&Q(role_id=role_id)&Q(entity_id=self._entity_id())
                rel_module = RoleModule.objects.using(self._current_app_schema()).filter(cond).order_by('created_date').values_list('id',flat=True)

                if len(rel_module) == 0:
                    ref_roll_module = RoleModule.objects.using(self._current_app_schema()).create(role_id=role_id, module_id=refid,
                                                                created_by=user_id, entity_id=self._entity_id())
                    refrollmodule_id = ref_roll_module.id

                    for emp_id in roll_obj.get_add():
                        RoleEmployee.objects.using(self._current_app_schema()).create(role_id=refrollmodule_id, employee_id=emp_id,
                                                    created_by=user_id, entity_id=self._entity_id())

                else :
                    for emp_id in roll_obj.get_add():
                        condition = None
                        for i in rel_module:
                            if condition is None:
                                condition = Q(role_id__exact=i)&Q(employee_id=emp_id)&Q(status=ModifyStatus.create) &Q(entity_id=self._entity_id())
                            else:
                                condition |= Q(role_id__exact=i)&Q(employee_id=emp_id)&Q(status=ModifyStatus.create) &Q(entity_id=self._entity_id())

                        role_emp = RoleEmployee.objects.using(self._current_app_schema()).filter(condition)

                        if len(role_emp) == 0:

                            RoleEmployee.objects.using(self._current_app_schema()).create(role_id=rel_module[0], employee_id=emp_id,
                                                        created_by=user_id, entity_id=self._entity_id())


        return

    def remove_check(self,roll_obj):
        module_id = roll_obj.get_module_id()
        module = Module.objects.using(self._current_app_schema()).get(id=module_id, entity_id=self._entity_id())
        refid = module.refid_id
        if refid is None:
            submodule_obj=Module.objects.using(self._current_app_schema()).filter(refid_id=module_id, entity_id=self._entity_id()).values_list('id',flat=True)
            arr=[]
            for mod_id in submodule_obj:
                rel_module = RoleModule.objects.using(self._current_app_schema()).filter(module_id=mod_id, entity_id=self._entity_id()).values_list('id',flat=True)
                for id in rel_module:

                    arr.append(id)

            for emp_id in roll_obj.get_remove():
                for i in arr:
                    cond = Q(role_id=i) & Q(employee_id=emp_id) &Q(entity_id=self._entity_id())
                    RoleEmployee.objects.using(self._current_app_schema()).filter(cond).update(status=2)

        return

    def fetch_employee_module(self,employee_id,user_id):
        roll_emp = RoleEmployee.objects.using(self._current_app_schema()).filter(Q(employee_id=employee_id)&Q(status=1)&Q(entity_id=self._entity_id()))
        list_length = len(roll_emp)
        emp_list_data = NWisefinList()
        if list_length <= 0:
            pass
        else:
            for employee in roll_emp:
                employee_data = RoleModuleResponse()
                employee_data.set_id(employee.id)
                rollmodule=RoleModule.objects.using(self._current_app_schema()).get(id=employee.role_id, entity_id=self._entity_id())

                if rollmodule.role_id is not None:
                    role_service=RoleService(self._scope())
                    employee_data.set_role_id(role_service.fetch_role(rollmodule.role_id))
                else:
                    employee_data.set_role_id(None)
                if rollmodule.module_id is not None:
                    module_service=ModuleService(self._scope())
                    employee_data.set_module_id(module_service.fetch_module(rollmodule.module_id))
                else:
                    employee_data.set_module_id(None)
                emp_list_data.append(employee_data)
        return emp_list_data

    def fetch_employee_modulerole(self,roll_id,module_id,user_id):
        emp_module = RoleModule.objects.using(self._current_app_schema()).get(Q(role_id=roll_id) &Q(module_id=module_id)& Q(status=1) &Q(entity_id=self._entity_id()))
        emp_list_data = NWisefinList()
        rollmodule = RoleEmployee.objects.using(self._current_app_schema()).filter(role_id=emp_module.id, entity_id=self._entity_id())
        for employee in rollmodule:
            if employee.employee_id is not None:
                employee_service = EmployeeService(self._scope())
                employee_data=employee_service.get_employee(employee.employee_id,user_id)
            else:
                employee_data=None
            emp_list_data.append(employee_data)
        return emp_list_data


    # def start_migrations(self,user_id):
    #     try:
    #         module_name=['e-Memo','Master']
    #         module_logo=['fa fa-sitemap','fa fa-cog']
    #         module_url=['/memosummary','/master']
    #         role_name=['Maker','Checker','Approver']
    #         operation_name=['Maker','Checker','Approver']
    #         role_code=['C001','C002','C003']
    #         migration_obj=VysfinMigrations.objects.all()
    #         len_list=len(migration_obj)
    #         if len_list==0:
    #             migrations=VysfinMigrations.objects.create(migration_id=0)
    #             migration_id = migrations.migration_id
    #             mig_id = migrations.id
    #         else:
    #             mig_obj=migration_obj[0]
    #             migration_id=mig_obj.migration_id
    #             mig_id=mig_obj.id
    #         if migration_id==0:
    #             for modulename in module_name:
    #                 try:
    #                     index_value=module_name.index(modulename)
    #                     module_obj=Module.objects.create(name=modulename,logo=index_value+1,url=module_url[index_value],created_by=user_id)
    #                 except:
    #                     error_obj = NWisefinError()
    #                     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
    #                     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
    #                     return error_obj
    #             for rolename in role_name:
    #                 try:
    #                     index_value = role_name.index(rolename)
    #                     role_obj=Role.objects.create(code=role_code[index_value],name=rolename,operation_name=operation_name[index_value],created_by=user_id)
    #                 except:
    #                     error_obj = NWisefinError()
    #                     error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
    #                     error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
    #                     return error_obj
    #             migrations_update = VysfinMigrations.objects.filter(id=mig_id).update(migration_id=1,status=True)
    #         else:
    #             error_obj = NWisefinError()
    #             error_obj.set_code(ErrorMessage.MIGRATIONS_STATUS)
    #             error_obj.set_description(ErrorDescription.MIGRATIONS_STATUS)
    #             return error_obj
    #     except:
    #         error_obj = NWisefinError()
    #         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
    #         error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
    #         return error_obj
    #     success_obj = NWisefinSuccess()
    #     success_obj.set_status(SuccessStatus.SUCCESS)
    #     success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
    #     return success_obj


    def fetch_employee_submodule(self,user_id,userid_check):
        if userid_check == False :
            employee_id = user_id
        elif userid_check == True:
            employee = Employee.objects.get(id=user_id)
            employee_id = employee.id

        role_emp=RoleEmployee.objects.using(self._current_app_schema()).filter(Q(employee_id=employee_id)&Q(status=1)&Q(entity_id=self._entity_id()))
        list_length = len(role_emp)
        emp_list_data = NWisefinList()
        if list_length <= 0:
            pass
        else:
            arr = []
            moduleid_arr=[]
            for employee in role_emp:
                employee_data = RoleModuleResponse()
                employee_data.set_id(employee.id)
                # rolemodule=RoleModule.objects.get(id=employee.role_id)
                rolemodule = employee.role

                if rolemodule.module_id is not None and rolemodule.module_id not in moduleid_arr:
                        moduleid_arr.append(rolemodule.module_id)
                        module_obj=rolemodule.module
                        role_obj=rolemodule.role
                        module_data = self.module_response(module_obj)
                        role_data = self.role_response(role_obj)
                        module_data.role = [role_data]
                        submodule_array = []
                        module_data.submodule=submodule_array
                        if module_obj.refid_id is not None:
                            module_data.refid_id = module_obj.refid_id
                            arr.append(module_data)
                        else:
                            emp_list_data.append(module_data)
                elif rolemodule.module_id in moduleid_arr :
                    check = False
                    mod_id = rolemodule.module_id
                    for i in emp_list_data.data:
                        if i.id == mod_id:
                            role_obj = rolemodule.role
                            role_data = self.role_response(role_obj)
                            i.role.append(role_data)
                            check = True
                            break
                    if check == False:
                        for j in arr :
                            if j.id == mod_id:
                                role_obj = rolemodule.role
                                role_data = self.role_response(role_obj)
                                j.role.append(role_data)
                                break

                else:
                    employee_data.set_module_id(None)
                    emp_list_data.append(employee_data)
            for sub in arr:
                submodule_refid = sub.refid_id
                for module in emp_list_data.data:
                    module_id = module.id
                    if submodule_refid == module_id:
                        del sub.submodule
                        del sub.refid_id
                        module.submodule.append(sub)

            # for mod in emp_list_data.data:
            #     if mod.name == 'e-Memo':
            #         emp_service = EmployeeService()
            #         sub_mod = emp_service.sub_module_memo(user_id)
            #         mod.submodule =sub_mod
            #         break


        return emp_list_data


    def role_response(self,role_obj):
        role_data = RoleResponse()
        role_data.set_id(role_obj.id)
        role_data.set_code(role_obj.code)
        role_data.set_name(role_obj.name)
        return role_data

    def module_response(self,module_obj):
        module_data = ModuleResponse()
        module_data.set_id(module_obj.id)
        module_data.set_name(module_obj.name)
        module_data.set_logo(module_obj.logo)
        module_data.set_url(module_obj.url)
        module_name = module_obj.name
        mod_name = module_name.casefold()
        if mod_name.__contains__('master'):
            module_data.type = "master"
        else:
            module_data.type = "transaction"

        return module_data

    def premission_all(self,data,user_id):
        employee = EmployeeEntityMapping.objects.using('default').filter(entity_id=self._entity_id())

        role_id = data.get('role_id')
        module_id = data.get('module_id')
        for mod_id in module_id:
            roll_module_list = RoleModule.objects.using(self._current_app_schema()).filter(
                Q(role_id=role_id) & Q(module_id=mod_id) &Q(entity_id=self._entity_id())).order_by('-created_by')
            len_list = len(roll_module_list)
            if len_list == 0:
                roll_module = RoleModule.objects.using(self._current_app_schema()).create(role_id=role_id,
                                                        module_id=mod_id, created_by=user_id, entity_id=self._entity_id())
                rollmodule_id = roll_module.id

            else:
                roll_module = roll_module_list[0]
                rollmodule_id = roll_module.id

            for obj in employee:
                emp = obj.employee
                emp_id = emp.id
                condition = Q(role_id=rollmodule_id) & Q(employee_id=emp_id) & Q(status=ModifyStatus.create) &Q(entity_id=self._entity_id())
                rolemodule = RoleEmployee.objects.using(self._current_app_schema()).filter(condition)
                if len(rolemodule) == 0:
                        RoleEmployee.objects.using(self._current_app_schema()).create(role_id=rollmodule_id, employee_id=emp_id, created_by=user_id, entity_id=self._entity_id())

        return

    # def premission_remove(self,data):
    #     logger.info('premission_remove')
    #     role_id = data.get('role_id')
    #     module_id = data.get('module_id')
    #     role_module_id = RoleModule.objects.get(role_id=role_id, module_id=module_id).id
    #     logger.info(str(role_id)+str(module_id)+str(role_module_id))
    #     dept_id=BranchType.objects.all().values_list('department_id',flat=True)
    #
    #     for i in dept_id:
    #         employee_id=EmployeeDepartmentPermission.objects.filter(department_id=i).values_list('employee_id',flat=True)
    #
    #         for emp_id in employee_id :
    #             cond = Q(role_id=role_module_id) & Q(employee_id=emp_id)
    #             RoleEmployee.objects.filter(cond).update(status=ModifyStatus.delete)
    #     return

    # def rems_premission(self,data,emp_id):
    #
    #     module_id = data.get_module_id()
    #     role_id = data.get_role_id()
    #     emp_add = data.get_add()
    #     emp_remove = data.get_remove()
    #     emp_arr = self.employee_classification_with_role(emp_add)
    #
    #     role_module_list = RoleModule.objects.using('default').filter(Q(role_id=role_id) & Q(module_id=module_id))
    #     len_role_module_list = len(role_module_list)
    #     if len_role_module_list == 0:
    #         role_module = RoleModule.objects.using('default').create(role_id=role_id, module_id=module_id,
    #                                                 created_by=emp_id)
    #         rolemodule_id = role_module.id
    #
    #         self.check_submodule(data, emp_id)
    #     else:
    #         self.check_submodule(data, emp_id)
    #
    #         role_module = role_module_list[0]
    #         rolemodule_id = role_module.id
    #
    #     if not emp_add is None:
    #         emp_arr = self.employee_classification_with_role(emp_add)
    #         for emp in emp_arr:
    #             condition = Q(role_id=rolemodule_id) & Q(employee_id=emp) & Q(status=ModifyStatus.create)
    #             rolemodule = RoleEmployee.objects.filter(condition)
    #             if len(rolemodule) == 0:
    #                 RoleEmployee.objects.create(role_id=rolemodule_id, employee_id=emp, created_by=emp_id)
    #     if not emp_remove is None:
    #         emp_arr = self.employee_classification_with_role(emp_add)
    #         self.remove_check(data)
    #         for emp in emp_arr:
    #             for i in role_module_list:
    #                 cond = Q(role_id=i.id) & Q(employee_id=emp)
    #                 RoleEmployee.objects.filter(cond).update(status=ModifyStatus.delete)
    #
    #     return

    # def employee_classification_with_role(self,role_type):
    #     emp_arr=[]
    #     for i in role_type :
    #         if i == rems_premission_type.branch:
    #             emp_obj=EmployeeDepartmentPermission.objects.filter(department__name=None).values_list('employee_id',flat=True)
    #             emp_obj=set(emp_obj)
    #             emp_arr.extend(emp_obj)
    #         if i == rems_premission_type.do:
    #             emp_obj=Employee.objects.filter(employee_branch__name__contains='D.O').values_list('id',flat=True)
    #             emp_obj = set(emp_obj)
    #             emp_arr.extend(emp_obj)
    #         if i == rems_premission_type.emc:
    #             emp_obj=Employee.objects.filter(code__contains='vsolv').values_list('id',flat=True)
    #             emp_arr.extend(emp_obj)
    #         if i == rems_premission_type.estate_cell:
    #             branch_id = EmployeeBranch.objects.get(code=1101).id
    #             condition = Q(department__branch_id=branch_id)&Q(department__name='ESTC')
    #             emp_obj = EmployeeDepartmentPermission.objects.filter(condition).values_list('employee_id',flat=True)
    #             emp_obj = set(emp_obj)
    #             emp_arr.extend(emp_obj)
    #
    #     return emp_arr


    def fetch_employee_role(self,emp_id,module):

        module_arr=RoleEmployee.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),status=1,employee_id=emp_id,role__module__name=module).values_list('role__role__name',flat=True)
        module_arr = set(module_arr)
        module_arr= list(module_arr)
        return module_arr


    def fetch_employees_by_role(self,module,emp_role,emp_id):
        module_arr=RoleEmployee.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),status=1,
                                     role__module__name=module,role__role__name=emp_role).exclude(employee__email_id__isnull=True).exclude(employee__email_id="").values_list('employee__email_id',flat=True)
        print('module_arr_query ',module_arr.query)
        return module_arr
