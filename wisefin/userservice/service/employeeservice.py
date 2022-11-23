import traceback
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from userservice.data.response.addresscontactresponse import AddressResponse
from userservice.data.userutil import employee_team_ta
from userservice.models.usermodels import Employee, EmployeeBranch, Department, EmployeeDepartmentPermission, \
    EmployeeAddress, BusinessSegment, EmployeeEntityMapping, EmployeeAccountDetails, EmployeeReportAproval
from nwisefin.settings import logger
import json
from django.db import IntegrityError
from django.utils.timezone import now
from userservice.controller import cachecontroller
from userservice.data.response.employeeresponse import EmployeeResponse, empdepartmentres
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinlitelist import NWisefinLiteList
from utilityservice.data.response.nwisefinuser import NWisefinUser
from utilityservice.data.response.nwisefinerror import NWisefinError as Error, NWisefinError
from django.db.models import Q, Count
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinsuccess import SuccessStatus,SuccessMessage,NWisefinSuccess
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from userservice.data.response.branchresponse import EmployeeBranchResponse
from userservice.data.response.departmentresponse import DepartmentResponse
from utilityservice.permissions.util.dbutil import Status
from utilityservice.data.response.nwisefinsearch import NwisefinSearch
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from userservice.service.branchservice import EmployeeBranchService
from django.http import HttpResponse
from userservice.data.response.employeeresponse import Employee_data_resp
# from utilityservice.service.api_service import ApiService
from wisefinapi.masterapi import MasterAPI
from masterservice.service.leaveattendanceservice import OrgDetailsService
class EmployeeService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.USER_SERVICE)

    def get_empid_from_userid(self, user_id):
        employee_cache_key = "employee_" + "userid_" + str(user_id)
        employee = cachecontroller.get_cache(employee_cache_key)
        logger.info('cache')
        if employee == None:
            employee = Employee.objects.get(id=user_id)
            cachecontroller.set_cache(employee_cache_key, employee)
            logger.info('db')

        employee_id = employee.id
        return employee_id

    def get_employee(self, emp_id, user_id):
        employee_cache_key = "employee_" + "empid_" + str(emp_id)
        employee = cachecontroller.get_cache(employee_cache_key)
        logger.info('cache')

        if employee == None:
            employee = Employee.objects.using('default').get(id=emp_id)
            cachecontroller.set_cache(employee_cache_key, employee)
            logger.info('db')

        emp_resp = EmployeeResponse()
        emp_resp.set_id(employee.id)
        emp_resp.set_first_name(employee.first_name)
        emp_resp.set_middle_name(employee.middle_name)
        emp_resp.set_last_name(employee.last_name)
        emp_resp.set_full_name(employee.full_name)
        emp_resp.set_code(employee.code)
        emp_resp.set_grade(employee.grade)
        emp_resp.set_designation(employee.designation)
        emp_resp.set_user(employee.user_id)

        # emp_resp.set_dob(employee.dob)
        # emp_resp.set_doj(employee.doj)
        # emp_resp.set_gender(employee.gender)
        # emp_resp.set_phone_no(employee.phone_no)
        # emp_resp.set_employee_type(employee.employee_type)
        # emp_resp.set_supervisor(employee.supervisor)
        # emp_resp.set_hierarchy(employee.hierarchy)
        emp_resp.set_branch(employee.branch)
        # emp_resp.set_employee_branch_id(employee.employee_branch_id)
        # emp_resp.set_costcentre(employee.costcentre)
        # emp_resp.set_businesssegment(employee.businesssegment)
        # emp_resp.set_address_id(employee.address_id)
        # emp_resp.set_contact_id(employee.contact_id)

        return emp_resp

    def get_full_employee_info(self, emp_id, user_id):
        employee_cache_key = "employee_" + "empid_" + str(emp_id)
        employee = cachecontroller.get_cache(employee_cache_key)
        logger.info('cache')

        if employee == None:
            employee = Employee.objects.using('default').get(id=emp_id)
            cachecontroller.set_cache(employee_cache_key, employee)
            logger.info('db')

        emp_resp = EmployeeResponse()
        emp_resp.set_id(employee.id)
        emp_resp.set_first_name(employee.first_name)
        emp_resp.set_middle_name(employee.middle_name)
        emp_resp.set_last_name(employee.last_name)
        emp_resp.set_full_name(employee.full_name)
        emp_resp.set_code(employee.code)
        emp_resp.set_grade(employee.grade)
        emp_resp.set_designation(employee.designation)
        emp_resp.set_user(employee.user_id)

        emp_resp.set_dob(employee.dob)
        emp_resp.set_doj(employee.doj)
        emp_resp.set_gender(employee.gender)
        emp_resp.set_phone_no(employee.phone_no)
        emp_resp.set_employee_type(employee.employee_type)
        emp_resp.set_supervisor(employee.supervisor)
        emp_resp.set_hierarchy(employee.hierarchy)
        emp_resp.set_branch(employee.branch)
        emp_resp.set_employee_branch_id(employee.employee_branch_id)
        emp_resp.set_costcentre(employee.costcentre)
        emp_resp.set_businesssegment(employee.businesssegment)
        emp_resp.set_address_id(employee.address_id)
        emp_resp.set_contact_id(employee.contact_id)

        return emp_resp


    def get_emp_dropdn(self, vys_page, data):
        emp_dpdn = EmployeeEntityMapping.objects.using(self._current_app_schema()).filter(employee__full_name__contains=data, entity_id=self._entity_id())[
                   vys_page.get_offset():vys_page.get_query_limit()]
        vlist = NWisefinList()
        for obj in emp_dpdn:
            employee = obj.employee
            emp_resp = EmployeeResponse()
            emp_resp.set_id(employee.id)
            emp_resp.set_full_name(employee.full_name)
            vlist.append(emp_resp)
        vpage = NWisefinPaginator(emp_dpdn, vys_page.get_index(), 10)
        vlist.set_pagination(vpage)
        return vlist
    def employee_info_by_id(self, user_arr):
        condition = None
        user_list = None
        for user_id in user_arr:
            if condition is None:
                condition = Q(employee__id__exact=user_id)
            else:
                condition |= Q(employee__id__exact=user_id)
        if condition is not None:
            user_list = EmployeeEntityMapping.objects.using('default').filter(condition)
        resp_list = NWisefinList()
        if user_list is not None:
            for obj in user_list:
                user = obj.employee
                user_obj = NWisefinUser()
                user_obj.set_id(user.id)
                disp_name = '(' + user.code + ') ' + user.full_name
                user_obj.set_full_name(disp_name)
                user_obj.set_designation(user.designation)
                resp_list.append(user_obj)
        return resp_list.get()

    def get_employee_from_userid(self, user_id):
        employee_cache_key = "employee_" + "userid_" + str(user_id)
        employee = cachecontroller.get_cache(employee_cache_key)
        logger.info('cache')
        if employee == None:
            employee = Employee.objects.get(user_id=user_id)
            cachecontroller.set_cache(employee_cache_key, employee)
            logger.info('db')

        return employee
    def get_employee_RMID(self, employee_id):
        # employee_cache_key = "employee_" + "userid_" + str(employee_id)
        # employee = cachecontroller.get_cache(employee_cache_key)
        # logger.info('cache')
        if employee_id != None:
            employee = Employee.objects.get(id=employee_id)
            # cachecontroller.set_cache(employee_cache_key, employee)
            # logger.info('db')
            employee_rm=employee.RM

        return employee_rm

    def get_rm_employee(self, employee_id):
        # employee_cache_key = "employee_" + "userid_" + str(employee_id)
        # employee = cachecontroller.get_cache(employee_cache_key)
        # logger.info('cache')
        if employee_id != None:
            employee = Employee.objects.filter(RM=employee_id)
            arr=[]
            for data in employee:
            # cachecontroller.set_cache(employee_cache_key, employee)
            # logger.info('db')
                arr.append(data.id)

        return arr

    def get_employee_functionalhead(self, employee_id):
        # employee_cache_key = "employee_" + "userid_" + str(employee_id)
        # employee = cachecontroller.get_cache(employee_cache_key)
        # logger.info('cache')
        if employee_id != None:
            employee = Employee.objects.get(id=employee_id)
            # cachecontroller.set_cache(employee_cache_key, employee)
            # logger.info('db')
            employee_funtionalhead=employee.functional_head
            dict={}
            dict["RM"]=employee.RM
            dict["Fictional_head"]=employee.functional_head

            return dict


    def get_employee_detail(self, empid_arr):
        obj_data = Employee.objects.filter(id__in=empid_arr).values('id', "full_name", "code", "employee_branch__code",
                                                                    "employee_branch__name", "employee_branch__id")
        vlist = []
        for employee in obj_data:
            emp_resp = EmployeeResponse()

            emp_resp.set_id(employee['id'])
            employe_name = '(' + employee['code'] + ') ' + employee['full_name']
            emp_resp.employe_name = employe_name
            emp_resp.set_full_name(employee['full_name'])
            emp_resp.set_code(employee['code'])
            emp_resp.branch_name = employee['employee_branch__name']
            emp_resp.branch_code = employee['employee_branch__code']
            emp_resp.branch_id = employee['employee_branch__id']

            vlist.append(emp_resp.get())
        return vlist

    def create_ad_employee(self, employee_code, empolyee_name, user_id):
        try:
            employee = Employee.objects.get(code=employee_code)
            employee.user_id = user_id
            employee.save()
            return employee
        except:
            employee = Employee.objects.create(code=employee_code, full_name=empolyee_name, user_id=user_id,
                                               created_by=user_id)
            return employee
    def create_employee(self, emp_obj, empid,address_id,contact_id):
        logger.info(str(emp_obj))

        if not emp_obj.get_id() is None:
            try:
                logger.error('EMPLOYEE: Employee Update Started')
                employee = Employee.objects.filter(id=emp_obj.get_id()).update(full_name=emp_obj.get_full_name(),
                                                                               first_name=emp_obj.get_first_name(),
                                                                               middle_name=emp_obj.get_middle_name(),
                                                                               last_name=emp_obj.get_last_name(),
                                                                               code=emp_obj.get_code(),
                                                                               designation=emp_obj.get_designation(),
                                                                               grade=emp_obj.get_grade(),
                                                                               # user_id=emp_obj.get_user_id(),
                                                                               employee_branch_id=emp_obj.get_employeebranch(),
                                                                               email_id=emp_obj.get_email_id(),
                                                                               dob=emp_obj.get_dob(),
                                                                               doj=emp_obj.get_doj(),
                                                                               gender=emp_obj.get_gender(),
                                                                               # phone_no = emp_obj.get_phone_no(),supervisor =emp_obj.get_supervisor(),
                                                                               # hierarchy =emp_obj.get_hierarchy(),
                                                                               branch=emp_obj.get_branch(),
                                                                               # costcentre=emp_obj.get_costcentre(),
                                                                               # businesssegment =emp_obj.get_businesssegment(),

                                                                               updated_date=now(), lastsync_date=now(),
                                                                               srlno=emp_obj.get_srlno(),
                                                                               accountnumber=emp_obj.get_accountnumber(),
                                                                               grade1=emp_obj.get_grade1(),
                                                                               grade1_date=emp_obj.get_grade1_date(),
                                                                               grade2=emp_obj.get_grade2(),
                                                                               grade2_date=emp_obj.get_grade2_date(),
                                                                               noticeperiod=emp_obj.get_noticeperiod(),
                                                                               role=emp_obj.get_role(),
                                                                               department_id=emp_obj.get_department_id())

                employee = Employee.objects.get(id=emp_obj.get_id())

                # employee cache update
                emp_id = emp_obj.get_id()
                employee_empid_cache_key = "employee_" + "empid_" + str(emp_id)
                cachecontroller.update_cache(employee_empid_cache_key, employee)

                usr_id = employee.user_id
                if usr_id is not None:
                    employee_usrid_catche_key = "employee_" + "userid_" + str(usr_id)
                    cachecontroller.update_cache(employee_usrid_catche_key, employee)
                logger.info('update employee over')
                logger.error('EMPLOYEE: Employee Update Success' + str(employee))



            except IntegrityError as error:
                logger.info('ERROR_Employee_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except Exception as e:
                logger.info('ERROR_Employee_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = Error()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
            except :
                logger.info('ERROR_Employee_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = Error()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                logger.error('EMPLOYEE: Employee Creation Started')
                employee = Employee.objects.create(full_name=emp_obj.get_full_name(),
                                                   first_name=emp_obj.get_first_name(),
                                                   middle_name=emp_obj.get_middle_name(),
                                                   last_name=emp_obj.get_last_name(), code=emp_obj.get_code(),
                                                   designation=emp_obj.get_designation(), grade=emp_obj.get_grade(),
                                                   user_id=emp_obj.get_user_id(),
                                                   employee_branch_id=emp_obj.get_employeebranch(),
                                                   email_id=emp_obj.get_email_id(),
                                                   dob=emp_obj.get_dob(), doj=emp_obj.get_doj(),
                                                   gender=emp_obj.get_gender(),
                                                   # phone_no = emp_obj.get_phone_no(),supervisor =emp_obj.get_supervisor(),
                                                   # hierarchy =emp_obj.get_hierarchy(),
                                                   branch=emp_obj.get_branch(),
                                                   # costcentre=emp_obj.get_costcentre(),
                                                   # businesssegment =emp_obj.get_businesssegment(),
                                                   address_id=address_id,
                                                   contact_id=contact_id,
                                                   created_by=empid, lastsync_date=now(), srlno=emp_obj.get_srlno(),
                                                   accountnumber=emp_obj.get_accountnumber(),
                                                   grade1=emp_obj.get_grade1(),
                                                   grade1_date=emp_obj.get_grade1_date(),
                                                   grade2=emp_obj.get_grade2(),
                                                   grade2_date=emp_obj.get_grade2_date(),
                                                   noticeperiod=emp_obj.get_noticeperiod(),
                                                   role=emp_obj.get_role(),
                                                   department_id=emp_obj.get_department_id())
                # employee = Employee.objects.get(id=emp_obj.get_id())
                logger.error('EMPLOYEE: Employee Creation Success' + str(employee))
            except IntegrityError as error:
                logger.error('ERROR_Employee_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except Employee.DoesNotExist:
                logger.error('ERROR_Employee_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
            except:
                logger.error('ERROR_Employee_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = Error()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj

        emp_resp = EmployeeResponse()
        emp_resp.set_id(employee.id)
        emp_resp.set_first_name(employee.first_name)
        emp_resp.set_middle_name(employee.middle_name)
        emp_resp.set_last_name(employee.last_name)
        emp_resp.set_full_name(employee.full_name)
        emp_resp.set_code(employee.code)
        emp_resp.set_grade(employee.grade)
        emp_resp.set_designation(employee.designation)
        return emp_resp

    def create_employee_sample(self, emp_obj):
        if not emp_obj.get_id() is None:
            try:
                pass
            except IntegrityError as error:
                pass
            except Employee.DoesNotExist:
                pass
            except:
                pass
        else:
            try:
                pass
            except IntegrityError as error:
                pass
            except Employee.DoesNotExist:
                pass
            except:
                pass
        emp_resp = EmployeeResponse()
        return emp_resp

    def get_employee_list(self,request, vys_page, user_id, search_key):
        try:
            condition = Q(entity_id=self._entity_id())
            if search_key is not None:
                condition &= (Q(employee__full_name__contains=search_key) & Q(employee__status=1))
            #     employeeList = EmployeeEntityMapping.objects.using(self._current_app_schema()).filter(Q(employee__full_name__contains=search_key) &
            #                                                                                           Q(employee__status=1)&Q(entity_id=self._entity_id()))[
            #                    vys_page.get_offset():vys_page.get_query_limit()]
            # else:
            employeeListCount = EmployeeEntityMapping.objects.using(self._current_app_schema()).filter(condition).count()
            employeeList = EmployeeEntityMapping.objects.using(self._current_app_schema()).filter(condition)[vys_page.get_offset():vys_page.get_query_limit()]
            vlist = NWisefinList()
            for obj in employeeList:
                employee=obj.employee
                emp_resp = EmployeeResponse()
                emp_resp.set_id(employee.id)
                emp_resp.set_first_name(employee.first_name)
                emp_resp.set_middle_name(employee.middle_name)
                emp_resp.set_last_name(employee.last_name)
                disp_name = '(' + employee.code + ') ' + employee.full_name
                emp_resp.set_full_name(disp_name)
                # emp_resp.set_full_name(employee.full_name)
                emp_resp.set_code(employee.code)
                emp_resp.set_grade(employee.grade)
                emp_resp.set_designation(employee.designation)
                emp_resp.set_user(employee.user_id)
                # emp_resp.set_department(employee.department_id)
                emp_resp.set_dob(employee.dob)
                emp_resp.set_doj(employee.doj)
                Gender_service = GENDER()
                genderdb = (employee.gender)
                # print(genderdb)
                gender = Gender_service.getGenderType(int(genderdb))
                emp_resp.gender=gender
                emp_resp.set_phone_no(employee.phone_no)
                emp_resp.set_employee_type(employee.employee_type)
                emp_resp.set_supervisor(employee.supervisor)
                emp_resp.set_hierarchy(employee.hierarchy)
                emp_resp.set_employee_branch_id(employee.employee_branch_id)
                emp_branch=employee.employee_branch_id
                if emp_branch != None:
                    branch = EmployeeBranch.objects.get(id=emp_branch)
                    emp_resp.branch = (branch.name)
                else:
                    emp_resp.set_branch(employee.branch)
                emp_resp.set_costcentre(employee.costcentre)
                emp_resp.set_businesssegment(employee.businesssegment)
                emp_resp.set_contact_id(employee.contact_id)
                if employee.address_id !=None and employee.address_id !='':
                    emp_resp.set_address_id(employee.address_id)

                    # emp_resp.set_email_id(employee.email_id)
                    # emp_resp.set_mobilenumber(employee.phone_no)
                    print(employee.id)
                    state_id=(employee.address.state_id)
                    print(state_id)
                    if state_id!= None:
                        state_ser=MasterAPI()
                        state=state_ser.get_state_id_new(request,state_id)
                        state=json.loads(state.content)
                        emp_resp.state_name = state['name']
                        print(emp_resp.state_name)
                    else:
                        emp_resp.state_name = ""
                else:
                    emp_resp.state_name = ""
                    emp_resp.set_address_id('')
                emp_resp.set_email_id(employee.email_id)
                emp_resp.set_mobilenumber(employee.phone_no)
                # print(emp_resp.state_name)
                vlist.append(emp_resp)
            vpage = NWisefinPaginator(employeeList, vys_page.get_index(), 10)
            vlist.set_listcount(employeeListCount)
            vlist.set_pagination(vpage)
            return vlist
        except:
            logger.error('ERROR_Employee_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_DATA)
            return error_obj

    def get_dept_employee_list(self, dept_id, vys_page):
        employeeList = EmployeeEntityMapping.objects.filter(employee__department_id=dept_id)[vys_page.get_offset():vys_page.get_query_limit()]
        vlist = NWisefinList()
        for obj in employeeList:
            employee = obj.employee
            emp_resp = EmployeeResponse()
            emp_resp.set_id(employee.id)
            emp_resp.set_first_name(employee.first_name)
            emp_resp.set_middle_name(employee.middle_name)
            emp_resp.set_last_name(employee.last_name)
            emp_resp.set_full_name(employee.full_name)
            emp_resp.set_code(employee.code)
            emp_resp.set_grade(employee.grade)
            emp_resp.set_designation(employee.designation)
            emp_resp.set_user(employee.user_id)
            emp_resp.set_department(employee.department_id)

            vlist.append(emp_resp)
        vpage = NWisefinPaginator(employeeList, vys_page.get_index(), 10)
        vlist.set_pagination(vpage)
        return vlist
    #
    # def get_employee(self, emp_id, user_id):
    #     employee_cache_key = "employee_" + "empid_" + str(emp_id)
    #     employee = cachecontroller.get_cache(employee_cache_key)
    #     logger.info('cache')
    #
    #     if employee == None:
    #         employee = Employee.objects.get(id=emp_id)
    #         cachecontroller.set_cache(employee_cache_key, employee)
    #         logger.info('db')
    #
    #     emp_resp = EmployeeResponse()
    #     emp_resp.set_id(employee.id)
    #     emp_resp.set_first_name(employee.first_name)
    #     emp_resp.set_middle_name(employee.middle_name)
    #     emp_resp.set_last_name(employee.last_name)
    #     emp_resp.set_full_name(employee.full_name)
    #     emp_resp.set_code(employee.code)
    #     emp_resp.set_grade(employee.grade)
    #     emp_resp.set_designation(employee.designation)
    #     emp_resp.set_user(employee.user_id)
    #
    #     emp_resp.set_dob(employee.dob)
    #     emp_resp.set_doj(employee.doj)
    #     emp_resp.set_gender(employee.gender)
    #     emp_resp.set_phone_no(employee.phone_no)
    #     emp_resp.set_employee_type(employee.employee_type)
    #     emp_resp.set_supervisor(employee.supervisor)
    #     emp_resp.set_hierarchy(employee.hierarchy)
    #     emp_resp.set_branch(employee.branch)
    #     emp_resp.set_employee_branch_id(employee.employee_branch_id)
    #     emp_resp.set_costcentre(employee.costcentre)
    #     emp_resp.set_businesssegment(employee.businesssegment)
    #     emp_resp.set_address_id(employee.address_id)
    #     emp_resp.set_contact_id(employee.contact_id)
    #
    #     return emp_resp

    def delete_employee(self, emp_id):
        emp = Employee.objects.filter(id=emp_id).delete()
        if emp[0] == 0:
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_EMP_ID)
            error_obj.set_description(ErrorDescription.INVALID_EMP_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

    def get_user_emp_list(self, user_id, search):
        emp = Employee.objects.get(id=user_id)
        vyslist = NWisefinList()
        lite = NWisefinLiteList()
        if (search):
            lite.set_id(str(emp.id) + '_emp')
        else:
            lite.set_id(emp.id)
        disp_name = '(' + emp.code + ') ' + emp.full_name
        lite.set_text(disp_name)
        vyslist.append(lite)
        dept_arr = Department.objects.all()
        for dept in dept_arr:
            lite = NWisefinLiteList()
            if (search):
                lite.set_id(str(dept.id) + '_dept')
            else:
                lite.set_id(dept.id)
            lite.set_text(dept.name)
            vyslist.append(lite)
        return vyslist

    def get_memo_filter(self, user_id, search):
        emp = Employee.objects.get(id=user_id)
        vyslist =NWisefinList()
        lite = NWisefinLiteList()
        lite.set_id(str(emp.id) + '_from_emp')
        disp_name = 'From (' + emp.code + ') ' + emp.full_name
        lite.set_text(disp_name)
        vyslist.append(lite)
        lite = NWisefinLiteList()
        lite.set_id(str(emp.id) + '_to_emp')
        disp_name = 'To (' + emp.code + ') ' + emp.full_name
        lite.set_text(disp_name)
        vyslist.append(lite)
        dept_arr = Department.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id())
        for dept in dept_arr:
            lite = NWisefinLiteList()
            lite.set_id(str(dept.id) + '_from_dept')
            disp_name = 'From ' + dept.name
            lite.set_text(disp_name)
            vyslist.append(lite)
            lite = NWisefinLiteList()
            lite.set_id(str(dept.id) + '_to_dept')
            disp_name = 'To ' + dept.name
            lite.set_text(disp_name)
            vyslist.append(lite)
        return vyslist

    def get_contact_address_id(self, employee_id):
        employee = Employee.objects.get(id=employee_id)

        data_obj = EmployeeResponse()
        data_obj.set_address_id(employee.address_id)
        data_obj.set_contact_id(employee.contact_id)
        return data_obj

    # mtm in employeee - department

    def add_remove_department_from_employee(self, employee_id, department_arr):
        employee = Employee.objects.get(id=employee_id)
        department_id = department_arr.get('department_id')
        method = department_arr.get('method')
        if len(department_id) >= 1:
            if method == "add":
                for id in department_id:
                    department = Department.objects.using(self._current_app_schema()).get(id=id, entity_id=self._entity_id())
                    employee.department.add(department)
            elif method == "remove":
                for id in department_id:
                    department = Department.objects.using(self._current_app_schema()).get(id=id, entity_id=self._entity_id())
                    employee.department.remove(department)

            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            return success_obj
        else:
            error_obj = Error()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            return error_obj

    def add_remove_employee_from_department(self, department_id, employee_arr):
        department = Department.objects.using(self._current_app_schema()).get(id=int(department_id))
        employee_id = employee_arr.get('employee_id')
        method = employee_arr.get('method')
        if len(employee_id) >= 1:
            if method == "add":
                for id in employee_id:
                    employee = Employee.objects.using(self._current_app_schema()).get(id=id)
                    # department.employee_set.add(employee)
            elif method == "remove":
                for id in employee_id:
                    employee = Employee.objects.using(self._current_app_schema()).get(id=id)
                    # department.employee_set.remove(employee)

            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            return success_obj
        else:
            error_obj = Error()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
            return error_obj

    # def get_department_from_employee(self, employee_id):
    #     employee = Employee.objects.get(id=employee_id)
    #     departmentList = employee.department.all()
    #     vlist = VysfinList()
    #     for department in departmentList:
    #         dept_resp = DepartmentResponse()
    #         dept_resp.set_id(department.id)
    #         dept_resp.set_name(department.name)
    #         dept_resp.set_code(department.code)
    #         dept_resp.set_description(department.description)
    #         dept_resp.set_short_notation(department.short_notation)
    #         vlist.append(dept_resp)
    #     return vlist

    def check_empid(self, employee_id, user_id):
        user_employee_id = self.get_empid_from_userid(user_id)
        if int(employee_id) == user_employee_id:
            return True
        else:
            return False

    def check_depid(self, department_id, employee_id, empid_check):
        if empid_check == False:
            employee_id = self.get_empid_from_userid(employee_id)

        condition = Q(employee_id=employee_id) & Q(department_id=department_id) &Q(entity_id=self._entity_id())
        employeeList = EmployeeDepartmentPermission.objects.using(self._current_app_schema()).filter(condition)

        if len(employeeList) > 0:
            return True
        else:
            return False

    def get_department_from_employee(self, employee_id):
        condition = Q(employee_id=employee_id) &Q(entity_id=self._entity_id())
        departmentList = EmployeeDepartmentPermission.objects.using(self._current_app_schema()).filter(condition)
        vlist = NWisefinList()
        for obj in departmentList:
            department = obj.department
            dept_resp = DepartmentResponse()
            if department is not None:
                dept_resp.set_id(department.id)
                dept_resp.set_name(department.name)
                dept_resp.set_code(department.code)
                dept_resp.set_description(department.description)
                dept_resp.set_short_notation(department.short_notation)
                vlist.append(dept_resp)
        return vlist

    def get_employee_from_department(self, department_id):
        condition = Q(department_id=department_id) &Q(entity_id=self._entity_id())
        employeeList = EmployeeDepartmentPermission.objects.using(self._current_app_schema()).filter(condition)
        vlist = NWisefinList()
        for obj in employeeList:
            employee = obj.employee
            emp_resp = EmployeeResponse()
            emp_resp.set_id(employee.id)
            emp_resp.set_first_name(employee.first_name)
            emp_resp.set_middle_name(employee.middle_name)
            emp_resp.set_last_name(employee.last_name)
            emp_resp.set_full_name(employee.full_name)
            emp_resp.set_code(employee.code)
            emp_resp.set_grade(employee.grade)
            emp_resp.set_designation(employee.designation)
            emp_resp.set_user(employee.user_id)
            emp_resp.set_department(employee.department_id)
            vlist.append(emp_resp)
        return vlist


    def get_dept_from_emp(self,employee_id,type,query,vys_page):

        if query == None:
            query = ''

        if type == 'memo':
            if query is not None:
                condition = Q(can_create=True) & Q(employee_id=employee_id) & Q(
                    department__name__icontains=query) &Q(entity_id=self._entity_id())
            else:
                condition = Q(can_create=True) & Q(employee_id=employee_id)&Q(entity_id=self._entity_id())
        elif type == 'admin':
            condition = Q(isadmin=True) & Q(employee_id=employee_id) & Q(
                department__name__icontains=query)&Q(entity_id=self._entity_id())
        elif type == 'all' or type == None:
            condition = Q(employee_id=employee_id) & Q(department__name__icontains=query)&Q(entity_id=self._entity_id())

        # else:
        #     condition = Q(employee_id=employee_id) & Q(department__name__icontains=query)

        departmentobj = EmployeeDepartmentPermission.objects.using(self._current_app_schema()).filter(condition)
        departmentList = []
        for i in departmentobj:
            dept = i.department
            dept.can_create = i.can_create
            dept.isadmin = i.isadmin
            departmentList.append(dept)

        vlist = NWisefinList()
        for department in departmentList:
            dept_resp = DepartmentResponse()
            dept_resp.set_id(department.id)
            dept_resp.set_name(department.name)
            dept_resp.set_code(department.code)
            dept_resp.set_description(department.description)
            dept_resp.set_short_notation(department.short_notation)
            dept_resp.isadmin = department.isadmin
            dept_resp.can_create = department.can_create

            vlist.append(dept_resp)
        vpage = NWisefinPaginator(departmentList, vys_page.get_index(), 10)
        vlist.set_pagination(vpage)
        return vlist

    def get_emp_from_dept(self,department_id,type,query,vys_page):
        if query == None:
            query = ''

        if type == 'memo':
            condition = Q(can_create=True) & Q(department_id=department_id) & Q(
                employee__full_name__icontains=query)
        elif type == 'admin':
            condition = Q(isadmin=True) & Q(department_id=department_id) & Q(
                employee__full_name__icontains=query)
        elif type == 'all' or type == None:
            condition = Q(department_id=department_id) & Q(employee__full_name__icontains=query)

        employeeobj = EmployeeDepartmentPermission.objects.using(self._current_app_schema()).filter(condition)
        employeeList = []
        for i in employeeobj:
            emp = i.employee
            emp.isadmin = i.isadmin
            emp.can_create = i.can_create
            employeeList.append(emp)

        vlist = NWisefinList()
        for employee in employeeList:
            emp_resp = EmployeeResponse()
            empbrnch_serv = EmployeeBranchService(self._scope())
            emp_resp.set_id(employee.id)
            emp_resp.set_first_name(employee.first_name)
            emp_resp.set_middle_name(employee.middle_name)
            emp_resp.set_last_name(employee.last_name)
            emp_resp.set_full_name(employee.full_name)
            emp_resp.set_code(employee.code)
            emp_resp.set_grade(employee.grade)
            emp_resp.set_designation(employee.designation)
            emp_resp.set_user(employee.user_id)
            emp_resp.set_dob(employee.dob)
            emp_resp.set_doj(employee.doj)
            emp_resp.set_gender(employee.gender)
            emp_resp.set_phone_no(employee.phone_no)
            emp_resp.set_employee_type(employee.employee_type)
            emp_resp.set_supervisor(employee.supervisor)
            emp_resp.set_hierarchy(employee.hierarchy)
            emp_resp.set_branch(employee.branch)

            emp_resp.set_costcentre(employee.costcentre)
            emp_resp.set_businesssegment(employee.businesssegment)
            emp_resp.set_address_id(employee.address_id)
            emp_resp.set_contact_id(employee.contact_id)
            emp_resp.isadmin = employee.isadmin
            emp_resp.can_create = employee.can_create
            vlist.append(emp_resp)
        return vlist

    def search_employee_list(self, request, query, vys_page):
        # search_employee_list
        condition = Q(entity_id=self._entity_id())& Q(employee__status=1)
        if query is not None:
            condition &= (Q(employee__full_name__icontains=query) | Q(employee__code__icontains=query) | Q(
                employee__designation__icontains=query))
        # employeeList = None
        # if condition is not None:
        employeeList = EmployeeEntityMapping.objects.values('employee__id', 'employee__full_name', 'employee__code','employee__employee_branch_id','employee__employee_branch__code',"employee__employee_branch__name").filter(condition)[
                           vys_page.get_offset():vys_page.get_query_limit()]
        print(employeeList)
        # else:
        #     employeeList = EmployeeEntityMapping.objects.values('employee__id', 'employee__full_name', 'employee__code','employee__employee_branch_id','employee__employee_branch__code',"employee__employee_branch__name").filter(entity_id=self._entity_id())[
        #                    vys_page.get_offset():vys_page.get_query_limit()]
        vlist = NWisefinList()
        for employee in employeeList:
            emp_resp = EmployeeResponse()
            disp_name = '(' + employee['employee__code'] + ') ' + employee['employee__full_name']
            emp_resp.set_full_name(disp_name)
            emp_resp.set_id(employee['employee__id'])
            emp_resp.branch_id = employee['employee__employee_branch_id']
            emp_resp.branch_code = employee['employee__employee_branch__code']
            emp_resp.branch_name = employee['employee__employee_branch__name']
            vlist.append(emp_resp)
        vpage = NWisefinPaginator(employeeList, vys_page.get_index(), 10)
        vlist.set_pagination(vpage)
        return vlist

    # TA function
    def search_employee_exclude_maker(self, request, query, vys_page,maker):
        # search_employee_list
        Rm_data=Employee.objects.using(self._current_app_schema()).filter(RM=request.employee_id)
        for each_data in Rm_data:
            maker.append(each_data.id)
        condition = Q(entity_id=self._entity_id())& Q(employee__status=1)
        if query is not None:
            condition &= (Q(employee__full_name__icontains=query) | Q(employee__code__icontains=query) )
        # employeeList = None
        # if condition is not None:
        employeeList = EmployeeEntityMapping.objects.values('employee__id', 'employee__full_name', 'employee__code','employee__employee_branch_id','employee__employee_branch__code',"employee__employee_branch__name").filter(condition).exclude(employee__id__in=maker)[
                           vys_page.get_offset():vys_page.get_query_limit()]
        # else:
        #     employeeList = Employee.objects.values('id', 'full_name', 'code','employee_branch_id','employee_branch__code',"employee_branch__name").exclude(id__in=[maker]).all()[
        #                    vys_page.get_offset():vys_page.get_query_limit()]
        vlist = NWisefinList()
        for employee in employeeList:
            emp_resp = EmployeeResponse()
            disp_name = '(' + employee['employee__code'] + ') ' + employee['employee__full_name']
            emp_resp.set_full_name(disp_name)
            emp_resp.set_employee_name(employee['employee__full_name'])
            emp_resp.set_code(employee['employee__code'])
            emp_resp.set_id(employee['employee__id'])
            emp_resp.branch_id = employee['employee__employee_branch_id']
            emp_resp.branch_code = employee['employee__employee_branch__code']
            emp_resp.branch_name = employee['employee__employee_branch__name']
            vlist.append(emp_resp)
        vpage = NWisefinPaginator(employeeList, vys_page.get_index(), 10)
        vlist.set_pagination(vpage)
        return vlist

    def search_employee(self, emp_id, user_id):
        employee = Employee.objects.values('id', 'full_name', 'code').get(id=emp_id)
        emp_resp = EmployeeResponse()
        emp_resp.set_full_name(employee['full_name'])
        emp_resp.set_code(employee['code'])
        emp_resp.set_id(employee['id'])
        return emp_resp

    def get_userid_from_empid(self, employee_id):
        employee_cache_key = "employee_" + "empid_" + str(employee_id)
        employee = cachecontroller.get_cache(employee_cache_key)
        logger.info('cache')

        if employee == None:
            employee = Employee.objects.get(id=employee_id)
            cachecontroller.set_cache(employee_cache_key, employee)
            logger.info('db')

        user_id = employee.user_id
        return user_id

    # def get_empid_from_userid(self, user_id):
    #     employee_cache_key = "employee_" + "userid_" + str(user_id)
    #     employee = cachecontroller.get_cache(employee_cache_key)
    #     logger.info('cache')
    #     if employee == None:
    #         employee = Employee.objects.get(user_id=user_id)
    #         cachecontroller.set_cache(employee_cache_key, employee)
    #         logger.info('db')
    #
    #     employee_id = employee.id
    #     return employee_id

    # def get_employee_from_userid(self, user_id):
    #     employee_cache_key = "employee_" + "userid_" + str(user_id)
    #     employee = cachecontroller.get_cache(employee_cache_key)
    #     logger.info('cache')
    #     if employee == None:
    #         employee = Employee.objects.get(user_id=user_id)
    #         cachecontroller.set_cache(employee_cache_key, employee)
    #         logger.info('db')
    #
    #     return employee
    def fetch_employee_by_empid(self, emp_id):
        employee = Employee.objects.get(id=emp_id)
        emp_data = {"id": employee.id, "code": employee.code, "name": employee.full_name,
                    "employee_branch": employee.employee_branch_id,"accountnumber":employee.accountnumber,
                    "address_id": employee.address_id,"email":employee.email_id,"phone_no":employee.phone_no}
        employee_dic = json.dumps(emp_data, indent=6)
        return emp_data

    def fetch_employee_grade(self, emp_id):
        employee = Employee.objects.get(id=emp_id)
        emp_data = {"grade1": employee.grade1}
        employee_dic = json.dumps(emp_data, indent=6)
        return emp_data

    def fetch_empbranch(self, empbranch_id):
        empbranch = EmployeeBranch.objects.using(self._current_app_schema()).get(id=empbranch_id)
        empbranch_data = {"id": empbranch.id, "code": empbranch.code, "name": empbranch.name, "gstin": empbranch.gstin,"glno":empbranch.glno}
        empbranch_dic = json.dumps(empbranch_data, indent=5)
        return empbranch_data
    def fetch_empbranchcode(self, branchcode):
        empbranch = EmployeeBranch.objects.using(self._current_app_schema()).get(code=branchcode)
        empbranch_data = {"id": empbranch.id, "code": empbranch.code, "name": empbranch.name, "gstin": empbranch.gstin,"glno":empbranch.glno}
        empbranch_dic = json.dumps(empbranch_data, indent=5)
        return empbranch_data
    def fetch_empbranch_empid(self, emp_id):
        empbranch = Employee.objects.using(self._current_app_schema()).get(id=emp_id)
        empbranch_data = {"id": empbranch.id, "code": empbranch.code, "branch":empbranch.branch}
        empbranch_dic = json.dumps(empbranch_data, indent=5)
        return empbranch_data

    def fetch_employee_address(self, add_id):
        employee = EmployeeAddress.objects.using(self._current_app_schema()).get(id=add_id)
        emp_data = {"id": employee.id, "line1": employee.line1, "line2": employee.line2,
                    "line3": employee.line3, "pincode_id": employee.pincode_id, "city_id": employee.city_id,
                    "state_id": employee.state_id}
        employee_dic = json.dumps(emp_data, indent=8)
        return emp_data

    def fetch_employee_by_empname(self, emp_id):
        employee = Employee.objects.get(id=emp_id)
        emp_data = {"id": employee.id, "code": employee.code, "name": employee.full_name}
        employee_dic = json.dumps(emp_data, indent=6)
        return emp_data

    # def check_employee_role(self, status_id):
    #     # status_id = status_id+1
    #     employee_role = EmployeeRole.objects.filter(role_id=status_id)
    #
    #     vlist = VysfinList()
    #     for emp in employee_role:
    #         employee_role_data = EmployeeRoleResponse()
    #         employee_role_data.set_role_id(emp.role_id)
    #         employee_role_data.set_role(emp.role)
    #         employee_role_data.set_employee_id(emp.employee_id)
    #
    #         vlist.append(employee_role_data)
    #     return vlist
    #
    # def get_employee_role(self, emp_id):
    #
    #     try:
    #         employee_role = EmployeeRole.objects.get(employee_id=emp_id)
    #         emp_role = employee_role.role_id
    #     except:
    #         emp_role = None
    #
    #     return emp_role

    def employee_isactive(self, emp_id):
        try:
            employee = Employee.objects.get(id=emp_id)
            if employee.status == Status.create:
                active = True
            else:
                active = False
            return active
        except:
            active = False
            return active

    def multi_employee_isactive(self, emp_id):
        condition = None
        for id in emp_id:
            if condition is None:
                condition = Q(id__exact=id) & Q(status=Status.create)
            else:
                condition |= Q(id__exact=id) & Q(status=Status.create)

        employee_status = Employee.objects.values_list('id', flat=True).filter(condition)

        for i in emp_id:
            if i in employee_status:
                active = True
            else:
                active = False
                break

        return active

    def employee_info(self, user_arr):
        # user_list = None
        # for user_id in user_arr:
        #     if condition is None:
        #         condition = Q(user_id__exact=user_id)
        #     else:
        #         condition |= Q(user_id__exact=user_id)
        # if condition is not None:
        user_list = Employee.objects.filter(user_id__in=user_arr)
        resp_list = NWisefinList()
        if user_list is not None:
            for user in user_list:
                user_obj = NWisefinUser()
                user_obj.set_id(user.id)
                disp_name = '(' + user.code + ') ' + user.full_name
                user_obj.set_full_name(disp_name)
                resp_list.append(user_obj)
        return resp_list.get()

    def department_info(self, user_arr):
        condition = None
        user_list = None
        for user_id in user_arr:
            if condition is None:
                condition = Q(id__exact=user_id) &Q(entity_id=self._entity_id())
            else:
                condition |= Q(id__exact=user_id) &Q(entity_id=self._entity_id())
        if condition is not None:
            user_list = Department.objects.using(self._current_app_schema()).filter(condition)
        resp_list = NWisefinList()
        if user_list is not None:
            for user in user_list:
                user_obj = NwisefinSearch()
                user_obj.set_id(user.id)
                user_obj.set_name(user.name)
                branch_data = self.get_branch_info_deptid(user.id)
                user_obj.branch = branch_data.get('branch')
                user_obj.branch_code = branch_data.get('branch_code')
                branch_id = user.branch_id
                if branch_id is None:
                    branch_code = None
                    branch_name = None
                else:
                    branch_code = user.branch.code
                    branch_name = user.branch.name
                branch_name1 = '(' + str(branch_code) + ') ' + str(branch_name)
                if user.name == None:
                    dept_name = branch_name1
                else:
                    dept_name = str(branch_name1) + ' (' + str(user.name) + ')'
                user_obj.dept_name = dept_name
                resp_list.append(user_obj)
        return resp_list.get()

    def get_branch_info_deptid(self, dept_id):
        try:
            dept = Department.objects.using(self._current_app_schema()).get(id=dept_id, entity_id=self._entity_id())
            branch = dept.branch
            branch_dict = {"branch_code": branch.code, "branch": branch.name}
        except:
            branch_dict = {"branch_code": None, "branch": None}
        return branch_dict

    def get_user_id(self, user_arr):
        condition = None
        user_list = None
        for user_id in user_arr:
            if condition is None:
                condition = Q(id__exact=user_id)
            else:
                condition |= Q(id__exact=user_id)
        if condition is not None:
            user_list = Employee.objects.filter(condition)
        resp_list = []
        if user_list is not None:
            for user in user_list:
                resp_list.append(str(user.user_id))
        return resp_list

    # def employee_info_by_id(self, user_arr):
    #     condition = None
    #     user_list = None
    #     for user_id in user_arr:
    #         if condition is None:
    #             condition = Q(id__exact=user_id)
    #         else:
    #             condition |= Q(id__exact=user_id)
    #     if condition is not None:
    #         user_list = Employee.objects.filter(condition)
    #     resp_list = NWisefinList()
    #     if user_list is not None:
    #         for user in user_list:
    #             user_obj = NWisefinUser()
    #             user_obj.set_id(user.id)
    #             disp_name = '(' + user.code + ') ' + user.full_name
    #             user_obj.set_full_name(disp_name)
    #             user_obj.set_designation(user.designation)
    #             resp_list.append(user_obj)
    #     return resp_list.get()

    def sub_module_memo(self, user_id):
        arr = []
        emp = self.get_empname_from_userid(user_id)
        dept_arr = self.get_deptname_from_employee(emp.id)
        for i in dept_arr:
            arr.append(i)

        arr.append(emp)
        return arr

    def get_deptname_from_employee(self, employee_id):
        employee = Employee.objects.get(id=employee_id)
        departmentList = employee.department.all()
        vlist = []
        for department in departmentList:
            dept_resp = DepartmentResponse()
            dept_resp.set_id(department.id)
            dept_resp.set_name(department.name)
            dept_resp.type = 'group'
            vlist.append(dept_resp)
        return vlist

    def get_empname_from_userid(self, user_id):
        employee_cache_key = "employee_" + "userid_" + str(user_id)
        employee = cachecontroller.get_cache(employee_cache_key)
        logger.info('cache')
        if employee == None:
            employee = Employee.objects.get(id=user_id)
            cachecontroller.set_cache(employee_cache_key, employee)
            logger.info('db')

        emp_resp = EmployeeResponse()
        emp_resp.name = employee.full_name
        emp_resp.type = None
        emp_resp.set_id(employee.id)
        return emp_resp

    def emp_code(self, emp_code):
        try:
            emp = Employee.objects.get(code=emp_code)
            return emp
        except:
            emp = None
            return emp

    def fetch_employee_list(self, search_key):
        condition = Q(entity_id=self._entity_id())
        if search_key is not None:
            condition &= Q(employee__code__contains=search_key)
        employeeList = EmployeeEntityMapping.objects.filter(condition)
        # else:
        #     employeeList = Employee.objects.all()
        vlist = NWisefinList()
        for obj in employeeList:
            employee = obj.employee
            emp_resp = EmployeeResponse()
            emp_resp.set_id(employee.id)
            emp_resp.set_first_name(employee.first_name)
            emp_resp.set_middle_name(employee.middle_name)
            emp_resp.set_last_name(employee.last_name)
            emp_resp.set_full_name(employee.full_name)
            emp_resp.set_code(employee.code)
            emp_resp.set_grade(employee.grade)
            emp_resp.set_designation(employee.designation)
            emp_resp.set_user(employee.user_id)
            emp_resp.set_dob(employee.dob)
            emp_resp.set_doj(employee.doj)
            emp_resp.set_gender(employee.gender)
            emp_resp.set_phone_no(employee.phone_no)
            emp_resp.set_employee_type(employee.employee_type)
            emp_resp.set_supervisor(employee.supervisor)
            emp_resp.set_hierarchy(employee.hierarchy)
            emp_resp.set_branch(employee.branch)
            emp_resp.set_costcentre(employee.costcentre)
            emp_resp.set_businesssegment(employee.businesssegment)
            emp_resp.set_address_id(employee.address_id)
            emp_resp.set_contact_id(employee.contact_id)
            vlist.append(emp_resp)
        return vlist

    def search_employee_designation(self, request, query, vys_page):
        condition = Q(entity_id=self._entity_id())
        if query is not None:
            condition &= (Q(employee__full_name__icontains=query) | Q(employee__code__icontains=query) | Q(
                employee__designation__icontains=query)) & Q(employee__status=1)
        employeeList = None
        # if condition is not None:
        employeeList = EmployeeEntityMapping.objects.values('employee__id', 'employee__full_name', 'employee__code', 'employee__designation').filter(condition)[
                           vys_page.get_offset():vys_page.get_query_limit()]
        # else:
        #     employeeList = Employee.objects.values('id', 'full_name', 'code', 'designation').all()[
        #                    vys_page.get_offset():vys_page.get_query_limit()]
        vlist = NWisefinList()
        for employee in employeeList:
            emp_resp = EmployeeResponse()
            desig = employee['employee__designation']
            if desig is None:
                disp_name = '(' + employee['employee__code'] + ') ' + employee['employee__full_name']

            else:
                disp_name = '(' + employee['employee__code'] + ') ' + employee['employee__full_name'] + ' (' + employee['employee__designation'] + ')'
            emp_resp.set_full_name(disp_name)
            emp_resp.set_id(employee['employee__id'])
            vlist.append(emp_resp)
        vpage = NWisefinPaginator(employeeList, vys_page.get_index(), 10)
        vlist.set_pagination(vpage)
        return vlist

    def get_email_id(self, emp_id):
        employee = Employee.objects.get(id=emp_id)
        emp_email = employee.email_id
        emp_name = employee.full_name
        if emp_email is '' or emp_email is None:
            emp_data = {"name": emp_name, "to": []}
        else:
            emp_data = {"name": emp_name, "to": [emp_email]}
        return emp_data

    def get_email_deptid(self, dept_id):
        data = EmployeeDepartmentPermission.objects.using(self._current_app_schema()).filter(department_id=dept_id, entity_id=self._entity_id())
        arr = []
        for i in data:
            dept = i.department
            dept_name = self.get_dept_branch_name(dept.id)
            dept_name = dept_name.get('name')
            employee = i.employee
            emp_email = employee.email_id
            emp_name = employee.full_name
            if emp_email is '' or emp_email is None:
                pass
            else:
                arr.append(emp_email)
        emp_data = {"name": dept_name, "to": arr}
        return emp_data

    def get_employeecode_sync(self, emp_code):
        employee = Employee.objects.get(code=emp_code)
        emp_resp = EmployeeResponse()
        emp_resp.set_id(employee.id)
        emp_resp.set_first_name(employee.first_name)
        emp_resp.set_middle_name(employee.middle_name)
        emp_resp.set_last_name(employee.last_name)
        emp_resp.set_full_name(employee.full_name)
        emp_resp.set_code(employee.code)
        emp_resp.set_grade(employee.grade)
        emp_resp.set_designation(employee.designation)
        emp_resp.set_user(employee.user_id)
        emp_resp.set_dob(employee.dob)
        emp_resp.set_doj(employee.doj)
        emp_resp.set_gender(employee.gender)
        emp_resp.set_phone_no(employee.phone_no)
        emp_resp.set_employee_type(employee.employee_type)
        emp_resp.set_supervisor(employee.supervisor)
        emp_resp.set_hierarchy(employee.hierarchy)
        emp_resp.set_branch(employee.branch)
        emp_resp.set_costcentre(employee.costcentre)
        emp_resp.set_businesssegment(employee.businesssegment)
        emp_resp.set_address_id(employee.address_id)
        emp_resp.set_contact_id(employee.contact_id)
        return emp_resp


    def get_employee_list_sync(self, getfull_data,datefilter):
        logger.info('work')
        if getfull_data is None:
            employeeList = EmployeeEntityMapping.objects.filter(employee__lastsync_date__gte=datefilter,entity_id=self._entity_id())
        elif (getfull_data == 'all'):
            employeeList = EmployeeEntityMapping.objects.filter(entity_id=self._entity_id())
        vlist = NWisefinList()
        for obj in employeeList:
            employee = obj.employee
            emp_resp = EmployeeResponse()
            emp_resp.set_id(employee.id)
            emp_resp.set_first_name(employee.first_name)
            emp_resp.set_middle_name(employee.middle_name)
            emp_resp.set_last_name(employee.last_name)
            emp_resp.set_full_name(employee.full_name)
            emp_resp.set_code(employee.code)
            emp_resp.set_grade(employee.grade)
            emp_resp.set_designation(employee.designation)
            emp_resp.set_user(employee.user_id)
            emp_resp.set_email_id(employee.email_id)
            emp_resp.set_dob(employee.dob)
            emp_resp.set_doj(employee.doj)
            emp_resp.set_gender(employee.gender)
            emp_resp.set_phone_no(employee.phone_no)
            emp_resp.set_employee_type(employee.employee_type)
            emp_resp.set_supervisor(employee.supervisor)
            emp_resp.set_hierarchy(employee.hierarchy)
            branch_service = EmployeeBranchService(self._scope())
            emp_resp.branch_code = None
            if employee.employee_branch_id is not None:
                branch = branch_service.fetch_branch(employee.employee_branch_id)
                emp_resp.branch_code = branch.code
            emp_resp.set_costcentre(employee.costcentre)
            emp_resp.set_businesssegment(employee.businesssegment)
            emp_resp.set_address_id(employee.address_id)
            emp_resp.set_contact_id(employee.contact_id)
            emp_resp.set_accountnumber(employee.accountnumber)
            emp_resp.set_grade1(employee.grade1)
            emp_resp.set_grade1_date(employee.grade1_date)
            emp_resp.set_grade2(employee.grade2)
            emp_resp.set_grade2_date(employee.grade2_date)
            emp_resp.set_noticeperiod(employee.noticeperiod)
            emp_resp.set_role(employee.role)
            emp_resp.set_department_id(employee.department_id)
            vlist.append(emp_resp)
        return vlist



    # def create_employeelog(self, gl_obj,status):
    #     try:
    #
    #         gl_var = EmployeeLog.objects.create(maindata=gl_obj.get_maindata(),range_from=gl_obj.get_range_from(),range_to = gl_obj.get_range_to(),lastsync_date=datetime.now(),status=status)
    #
    #
    #         gl_data = EmployeeLogResponse()
    #         gl_data.set_id(gl_var.id)
    #         return gl_data
    #     except Exception as e:
    #         logger.info(str(e))

    def Fetch_Emp_List(self,codefilter):
        logger.info('work')
        employeeList = EmployeeEntityMapping.objects.filter(employee__code=codefilter, entity_id=self._entity_id())

        vlist = NWisefinList()
        for obj in employeeList:
            employee = obj.employee
            emp_resp = EmployeeResponse()
            emp_resp.set_id(employee.id)
            emp_resp.set_first_name(employee.first_name)
            emp_resp.set_middle_name(employee.middle_name)
            emp_resp.set_last_name(employee.last_name)
            # full_name = '(' + employee.code + ') ' + employee.full_name
            # emp_resp.set_full_name(disp_name)
            emp_resp.set_full_name(employee.full_name)
            emp_resp.set_code(employee.code)
            emp_resp.set_grade(employee.grade)
            emp_resp.set_designation(employee.designation)
            emp_resp.set_user(employee.user_id)
            emp_resp.set_email_id(employee.email_id)
            emp_resp.set_dob(employee.dob)
            emp_resp.set_doj(employee.doj)
            emp_resp.set_gender(employee.gender)
            emp_resp.set_phone_no(employee.phone_no)
            emp_resp.set_employee_type(employee.employee_type)
            emp_resp.set_supervisor(employee.supervisor)
            emp_resp.set_hierarchy(employee.hierarchy)
            emp_resp.set_branch(employee.branch)
            emp_resp.set_costcentre(employee.costcentre)
            emp_resp.set_businesssegment(employee.businesssegment)
            emp_resp.set_address_id(employee.address_id)
            emp_resp.set_contact_id(employee.contact_id)
            vlist.append(emp_resp)
        return vlist


    # def get_employee_log_list(self,datefilter,status):
    #     logger.info('work')
    #     employeeList =  EmployeeLog.objects.filter(lastsync_date__gte=datefilter,status=status)
    #
    #     vlist = NWisefinList()
    #     for employee in employeeList:
    #         emp_resp = EmployeeLogResponse()
    #         emp_resp.set_id(employee.id)
    #         emp_resp.set_maindata(employee.maindata)
    #         emp_resp.set_range_from(employee.range_from)
    #         emp_resp.set_range_to(employee.range_to)
    #         vlist.append(emp_resp)
    #     return vlist

    def employee_info_update(self, data):
        emp_code = data.get('code')
        type = data.get('type')
        value = data.get('value')

        if type == 'email':
            Employee.objects.filter(code=emp_code).update(email_id=value)
            logger.info("updated mail")

        elif type == 'status':
            value = int(value)
            Employee.objects.filter(code=emp_code).update(status=value)
            logger.info("updated status")

        elif type == 'branch':
            value = int(value)
            Employee.objects.filter(code=emp_code).update(employee_branch_id=value)
            logger.info("updated status")

        else:
            pass

        return

    def get_dept_branch_name(self, dept_id):
        department = Department.objects.using(self._current_app_schema()).get(id=dept_id, entity_id=self._entity_id())
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

    def get_email_id_with_using(self, emp_id):
        employee = Employee.objects.using('scheduler').get(id=emp_id)
        emp_email = employee.email_id
        emp_name = employee.full_name
        if emp_email !=None and '@' in emp_email :
            emp_data = {"name": emp_name, "to": [emp_email]}
        else:
            emp_data = {"name": emp_name, "to": []}
        return emp_data
# scheduler
    def get_email_deptid_with_using(self, dept_id):
        data = EmployeeDepartmentPermission.objects.using('scheduler').filter(department_id=dept_id)
        arr = []
        dept_name=None
        for i in data:
            dept = i.department
            dept_name = self.get_dept_branch_name_with_using(dept.id)
            dept_name = dept_name.get('name')
            employee = i.employee
            emp_email = employee.email_id
            emp_name = employee.full_name
            if emp_email !=None and '@' in emp_email :
                arr.append(emp_email)
        emp_data = {"name": dept_name, "to": arr}
        return emp_data

    def get_dept_branch_name_with_using(self, dept_id):
        department = Department.objects.using('scheduler').get(id=dept_id)
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


    # def empmobileupdate(self, data,employee_id):
    #     mobile=Employeemobileno.objects.filter(mobile_number=data.mobile_number).values('mobile_number', 'code').exclude(code =data.code)
    #     if len(mobile)==0:
    #         updateornot = Employeemobileno.objects.filter(code=data.code).values('mobile_number', 'code')
    #         if len(updateornot)>0:
    #
    #             employeeupdate = Employeemobileno.objects.filter(code=data.code).update(mobile_number=data.mobile_number,
    #                                                                                           updated_date=now(),
    #                                                                                       updated_by=employee_id)
    #             if employeeupdate:
    #                 emp_resp={"MESSAGE":'SUCCESS'}
    #             else:
    #                 emp_resp = {"MESSAGE": 'UPDATE FAILED'}
    #
    #
    #         else:
    #             employee = Employeemobileno.objects.create(code=data.code, mobile_number=data.mobile_number,
    #                                                        created_by=employee_id)
    #             if employee:
    #                 emp_resp = {"MESSAGE": 'SUCCESS'}
    #             else:
    #                 emp_resp = {"MESSAGE": 'FAILED '}
    #
    #
    #     else:
    #         emp_resp = {"MESSAGE": ' The Mobile Number Already Exist for Another User  Try with new Mobile number'}
    #     return emp_resp


    # def empmobileget(self,empid):
    #     mobile = Employeemobileno.objects.filter(code=empid).values('mobile_number','id')
    #
    #     if mobile:
    #         mobile=mobile
    #     else:
    #         mobile=[{"mobile_number":'','id':None}]
    #     employee = Employee.objects.filter(code=empid)
    #     # emp_resp = EmployeeMobieResponse()
    #     emp_resp = EmployeeResponse()
    #     if employee:
    #         for i in employee:
    #             emp_resp.set_id(mobile[0]['id'])
    #             emp_resp.set_first_name(i.first_name)
    #             emp_resp.set_middle_name(i.middle_name)
    #             emp_resp.set_last_name(i.last_name)
    #             emp_resp.set_full_name(i.full_name)
    #             emp_resp.set_code(i.code)
    #             emp_resp.set_mobilenumber(mobile[0]['mobile_number'])
    #
    #     return emp_resp

    def get_employee_name_from_empid(self, emp_id):
        employee = Employee.objects.get(id=emp_id)

        return employee.full_name

    # def fetch_logout_info(self,employee,from_date,to_date,vys_page):
    #     condition = None
    #     if employee is not None:
    #         res = ast.literal_eval(employee)
    #         if condition is None:
    #             condition = Q(employee__in =res)
    #     if from_date is not None and to_date is not None:
    #         if condition is None:
    #             condition = Q(login_date__range=[from_date, to_date])
    #         else:
    #             condition &= Q(login_date__range=[from_date, to_date])
    #     if condition is not None:
    #         obj_data = LogoutInfo.objects.filter(condition)[vys_page.get_offset():vys_page.get_query_limit()]
    #     else:
    #         obj_data = LogoutInfo.objects.all()[vys_page.get_offset():vys_page.get_query_limit()]
    #
    #     vlist = NWisefinList()
    #     for employee in obj_data:
    #         emp_resp = EmployeeLogResponse()
    #         emp_resp.set_id(employee.id)
    #         emp_obj=Employee.objects.get(id=employee.id)
    #         emp_name=emp_obj.full_name + ' (' + emp_obj.code + ')'
    #         emp_resp.employe_name=emp_name
    #         emp_resp.ip_address=employee.ip_address
    #         date_set=str(employee.login_date)
    #         logout_date=date_set.split('.')
    #         emp_resp.logout_date=logout_date[0]
    #         vpage = NWisefinPaginator(obj_data, vys_page.get_index(), 10)
    #         vlist.set_pagination(vpage)
    #         vlist.append(emp_resp)
    #     return vlist

    # def fetch_login_info(self,employee,from_date,to_date,vys_page):
    #     condition = None
    #     if employee is not None:
    #         res = ast.literal_eval(employee)
    #         if condition is None:
    #             condition = Q(employee__in =res)
    #     if from_date is not None and to_date is not None:
    #         if condition is None:
    #             condition = Q(login_date__range=[from_date, to_date])
    #         else:
    #             condition &= Q(login_date__range=[from_date, to_date])
    #     if condition is not None:
    #         obj_data = LoginInfo.objects.filter(condition)[vys_page.get_offset():vys_page.get_query_limit()]
    #     else:
    #         obj_data = LoginInfo.objects.all()[vys_page.get_offset():vys_page.get_query_limit()]
    #
    #     vlist = NWisefinList()
    #     for employee in obj_data:
    #         emp_resp = EmployeeLogResponse()
    #         emp_resp.set_id(employee.id)
    #         emp_obj=Employee.objects.get(id=employee.id)
    #         emp_name=emp_obj.full_name + ' (' + emp_obj.code + ')'
    #         emp_resp.employe_name=emp_name
    #         emp_resp.ip_address=employee.ip_address
    #         date_set=str(employee.login_date)
    #         logout_date=date_set.split('.')
    #         emp_resp.logout_date=logout_date[0]
    #         emp_resp.user_agent=employee.user_info
    #         vpage = NWisefinPaginator(obj_data, vys_page.get_index(), 10)
    #         vlist.set_pagination(vpage)
    #         vlist.append(emp_resp)
    #     return vlist


    def get_employee_info(self,empid_arr):
        obj_data=Employee.objects.filter(id__in=empid_arr).values('id',"full_name","code","employee_branch__code","employee_branch__name")
        vlist = []
        for employee in obj_data:
            employe_name='(' + employee['code'] + ') ' + employee['full_name']
            emp_resp = {"id":employee['id'], "code": employee['code'],"full_name":employe_name,
                        "branch_name": employee['employee_branch__name'],"branch_code":employee['employee_branch__code']}

            vlist.append(emp_resp)
        return vlist

    def get_multi_employee(self,arr):
        data=self.get_employee_info(arr)
        emp_arr=[]
        for i in data:
            j=json.dumps(i,indent=4)
            emp_arr.append(j)
        return emp_arr

    # def updateauthrequest(self,employee_id,data):
    #     update = Authrequest.objects.filter(employee=employee_id).update(created_date=now(),mobile_number=data['mobile_number'])
    #     employeedata = Authrequest.objects.get(employee=employee_id)
    #     return employeedata

# prpo-micro to micro
    def search_Employee(self, query, vys_page):
        condition = (Q(employee__full_name__icontains=query) | Q(employee__code__icontains=query)) & Q(employee__status=1) &Q(entity_id=self._entity_id())
        employeeList = EmployeeEntityMapping.objects.filter(condition)[vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(employeeList)
        employeeList_data = NWisefinList()
        if list_length > 0:
            for obj in employeeList:
                employee = obj.employee
                emp_resp = EmployeeResponse()
                emp_resp.set_id(employee.id)
                disp_name = '(' + employee.code + ') ' + employee.full_name
                emp_resp.set_full_name(disp_name)
                employeeList_data.append(emp_resp)
            vpage = NWisefinPaginator(employeeList, vys_page.get_index(), 10)
            employeeList_data.set_pagination(vpage)
        return employeeList_data

    def fetch_employeedata(self, employee_id):
        employee = Employee.objects.get(id=employee_id)
        emp_data = {"id": employee.id,
                    "code": employee.code,
                    "name": employee.full_name,
                    "fullname": employee.code + "--" + employee.full_name,
                    "full_name": employee.code + "--" + employee.full_name,
                    "employee_branch_id": employee.employee_branch_id,
                    "employee_branch_code": employee.employee_branch.code,
                    "employee_branch_name": employee.employee_branch.name}
        return emp_data

    def employee_get(self, emp_data):
        empId_arr = emp_data.get('employee_id')
        employee = Employee.objects.filter(id__in=empId_arr).values('id', 'code', 'full_name')
        emp_list_data =NWisefinList()
        for i in employee:
            data = {"id": i['id'], "code": i['code'], "name": i['full_name'],
                    "fullname": i['code'] + "--" + i['full_name']}
            emp_list_data.append(data)
        return emp_list_data.get()

    def search_employeename(request, employee_name):
        logger.info("employee: " + str())
        condition1 = (Q(employee__full_name__icontains=employee_name) | Q(employee__code__icontains=employee_name)) & Q(employee__status=1)&Q(entity_id=request._entity_id())
        employee = EmployeeEntityMapping.objects.filter(condition1).values('employee__id', 'employee__code', 'employee__full_name', 'employee__employee_branch_id')
        emp_list_data = NWisefinList()
        for i in employee:
            data = {"id": i['employee__id'],
                    "code": i['employee__code'],
                    "name": i['employee__full_name'],
                    "full_name": i['employee__code'] + "--" + i['employee__full_name'],
                    "employee_branch_id": i['employee__employee_branch_id']}
            emp_list_data.append(data)
        return emp_list_data.get()

    def get_employeecode(self, code):
        try:
            commodity = Employee.objects.get(code=code, status=1)
            comm_data = {"id": commodity.id, "code": commodity.code,
                         "name": commodity.full_name,
                         "full_name": commodity.code + "--" + commodity.full_name}
            return comm_data
        except Employee.DoesNotExist as e:
            print(e)
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(e) + ' : ' + str(code))
            return error_obj

    def employeebranch_get(self, emp_data):
        empId_arr = emp_data.get('employeebranch_id')
        employeebranch = EmployeeBranch.objects.using(self._current_app_schema()).filter(id__in=empId_arr).values('id', 'code',
                                                                                'name', 'gstin',
                                                                                'address_id', 'contact_id')
        employeebranch_list_data = NWisefinList()
        for i in employeebranch:
            data = {"id": i['id'], "code": i['code'], "name": i['name'], "gstin": i["gstin"],
                    "address_id": i["address_id"],
                    "contact_id": i["contact_id"],
                    "fullname": i['code'] + "--" + i['name'],
                    "full_name": i['code'] + "--" + i['name']}
            employeebranch_list_data.append(data)
        return employeebranch_list_data.get()

    def get_employeename(self, name):
        condition1 = (Q(full_name__icontains=name) | Q(code__icontains=name)) & Q(status=1)
        commodity = Employee.objects.filter(condition1)
        emp_list_data = NWisefinList()
        for i in commodity:
            data = {"id": i['id'], "code": i['code'], "name": i['full_name'],
                    "full_name": i['code'] + "--" + i['full_name']}
            emp_list_data.append(data)
        return emp_list_data.get()

    def get_employeedata(self):
        condition1 = Q(status=1)
        commodity = Employee.objects.filter(condition1)
        emp_list_data = NWisefinList()
        for i in commodity:
            data = {"id": i['id'], "code": i['code'],
                    "name": i['full_name'],
                    "designation": i['designation'],
                    "full_name": i['code'] + "--" + i['full_name']}
            emp_list_data.append(data)
        return emp_list_data.get()

    def get_employeename_data(self, emp_data, query):
        empId_arr = emp_data.get('employeebranch_id')
        if (query != '') or (query is not None):
            employee = Employee.objects.filter(id__in=empId_arr, name=query)
        else:
            employee = Employee.objects.filter(id__in=empId_arr)

        emp_list_data = NWisefinList()
        for i in employee:
            data = {"id": i['id'], "code": i['code'],
                    "name": i['full_name'],
                    "designation": i['designation'],
                    "full_name": i['code'] + "--" + i['full_name']}
            emp_list_data.append(data)
        return emp_list_data.get()

    def fetch_ebranchaddressdata(self, empbranch_id):
        empbranch = EmployeeBranch.objects.using(self._current_app_schema()).get(id=empbranch_id)
        employee = EmployeeAddress.objects.using(self._current_app_schema()).get(id=empbranch.address_id)
        emp_data = {"id": employee.id, "line1": employee.line1, "line2": employee.line2,
                    "line3": employee.line3, "pincode_id": employee.pincode_id, "city_id": employee.city_id,
                    "state_id": employee.state_id}
        return emp_data

    def get_employee_designation_department(self,empid):
        try:
            from userservice.service.departmentservice import DepartmentService
            emp = Employee.objects.get(id = empid)
            dept_serv=DepartmentService(self._scope())
            empbranch_serv=EmployeeBranchService(self._scope())
            req_data = EmployeeResponse()
            req_data.set_id(emp.id)
            req_data.set_full_name(emp.full_name)
            req_data.set_code(emp.code)
            req_data.set_designation(emp.designation)
            print('department',emp.department_id,'  , ',empid)
            req_data.department = (dept_serv.fetch_internal_department(emp.department_id))
            req_data.set_grade(emp.grade)
            req_data.set_employee_branch_id(empbranch_serv.fetch_branch(emp.employee_branch_id))
            return req_data
        except Employee.DoesNotExist:
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description("INVALID_EMPLOYEE_ID")
            return error_obj
        except Exception  as excep:
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj


    def emp_branch(self, emp_id):
        employee = Employee.objects.get(id=emp_id)
        emp_name = employee.full_name
        employee_branch_id = employee.employee_branch_id
        try:
            emp_branch = EmployeeBranch.objects.using(self._current_app_schema()).get(id=employee_branch_id)
            emp_obj = EmployeeResponse()
            emp_obj.set_id(emp_branch.id)
            emp_obj.employee_id = emp_id
            emp_obj.name = emp_branch.name
            fullname = '(' + emp_branch.code + ') ' + emp_branch.name
            # emp_obj.set_full_name = emp_branch.code + ' -- ' + emp_branch.name
            emp_obj.set_full_name = fullname
            emp_obj.set_code(emp_branch.code)
            # return emp_obj
        except Exception as e:
            print(e)
            emp_obj = Error()
            emp_obj.error = "Employee: " + emp_name + " not mapped with the EmployeeBranch"
            emp_obj.set_description(str(e) + ' : ' + str(emp_id))
        return emp_obj

    def fetch_employee_id(self):
        condition1 = Q(employee__status=1) & Q(entity_id=self._entity_id())
        employee = EmployeeEntityMapping.objects.filter(condition1).values('employee__id')
        emp_list_data = NWisefinList()
        prod_arr = []
        for i in employee:
            prod_arr.append(i['employee__id'])
        data = {"id": prod_arr}
        emp_list_data.append(data)
        return emp_list_data

    def employeectrlbranch_get(self):
        employeebranch = EmployeeBranch.objects.using(self._current_app_schema()).values('control_office_branch').\
            annotate(id=Count('control_office_branch'))
        employeebranch_list_data = NWisefinList()
        for i in employeebranch:
            data = {"control_office_branch": i['control_office_branch'],
                    "id": i['id']}
            employeebranch_list_data.append(data)
        return employeebranch_list_data


    def ctrl_office_info(self, search_key, vys_page):
        condition = Q(name__icontains=search_key)
        employeebranch = EmployeeBranch.objects.filter(condition)[vys_page.get_offset():vys_page.get_query_limit()]
        employeeList_data = NWisefinList()
        if len(employeebranch) > 0:
            for employee in employeebranch:
                emp_resp = EmployeeResponse()
                emp_resp.set_id(employee.id)
                disp_name = '(' + employee.code + ') ' + employee.name
                emp_resp.set_full_name(disp_name)
                emp_resp.code = employee.code
                emp_resp.name = employee.name
                emp_resp.eb_code = employee.control_office_branch
                employeeList_data.append(emp_resp)
        return employeeList_data

    def fetch_emp_branch_name(self,code,name,gstin,Entity):
        emp_branch = EmployeeBranch.objects.using(self._current_app_schema()).filter(code__iexact=code)
        if len(emp_branch) > 0:
            empbranch_id = emp_branch[0].id
            return empbranch_id
        else:
            emp_branch = EmployeeBranch.objects.using(self._current_app_schema()).create(code=code,name=name,gstin=gstin)
            return emp_branch.id

    def fetch_emp_rm_id(self,rm_id):
        try:
            rm = Employee.objects.using(self._current_app_schema()).get(code__iexact=rm_id)
            rm_id = rm.id
            return rm_id

        except:
            return 0

    def change_password(self, old_password, user_name, new_password):
        if (old_password == new_password) or (len(new_password) < 6):
            resp = Error()
            resp.set_code(ErrorMessage.INVALID_NEW_PASSWORD)
            resp.set_description(ErrorDescription.INVALID_NEW_PASSWORD)
            return resp
        user_authenticate = authenticate(username=user_name, password=old_password)
        if user_authenticate is None:
            resp = Error()
            resp.set_code(ErrorMessage.INVALID_USER_OR_PASSWORD)
            resp.set_description(ErrorDescription.INVALID_USER_OR_PASSWORD)
            return resp
        else:
            print('success')
            print('user_name'+str(user_name))
            print('password'+str(new_password))
            user = User.objects.get(username=user_name)
            user.set_password(new_password)
            user.save()
            resp = NWisefinSuccess()
            resp.set_message(SuccessMessage.CREATE_MESSAGE)
            resp.set_status(SuccessStatus.SUCCESS)
            return resp

    def cemployee_org_info(self,data):
        empid=data['empid']
        orgid=data['orgid']
        emporg = Employee.objects.using(self._current_app_schema()).filter(id__in=empid).update(org_id=orgid)
        resp = NWisefinSuccess()
        resp.set_message(SuccessMessage.UPDATE_MESSAGE)
        resp.set_status(SuccessStatus.SUCCESS)
        return resp

    def getemployee_org_info(self,employeeid):
        emporg = Employee.objects.using(self._current_app_schema()).get(id=employeeid)
        orgid = emporg.org_id
        orgdetails = OrgDetailsService(self._scope()).get_orgdetails_by_id(orgid)
        return orgdetails


class GENDER:
    OTHERS = "-1"
    MALE = "1"
    FEMALE = "2"
    Other_value = 'Others'
    MALE_VALUE = 'Male'
    FEMALE_VALUE = 'Female'

    def getGenderType(request, id):
        data = [{"id": GENDER.OTHERS, "name": GENDER.Other_value},
                {"id": GENDER.MALE, "name": GENDER.MALE_VALUE},
                {"id": GENDER.FEMALE, "name": GENDER.FEMALE_VALUE}]
        for i in data:
            if (int(i['id']) == id):
                return i['name']


class TA_employee_service(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.USER_SERVICE)

    def role_bh_emp_get(self, branch, approver, approver_except):
            employee = EmployeeEntityMapping.objects.filter(employee__employee_branch_id=branch, employee__role="BH", employee__status=1, entity_id=self._entity_id())
            arr = []
            emp_id_arr = []
            filter_grade_list = ["S3", "S4", "S5", "S6", "S7", "L3", "L4", "L5", "L6"]
            for obj in employee:
                emp = obj.employee
                report_res = EmployeeResponse()
                report_res.set_id(emp.id)
                report_res.set_full_name(emp.full_name)
                report_res.set_designation(emp.designation)
                report_res.set_code(emp.code)
                report_res.set_id(emp.id)
                report_res.set_employee_branch_id(emp.employee_branch_id)
                if emp.grade1 in filter_grade_list:
                    if approver is None:
                        if emp.id not in approver_except:
                            arr.append(report_res)
                            emp_id_arr.append(emp.id)
                    if  emp.full_name is not None and emp.code is not None:
                        if approver in emp.full_name.lower() or approver in emp.code.lower():
                            if emp.id not in approver_except:
                                arr.append(report_res)
                                emp_id_arr.append(emp.id)
            return (arr, emp_id_arr)
    def branch_data(self,request,vys_page):

        condition = Q()
        if "data" in request.GET:
            condition &= Q(name__icontains=request.GET.get("data"))|Q(code__icontains=request.GET.get("data"))
        branch_data = EmployeeBranch.objects.using(self._current_app_schema()).filter(condition).values('id', 'code', 'name')[
                   vys_page.get_offset():vys_page.get_query_limit()]
        list_len = len(branch_data)
        branch_list = NWisefinList()
        if list_len <= 0:
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_branch_ID)
            error_obj.set_description(ErrorDescription.INVALID_branch_ID)
            return error_obj
        else:

            for i in branch_data:
                response = empdepartmentres()
                response.set_id(i['id'])
                response.set_code(i['code'])
                response.set_name(i['name'])
                branch_list.append(response)
            vpage = NWisefinPaginator(branch_data, vys_page.get_index(), 10)
            branch_list.set_pagination(vpage)
            return branch_list
    def bs_data(self,request,vys_page):
        condition = Q()
        if "data" in request.GET:
            condition &= Q(name__icontains=request.GET.get("data"))
        bs_datas =BusinessSegment.objects.using(self._current_app_schema()).filter(condition).values('id', 'code', 'name')[
                           vys_page.get_offset():vys_page.get_query_limit()]
        # print(bs_datas)
        list_len = len(bs_datas)
        bs_list = NWisefinList()
        if list_len <= 0:
            return bs_list
        else:

            for i in bs_datas:
                # print(i['code'])
                # print(i['name'])
                response = empdepartmentres()
                response.set_id(i['id'])
                response.set_code(i['code'])
                response.set_name(i['name'])
                bs_list.append(response)
            vpage = NWisefinPaginator(bs_datas, vys_page.get_index(), 10)
            bs_list.set_pagination(vpage)
            return bs_list

    def employee_details_get(self,empid):
        emp = Employee.objects.filter(id = empid)
        req_data = EmployeeResponse()
        if len (emp)==0:
            req_data.set_id(None)
            req_data.set_full_name(None)
            req_data.set_code(None)
            req_data.set_designation(None)
            req_data.set_grade(None)
            req_data.set_employee_branch_id(None)
            req_data.set_employee_branch_name(None)
        else:
            emp=emp[0]
            req_data = EmployeeResponse()
            req_data.set_id(emp.id)
            req_data.set_full_name(emp.full_name)
            req_data.set_code(emp.code)
            req_data.set_designation(emp.designation)
            req_data.set_grade(emp.grade)
            req_data.set_employee_branch_id(emp.employee_branch_id)
            req_data.set_employee_branch_name(emp.employee_branch.name)
        return req_data

    def employee_teamdetails_get(self, empid):
        emp_dept = EmployeeDepartmentPermission.objects.using(self._current_app_schema()).filter(
            employee_id=empid).order_by("department_id")
        if len(emp_dept) == 0:
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_DEPARTMENT_ID)
            error_obj.set_description(ErrorDescription.INVALID_DEPARTMENT_ID)
            return error_obj
        team = Department.objects.using(self._current_app_schema()).get(id=(emp_dept.first()).department_id)
        sub_team = Department.objects.using(self._current_app_schema()).get(id=(emp_dept.last()).department_id)
        req_data = EmployeeResponse()
        team_id = team.id
        sub_team_id = sub_team.id
        req_data.set_team(team_id)
        req_data.set_sub_team(sub_team_id)
        return req_data


    def employee_details_arr(self,empid):
        emp = Employee.objects.filter(id__in = empid).values("full_name","id","code")

        return emp
    def create_department_get(self,request,vys_page):
        condition = Q()
        if "data" in request.GET:
            condition &= Q(name__icontains=request.GET.get("data"))
        department_datas=Department.objects.using(self._current_app_schema()).filter(condition).values('id','code','name')[
                         vys_page.get_offset():vys_page.get_query_limit()]
        print(department_datas)
        list_len = len(department_datas)
        deparetment_list = NWisefinList()
        if list_len <= 0:
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_DEPARTMENT_ID)
            error_obj.set_description(ErrorDescription.INVALID_DEPARTMENT_ID)
            return error_obj
        else:

            for i in department_datas:
                # print(i['code'])
                # print(i['name'])
                response = empdepartmentres()
                response.set_id(i['id'])
                response.set_code(i['code'])
                response.set_name(i['name'])
                deparetment_list.append(response)
            vpage = NWisefinPaginator(department_datas, vys_page.get_index(), 10)
            deparetment_list.set_pagination(vpage)
            return deparetment_list

    def get_branch_data(self, branch):
        branch_details = EmployeeBranch.objects.filter(id=branch)
        if len(branch_details) == 0:
            resp = EmployeeBranchResponse()
            resp.set_name(None)
            resp.set_code(None)
            resp.set_id(None)
        else:
            resp = EmployeeBranchResponse()
            branch_details = branch_details[0]
            resp.set_name(branch_details.name)
            resp.set_code(branch_details.code)
            resp.set_id(branch_details.id)
            resp.set_address_id(branch_details.address_id)
        return resp
    def get_address_data(self, id):
        address_details = EmployeeAddress.objects.filter(id=id)
        if len(address_details) == 0:
            resp = AddressResponse()
            # resp.set_name(None)
            # resp.set_code(None)
            resp.set_city_id(None)
            resp.set_district_id(None)
            resp.set_district_id(None)
            resp.set_pincode_id(None)

            resp.set_id(None)
        else:
            resp = AddressResponse()
            address_details = address_details[0]
            resp.set_city_id(address_details.city_id)
            resp.set_district_id(address_details.district_id)
            resp.set_district_id(address_details.district_id)
            resp.set_pincode_id(address_details.pincode_id)
            resp.set_state_id(address_details.state_id)
        return resp

    def employee_all_details_get(self,empid):
        emp = Employee.objects.filter(id = empid)
        emp=emp[0]
        req_data = EmployeeResponse()
        req_data.set_id(emp.id)
        req_data.set_full_name(emp.full_name)
        req_data.set_code(emp.code)
        req_data.set_designation(emp.designation)
        req_data.set_grade(emp.grade)
        req_data.set_grade1(emp.grade1)
        req_data.set_department_id(emp.department_id)
        req_data.set_employee_branch_id(emp.employee_branch_id)
        req_data.set_accountnumber(emp.accountnumber)
        req_data.set_gender(emp.gender)
        req_data.set_branch_gst(emp.employee_branch.gstin)
        return req_data


    def employee_acc_no_get_ta(self,empid):
        acc_details = EmployeeAccountDetails.objects.filter(employee = empid,paymode=4).last()
        req_data = EmployeeResponse()
        if acc_details is not None:
            req_data.set_accountnumber(acc_details.account_number)
        else:
            req_data.set_accountnumber(0)
        return req_data

    # def employee_report_approval(self, data, user_id):
    #     logger.info(str(data))
    #
    #     if not data.get_id() is None:
    #         employee = EmployeeReportAproval.objects.filter(id=data.get_id()).update(employee_id=data.get_employee_id(),
    #                                            reporting_manager=data.get_reporting_manager(),
    #                                            approving_manager=data.get_approving_manager(),
    #                                            status=data.get_status(),
    #                                            updated_by=emp_id,
    #                                            updated_date=now,)
    def branch_employee_get(self, branch_id,query,vys_page,maker):
        condition = Q(entity_id=self._entity_id())
        if int(branch_id)==0:
            condition &= Q(employee__status=1)
        else:
            condition &= Q(employee__employee_branch_id=branch_id,employee__status=1)
        if query != None:
            condition &= (Q(employee__full_name__icontains=query) | Q(employee__code__icontains=query))
        if maker is None:
            employeeList = EmployeeEntityMapping.objects.filter(condition).order_by('employee__created_date')[vys_page.get_offset():vys_page.get_query_limit()]
        else:
            employeeList = EmployeeEntityMapping.objects.filter(condition).exclude(employee__id__in=[maker]).order_by('employee__created_date')[vys_page.get_offset():vys_page.get_query_limit()]
        employeeList_data = NWisefinList()
        for obj in employeeList:
            employee = obj.employee
            emp_resp = EmployeeResponse()
            emp_resp.set_id(employee.id)
            disp_name = '(' + employee.code + ') ' + employee.full_name
            emp_resp.set_full_name(disp_name)
            emp_resp.code = employee.code
            emp_resp.name = employee.full_name
            employeeList_data.append(emp_resp)
        vpage = NWisefinPaginator(employeeList, vys_page.get_index(), 10)
        employeeList_data.set_pagination(vpage)
        return employeeList_data

    def login_emp_details_get(self,userid):
        try:
            employee = Employee.objects.get(user_id=userid)
            deptid=(EmployeeDepartmentPermission.objects.using(self._current_app_schema()).get(employee=employee.id, entity_id=self._entity_id())).department_id
            emp_data = {"id":employee.id,"name": employee.full_name, "code": employee.code, "grade": employee.grade,
                        "designation": employee.designation, "employee_branch_id": employee.employee_branch_id,
                        "employee_department_id":deptid}
        except:
            emp_data = {"id": userid, "name": None, "code": None, "grade": None,
                        "designation": None, "employee_branch_id": None, "employee_department_id": None}
        employee_dic = json.dumps(emp_data, indent=4)
        return HttpResponse(employee_dic, content_type='application/json')

    def get_emp_grade1(self,id):
        try:
            user = Employee.objects.get(id=id)
            return user.grade1
        except:
            return None

    def get_branch_details(self,branch_json):
        branch_arr = branch_json['id']
        branch_details = EmployeeBranch.objects.using(self._current_app_schema()).filter(id__in=branch_arr).values('id','name','code')
        arr=[]
        for data in branch_details:
            branch_data = {"id":data['id'],"name": data['name'], "code": data['code']}
            arr.append(branch_data)
        branch_dict = json.dumps(arr, indent=4)
        return HttpResponse(branch_dict, content_type='application/json')

    def bank_gst_get(self,gst,vys_page):
        resp_list = NWisefinList()
        gst_list = EmployeeBranch.objects.filter(Q(name__icontains=gst)|Q(gstin__icontains=gst)).all() [vys_page.get_offset():vys_page.get_query_limit()]
        for data in gst_list:
            req_data=Employee_data_resp()
            req_data.set_bankgstno(data.gstin)
            req_data.set_bank_name(data.name)

            resp_list.append(req_data)
        vpage = NWisefinPaginator(gst_list, vys_page.get_index(), 10)
        resp_list.set_pagination(vpage)

        return resp_list

    def emp_dept_get(self,empid):
        resp_list = NWisefinList()
        dept_data = EmployeeDepartmentPermission.objects.filter(employee_id=empid)[0]
        return dept_data

    def check_permission_ta(self, emp_id):

        # department = EmployeeDepartmentPermission.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),employee_id=emp_id)
        department = EmployeeDepartmentPermission.objects.using(self._current_app_schema()).filter(employee_id=emp_id)
        dept_array=[]
        for each_dept in department:
            dept_array.append(each_dept.department_id)

        CEO=False
        HR=False
        ADMIN=False
        CEO_ADMIN=False
        dept_data = Department.objects.using(self._current_app_schema()).filter(id__in=dept_array)
        for each_team in dept_data:
            if (employee_team_ta.ceo).lower() in (each_team.name).lower():
                CEO=True
            if (employee_team_ta.hr).lower() in (each_team.name).lower():
                HR=True
            if (employee_team_ta.admin).lower() in (each_team.name).lower():
                ADMIN=True
            if (employee_team_ta.ceo_admin).lower() in (each_team.name).lower():
                CEO_ADMIN=True

        return json.dumps({employee_team_ta.ceo: CEO, employee_team_ta.hr: HR, employee_team_ta.admin: ADMIN, employee_team_ta.ceo_admin: CEO_ADMIN})

    def ceo_team_get_ta_check(self,login_id,query):
        onb=self.ceo_team_get_ta(login_id,query)
        if len(onb.data) > 0:
            return json.dumps({"onbehalf": True})
        else:
            return json.dumps({"onbehalf": False})



    def ceo_team_get_ta(self,login_id,query):
        ceo_team_check=self.check_permission_ta(login_id)
        if json.loads(ceo_team_check)['CEO Office - Admin']==False:
            vlist = NWisefinList()
            return vlist
        ceo_team=Department.objects.using(self._current_app_schema()).filter(name__icontains="ceo")
        ceo_arr=[]
        for each_team in ceo_team:
            ceo_arr.append(each_team.id)
        emp_id=[]
        ceo_team = EmployeeDepartmentPermission.objects.using(self._current_app_schema()).filter(department_id__in=ceo_arr)
        for each_emp in ceo_team:
            emp_id.append(each_emp.employee_id)
        obj_data = Employee.objects.filter(id__in=emp_id).exclude(id=login_id)
        vlist = NWisefinList()
        for employee in obj_data:
            emp_resp = EmployeeResponse()

            emp_resp.set_id(employee.id)
            # employe_name = '(' + employee['code'] + ') ' + employee['full_name']
            # emp_resp.employe_name = employe_name
            emp_resp.set_full_name(employee.full_name)
            emp_resp.set_code(employee.code)
            # emp_resp.set_branch_name (employee.employee_branch__name)
            # emp_resp.set_branch_code (employee.employee_branch__code)
            # emp_resp.set_branch_id (employee.employee_branch__id)
            if query is not None:
                if query.lower() in (employee.full_name).lower() or query.lower() in (employee.code).lower():
                    vlist.append(emp_resp)
            else:
                vlist.append(emp_resp)
        return vlist

    def emp_team_get(self,emp_id):
        emp_dept=EmployeeDepartmentPermission.objects.using(self._current_app_schema()).filter(employee_id=emp_id).order_by("department_id")
        if len(emp_dept)!=2:
            team_name="Team not assigned"
            sub_team_name="Sub-Team not assigned"
        else:
            team=Department.objects.using(self._current_app_schema()).get(id=(emp_dept.first()).department_id)
            sub_team=Department.objects.using(self._current_app_schema()).get(id=(emp_dept.last()).department_id)
            team_name=team.name
            sub_team_name=sub_team.name
        return {"team":team_name,"sub_team":sub_team_name}

    def team_name(self,team,sub_team):
        team = Department.objects.using(self._current_app_schema()).get(id=team)
        sub_team = Department.objects.using(self._current_app_schema()).get(id=sub_team)
        team_name = team.name
        sub_team_name = sub_team.name
        return {"team": team_name, "sub_team": sub_team_name}

    def emp_team_arr(self,emp_id):
        emp_dept=EmployeeDepartmentPermission.objects.using(self._current_app_schema()).filter(employee_id__in=emp_id).values("department__name","employee_id","id")
        return emp_dept

    def checker_details(self, checker_id):
        checker = Employee.objects.using(self._current_app_schema()).filter(
            id=checker_id)[0]
        return checker

    def maker_details(self, maker_id):
        maker = Employee.objects.using(self._current_app_schema()).filter(
            id=maker_id)[0]
        return maker

    def admin_details1(self):
        department_id = Department.objects.using(self._current_app_schema()).filter(
            name='Admin')[0].id

        admin = EmployeeDepartmentPermission.objects.using(self._current_app_schema()).filter(
            department_id=department_id).values('employee_id')
        print('admin',admin)
        admin_mail_id = []
        for i in admin:
            mail_id = Employee.objects.using(self._current_app_schema()).filter(
                id=i['employee_id']).values('email_id')
            admin_mail_id.append(mail_id)
        print('admin_mail_id',admin_mail_id)
        return admin_mail_id

    def admin_details2(self):
        department_id = Department.objects.using(self._current_app_schema()).filter(
            name='Admin').last().id

        admin = EmployeeDepartmentPermission.objects.using(self._current_app_schema()).filter(
            department_id=department_id).values('employee_id')
        print('admin',admin)
        admin_mail_id = []
        for i in admin:
            mail_id = Employee.objects.using(self._current_app_schema()).filter(
                id=i['employee_id']).values('email_id')
            admin_mail_id.append(mail_id)
        print('admin_mail_id',admin_mail_id)
        return admin_mail_id

    def emp_id_get(self,emp_name):
        condition=Q(full_name__icontains=emp_name)|Q(code__icontains=emp_name)
        maker = Employee.objects.using(self._current_app_schema()).filter(condition)
        arr=[]
        for data in maker:
            arr.append(data.id)
        return arr
    def emp_branchid(self,branch_id):
        condition=Q(employee_branch_id=branch_id)
        maker = Employee.objects.using(self._current_app_schema()).filter(condition)
        arr=[]
        for data in maker:
            arr.append(data.id)
        return arr

    def branch_dropdown(self,employee_branch,vys_page):
        condition=Q(status=1)
        if employee_branch!=None:
            condition&=Q(name__icontains=employee_branch)|Q(code__icontains=employee_branch)
            branch_drop=EmployeeBranch.objects.using(self._current_app_schema()).filter(condition)[vys_page.get_offset():vys_page.get_query_limit()]
        else:
            branch_drop = EmployeeBranch.objects.using(self._current_app_schema()).filter(condition)[vys_page.get_offset():vys_page.get_query_limit()]
        resp_list=NWisefinList()
        for data in branch_drop:
            res_list=EmployeeResponse()
            res_list.set_branch(data.name)
            res_list.set_id(data.id)
            res_list.set_code(data.code)
            resp_list.append(res_list)
        vpage = NWisefinPaginator(branch_drop, vys_page.get_index(), 10)
        resp_list.set_pagination(vpage)

        return resp_list



