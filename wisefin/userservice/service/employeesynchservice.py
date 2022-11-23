import traceback
from dateutil import parser
from django.db import IntegrityError, transaction

from masterservice.models import BankBranch
from masterservice.service.designationservice import DesignationService
from userservice.data.response.hierarchyresponse import HierarchyResponse
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinlist import NWisefinList
from userservice.models import EmployeeHierarchy
from django.utils import timezone
import json
from userservice.models import Employee, User, LogoutInfo
from utilityservice.data.response.nwisefinerror import NWisefinError as Error
from userservice.data.response.employeesynchresponse import EmployeeSynchResponse
from django.utils.timezone import now

from utilityservice.service.api_service import ApiService
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from nwisefin.settings import logger
from userservice.models.usermodels import Employee, EmployeeAddress, EmployeeContact, EmployeeEntityMapping, Department, \
    EmployeeBranch, EmployeeDepartmentPermission, EmployeeAccountDetails


class EmployeeSynchService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.USER_SERVICE)

    def create_data(self, emp_obj, address_obj, contact_obj,acc_obj, emp_id, emp_code, Entity, request):
        Error_code = 0
        try:
            with transaction.atomic(using=self._current_app_schema()):
                Error_code = 1
                address = EmployeeAddress.objects.using(self._current_app_schema()).create(
                    line1=address_obj.get_line1(),
                    line2=address_obj.get_line2(), line3=address_obj.get_line3(),
                    pincode_id=address_obj.get_pincode_id(),
                    city_id=address_obj.get_city_id(),
                    district_id=address_obj.get_district_id(),
                    state_id=address_obj.get_state_id(),
                    created_by=emp_id)
                # employee = Employee.objects.get(id=emp_obj.get_id())
                logger.info('Employee Address Created Success')
                emp_resp = EmployeeSynchResponse()
                addr_resp = {"Message": "Success", 'address_id': address.id}
                # return emp_resp

                Error_code = 2
                contact = EmployeeContact.objects.using(self._current_app_schema()).create(
                    type_id=contact_obj.get_type_id(),
                    name=contact_obj.get_name(),
                    designation_id=emp_obj.get_designation(),
                    landline=contact_obj.get_landline(),
                    landline2=contact_obj.get_landline2(),
                    mobile=contact_obj.get_mobile(),
                    mobile2=contact_obj.get_mobile2(),
                    email=contact_obj.get_email(),
                    dob=parser.parse(contact_obj.get_dob()),
                    wedding_date=contact_obj.get_wedding_date(),
                    created_by=emp_id)
                # employee = Employee.objects.get(id=emp_obj.get_id())
                logger.info('Employee Contact Create Success')
                emp_resp = EmployeeSynchResponse()
                cont_resp = {"Message": "Success", 'contact_id': contact.id}
                # return emp_resp

                Error_code = 3
                auth_user_id = None
                Auth_User = User.objects.create_user(username=emp_obj.get_code(), password=emp_obj.get_code())
                Auth_User_id = Auth_User.id
                logger.info('Employee Auth User Created Success')


                Error_code = 4
                new_employee_id = None
                print(emp_obj.get_employee_branch())
                employee = Employee.objects.using(self._current_app_schema()).create(full_name=emp_obj.get_full_name(),
                                                                                     first_name=emp_obj.get_first_name(),
                                                                                     middle_name=emp_obj.get_middle_name(),
                                                                                     last_name=emp_obj.get_last_name(),
                                                                                     code=emp_obj.get_code(),
                                                                                     designation=emp_obj.get_designation(),
                                                                                     grade=emp_obj.get_grade(),
                                                                                     user_id=Auth_User_id,
                                                                                     employee_branch_id=emp_obj.get_employee_branch(),
                                                                                     email_id=emp_obj.get_email_id(),
                                                                                     dob=str(emp_obj.get_dob()),
                                                                                     doj=str(emp_obj.get_doj()),
                                                                                     gender=emp_obj.get_gender(),
                                                                                     # phone_no = emp_obj.get_phone_no(),
                                                                                     # supervisor =emp_obj.get_supervisor(),
                                                                                     # hierarchy =emp_obj.get_hierarchy(),
                                                                                     # branch=emp_obj.get_branch(),
                                                                                     # costcentre=emp_obj.get_costcentre(),
                                                                                     # businesssegment =emp_obj.get_businesssegment(),
                                                                                     address_id=addr_resp['address_id'],
                                                                                     contact_id=cont_resp['contact_id'],
                                                                                     RM=emp_obj.get_rm_id(),
                                                                                     functional_head=emp_obj.get_functional_head_id(),
                                                                                     created_by=emp_id,
                                                                                     lastsync_date=now(),
                                                                                     srlno=emp_obj.get_srlno(),
                                                                                     accountnumber=emp_obj.get_accountnumber(),
                                                                                     grade1=emp_obj.get_grade1(),
                                                                                     grade1_date=emp_obj.get_grade1_date(),
                                                                                     grade2=emp_obj.get_grade2(),
                                                                                     grade2_date=emp_obj.get_grade2_date(),
                                                                                     noticeperiod=emp_obj.get_noticeperiod(),
                                                                                     role=emp_obj.get_role(),
                                                                                     department_id=emp_obj.get_department_id())
                logger.info('Employee Details Created Success')
                new_employee_id = employee.id
                # emp_resp = EmployeeSynchResponse()

                Error_code = 5
                auth_user_id = None
                EmployeeEntityMapping_Res = EmployeeEntityMapping.objects.create(entity_id=Entity,
                                                                                 employee_id=new_employee_id)
                Auth_User_id = Auth_User.id
                logger.info('Employee Auth User Created Success')
                log_msg = {"Message": "Single Employee Created Successfully", "Emp Code": emp_obj.get_code()}
                logger.info(log_msg)

                Error_code = 6
                emp_dept = EmployeeDepartmentPermission.objects.using(self._current_app_schema()).filter(
                    entity_id=Entity,
                    department_id=emp_obj.get_department_id(),
                    employee_id=employee.id)
                if len(emp_dept) > 0:
                    print(employee, "employee")
                else:
                    emp_dept = EmployeeDepartmentPermission.objects.using(self._current_app_schema()).create(
                        entity_id=Entity,
                        department_id=emp_obj.get_department_id(),
                        employee_id=employee.id)
                logger.info('Employee Account Permission Success')

                Error_code =7
                emp_dept = EmployeeAccountDetails.objects.using(self._current_app_schema()).create(
                    entity_id=Entity,
                    employee=employee.id,
                    bank=acc_obj.get_bank_name(),
                    bankbranch=acc_obj.get_branch_name(),
                    account_number=acc_obj.get_account_number(),
                    beneficiary_name=acc_obj.get_beneficiary_name(),
                    paymode=4,created_by=emp_id,created_date=now())

                logger.info('Employee Account Details Created Success')


                emp_resp = {"Message": "Success", "Code": str(0)}
                return emp_resp

        except Exception as e:
            error_mst = {"Message": "Failed", "Error_Code": str(Error_code), "Employee_Code": emp_code,
                         "Error_Description": str(e)}
            logger.info(error_mst)
            transaction.rollback()
            traceback.print_exc()
            return error_mst
