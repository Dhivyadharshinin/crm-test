import json
import re

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from userservice.data.request.branchrequest import EmployeeBranchRequest
from userservice.models import Department
from userservice.service.employeeservice import EmployeeService
from utilityservice.data.response.nwisefinerror import NWisefinError as Error
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from userservice.service.employeesynchservice import EmployeeSynchService
from userservice.data.request.employeesynchrequest import EmployeeSynchRequest, AddressSynchRequest, \
    ContactSynchRequest, AccountDetailsSynchRequest
from nwisefin.settings import logger
from django.utils.timezone import now
from wisefinapi.masterapi import MasterAPI
from utilityservice.service.api_service import ApiService


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def employeesynchcontroller_data(request):
    if request.method == 'POST':
        scope = request.scope
        employee_synch_service = EmployeeSynchService(scope)
        service_data = json.loads(request.body)
        TRANSACTION_START_TIME_D = now()
        TRANSACTION_START_TIME = TRANSACTION_START_TIME_D.strftime("%d/%m/%Y %H:%M:%S")
        temp_data = {"Synch_Data": service_data, "Employee_Synch_Start_Time": TRANSACTION_START_TIME}
        logger.info('Employee Synch Stared')
        logger.info(temp_data)
        user_id = request.user.id
        emp_service = EmployeeService(scope)
        empid = emp_service.get_empid_from_userid(user_id)
        Action = service_data.get("Action")
        Type = service_data.get("Type")

        success_count = 0
        fail_count = 0
        final_execute = 1
        fail_data_all = []
        All_Service_Data = service_data.get("Data")
        All_Data_len = len(All_Service_Data)
        if (Action == "Insert" and Type == "Employee"):
            for single_data in All_Service_Data:
                final_execute = 1
                single_emp = single_data.get("Employee")
                Account_details = single_data.get("Account_details")
                Entity = single_data.get("Entity")
                regex = re.compile('[@_!#$%^&*()<>?/\|}{~:,`]')
                alpha = re.compile('[@_!#$%^&*()<>?/a-zA-Z\|}{~:,`]')
                pat = "^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{1,3}$"

                department_name = single_emp.get("department_name")
                employee_branch_code = single_emp.get("employee_branch_code")
                employee_branch_name = single_emp.get("employee_branch_name")
                gstin = single_emp.get("gstin")
                designation = single_emp.get("designation")
                emp_code = single_emp.get("code")
                rm_code = single_emp.get("rm_code")
                functional_head_code = single_emp.get("functional_head_code")
                bank_name=single_data.get("Account_details").get("bank_name")
                bank_branch_name=single_data.get("Account_details").get("branch_name")
                ifsc_code=single_data.get("Account_details").get("ifsc_code")
                all_master = ApiService(scope)

                if (department_name == None or department_name == ""):
                    final_execute = 0
                    error_mst = {"Message": 'Failed', "Employee_Code": emp_code,
                                 "Error_Description": "department_name is mandatory field"}
                    fail_data_all.append(error_mst)
                else:
                    department_id=all_master.get_department_name(department_name,Entity)
                    single_emp['department_id'] = department_id

                if (employee_branch_code==None or employee_branch_code=="" or employee_branch_name == None or employee_branch_name == "" or gstin==None or gstin==""):
                    final_execute = 0
                    error_mst = {"Message": 'Failed', "Employee_Code": emp_code,
                                 "Error_Description": "employee_branch_code and employee_branch_name and GST_number is mandatory field"}
                    fail_data_all.append(error_mst)
                else:
                    employee_branch_id=all_master.get_emp_branch_name(employee_branch_code,employee_branch_name,gstin,Entity)
                    single_emp['employee_branch'] = str(employee_branch_id)


                if (designation == None or designation == ""):
                    final_execute = 0
                    error_mst = {"Message": 'Failed', "Employee_Code": emp_code,
                                 "Error_Description": "designation is mandatory field"}
                    fail_data_all.append(error_mst)
                else:
                    designation_id=all_master.get_designation_name(designation,Entity)
                    single_emp['designation']=str(designation_id)

                if  rm_code == None or rm_code == " ":
                    final_execute = 0
                    error_mst = {"Message": 'Failed', "Employee_Code": emp_code,
                                 "Error_Description": "EMP code not available", "Error_Code": "4"}
                    fail_data_all.append(error_mst)
                else:
                    rm_id=all_master.fetch_rm_code(rm_code)
                    if(rm_id!=0):
                        single_emp['rm_id'] = rm_id
                    else:
                        final_execute = 0
                        error_mst = {"Message": 'Failed', "Employee_Code": emp_code,
                                     "Error_Description": "RM invalid", "Error_Code": "4"}
                        fail_data_all.append(error_mst)

                if  functional_head_code == None or functional_head_code == " ":
                    final_execute = 0
                    error_mst = {"Message": 'Failed', "Employee_Code": emp_code,
                                 "Error_Description": "EMP code not available", "Error_Code": "4"}
                    fail_data_all.append(error_mst)
                else:
                    fun_id=all_master.fetch_rm_code(functional_head_code)
                    if (fun_id != 0):
                        single_emp['functional_head_id'] = fun_id
                    else:
                        final_execute = 0
                        error_mst = {"Message": 'Failed', "Employee_Code": emp_code,
                                     "Error_Description": "Functional head invalid", "Error_Code": "4"}
                        fail_data_all.append(error_mst)
                if (Account_details.get("account_number") == None):
                    final_execute = 0
                    error_mst = {"Message": 'Failed', "Employee_Code": emp_code,
                                 "Error_Description": "Account number less than 16 digits",
                                 "Error_Code": "4"}
                    fail_data_all.append(error_mst)
                else:
                    single_emp['accountnumber'] = Account_details.get("account_number")

                emp_obj = EmployeeSynchRequest(single_emp)

                if (Entity == None or Entity == "" or Entity == 0 or Entity == '0'):
                    final_execute = 0
                    error_mst = {"Message": 'Failed', "Employee_Code": emp_code,
                                 "Error_Description": "Entity is mandatory field"}
                    fail_data_all.append(error_mst)


                if emp_obj.code == None or emp_obj.code == "" or len(emp_obj.code) == 0:
                    final_execute = 0
                    error_mst = {"Message": 'Failed', "Employee_Code": emp_code,
                                 "Error_Description": "Missing the emp_code", "Error_Code": "4"}
                    fail_data_all.append(error_mst)


                if (regex.search(emp_obj.full_name) != None):
                    final_execute = 0
                    error_mst = {"Message": 'Failed', "Employee_Code": emp_code,
                                 "Error_Description": "Invalid the full_name or special characters",
                                 "Error_Code": "4"}
                    fail_data_all.append(error_mst)

                if emp_obj.full_name == None or emp_obj.full_name == "" or len(emp_obj.full_name) == 0:
                    final_execute = 0
                    error_mst = {"Message": 'Failed', "Employee_Code": emp_code,
                                 "Error_Description": "Missing the full_name",
                                 "Error_Code": "4"}
                    fail_data_all.append(error_mst)

                if emp_obj.dob == None or emp_obj.dob == " ":
                    final_execute = 0
                    error_mst = {"Message": 'Failed', "Employee_Code": emp_code, "Error_Description": "Missing the dob",
                                 "Error_Code": "4"}
                    fail_data_all.append(error_mst)

                if emp_obj.doj == None or emp_obj.doj == " ":
                    final_execute = 0
                    error_mst = {"Message": 'Failed', "Employee_Code": emp_code, "Error_Description": "Missing the doj",
                                 "Error_Code": "4"}
                    fail_data_all.append(error_mst)

                if emp_obj.email_id == None or emp_obj.email_id == " " or len(emp_obj.email_id) == 0:
                    final_execute = 0
                    error_mst = {"Message": 'Failed', "Employee_Code": emp_code,
                                 "Error_Description": "Missing the email_id",
                                 "Error_Code": "4"}
                    fail_data_all.append(error_mst)

                validate_email = re.match(pat, emp_obj.email_id)
                if validate_email == None:
                    final_execute = 0
                    error_mst = {"Message": 'Failed', "Employee_Code": emp_code,
                                 "Error_Description": "Missing the @ or .",
                                 "Error_Code": "4"}
                    fail_data_all.append(error_mst)

                if emp_obj.gender == None or emp_obj.gender == " ":
                    final_execute = 0
                    error_mst = {"Message": 'Failed', "Employee_Code": emp_code,
                                 "Error_Description": "Missing the gender", "Error_Code": "4"}
                    fail_data_all.append(error_mst)





                single_emp = single_data.get("Address")
                state_name = single_data.get("Address").get("state_name")
                country_name = single_data.get("Address").get("country_name")
                city_name = single_data.get("Address").get("city_name")
                pincode_id = single_data.get("Address").get("pincode_no")
                district_name = single_data.get("Address").get("district_name")
                all_master=ApiService(scope)

                if country_name == None or country_name == " " or country_name == 0:
                    final_execute = 0
                    error_mst = {"Message": 'Failed', "Employee_Code": emp_code,
                                 "Error_Description": "Missing the country_name", "Error_Code": "1"}
                    fail_data_all.append(error_mst)
                else:
                    country_name = all_master.create_country_sync(country_name,Entity)
                    if(country_name==0):
                        final_execute = 0
                        error_mst = {"Message": 'Failed', "Employee_Code": emp_code,
                                     "Error_Description": " pls add to country table", "Error_Code": "1"}
                        fail_data_all.append(error_mst)
                    else:
                        single_emp['country_name'] = country_name

                if  state_name == None or state_name == " " or state_name == 0:
                    final_execute = 0
                    error_mst = {"Message": 'Failed', "Employee_Code": emp_code,
                                 "Error_Description": "Missing the state_name", "Error_Code": "1"}
                    fail_data_all.append(error_mst)
                else:
                    state_name = all_master.create_state_sync(state_name,country_name,Entity)
                    single_emp['state_id'] = state_name

                if  district_name == None or district_name == " " or district_name == 0:
                    final_execute = 0
                    error_mst = {"Message": 'Failed', "Employee_Code": emp_code,
                                 "Error_Description": "Missing the district_name", "Error_Code": "1"}
                    fail_data_all.append(error_mst)
                else:
                    district_name = all_master.create_district_sync(district_name,state_name,Entity)
                    single_emp['district_id'] = district_name

                if  city_name == None or city_name == " " or city_name == 0:
                    final_execute = 0
                    error_mst = {"Message": 'Failed', "Employee_Code": emp_code,
                                 "Error_Description": "Missing the city_name", "Error_Code": "1"}
                    fail_data_all.append(error_mst)
                else:
                    city_name = all_master.create_city_sync(city_name,state_name,Entity)
                    single_emp['city_id'] = city_name

                if pincode_id == None or pincode_id == " " or pincode_id == 0:
                    final_execute = 0
                    error_mst = {"Message": 'Failed', "Employee_Code": emp_code,
                                 "Error_Description": "Missing the pincode_id", "Error_Code": "1"}
                    fail_data_all.append(error_mst)
                else:
                    pincode_id=all_master.create_pincode_sync(pincode_id,city_name,district_name,Entity)
                    single_emp['pincode_id'] = pincode_id

                add_obj = AddressSynchRequest(single_emp)
                if add_obj.line1 == None or add_obj.line1 == " " or len(add_obj.line1) == 0:
                    final_execute = 0
                    error_mst = {"Message": 'Failed', "Employee_Code": emp_code,
                                 "Error_Description": "Missing the line1", "Error_Code": "1"}
                    fail_data_all.append(error_mst)

                single_emp = single_data.get("Contact")
                single_emp['type_id']=1
                cont_obj = ContactSynchRequest(single_emp)

                check_special_char_account_number = (Account_details.get("account_number").isdecimal())
                if (check_special_char_account_number == False):
                    final_execute = 0
                    error_mst = {"Message": 'Failed', "Employee_Code": emp_code,
                                 "Error_Description": "Accountnumber not allow special character",
                                 "Error_Code": "4"}
                    fail_data_all.append(error_mst)



                if cont_obj.name == None or cont_obj.name == " " or len(cont_obj.name) == 0 or regex.search(
                        cont_obj.name):
                    final_execute = 0
                    error_mst = {"Message": 'Failed', "Employee_Code": emp_code,
                                 "Error_Description": "Missing the name", "Error_Code": "2"}
                    fail_data_all.append(error_mst)

                if cont_obj.type_id == None or cont_obj.type_id == " ":
                    final_execute = 0
                    error_mst = {"Message": 'Failed', "Employee_Code": emp_code,
                                 "Error_Description": "Missing the type_id", "Error_Code": "2"}
                    fail_data_all.append(error_mst)

                check_special_char_mobile = (cont_obj.mobile.isdecimal())
                if (check_special_char_mobile == False):
                    final_execute = 0
                    error_mst = {"Message": 'Failed', "Employee_Code": emp_code,
                                 "Error_Description": "Invalid the mobile number", "Error_Code": "2"}
                    fail_data_all.append(error_mst)
                if cont_obj.mobile == None or cont_obj.mobile == " " or len(cont_obj.mobile) == 0:
                    final_execute = 0
                    error_mst = {"Message": 'Failed', "Employee_Code": emp_code,
                                 "Error_Description": "Missing the emp_code", "Error_Code": "2"}
                    fail_data_all.append(error_mst)

                if (bank_name == None or bank_name == ""):
                    final_execute = 0
                    error_mst = {"Message": 'Failed', "Employee_Code": emp_code,
                                 "Error_Description": "Bank name is mandatory field"}
                    fail_data_all.append(error_mst)
                else:
                    bk_id = all_master.fetch_bank_sync(bank_name)
                    if (bk_id != 0):
                        Account_details['bank_name'] = bk_id
                    else:
                        final_execute = 0
                        error_mst = {"Message": 'Failed', "Employee_Code": emp_code,
                                     "Error_Description": "Bank Name is not in MasterTable", "Error_Code": "4"}
                        fail_data_all.append(error_mst)

                if (bank_branch_name == None or bank_branch_name == "" or ifsc_code == None or ifsc_code == ""):
                    final_execute = 0
                    error_mst = {"Message": 'Failed', "Employee_Code": emp_code,
                                 "Error_Description": "Bank branch name is mandatory field"}
                    fail_data_all.append(error_mst)
                else:
                    branch_id = all_master.fetch_bank_branch_sync(bank_branch_name, ifsc_code)
                    if (branch_id != 0):
                        Account_details['branch_name'] = branch_id
                    else:
                        final_execute = 0
                        error_mst = {"Message": 'Failed', "Employee_Code": emp_code,
                                     "Error_Description": "Branch branch name is not in MasterTable", "Error_Code": "4"}
                        fail_data_all.append(error_mst)


                acc_obj = AccountDetailsSynchRequest(Account_details)

                if (final_execute == 1):
                    resp_obj = employee_synch_service.create_data(emp_obj, add_obj, cont_obj,acc_obj, empid, emp_code, Entity,request)

                    single_out_put_data = resp_obj
                    if (single_out_put_data.get('Message') == "Success"):
                        success_count += 1
                    else:
                        fail_data_all.append(single_out_put_data)
                        fail_count += 1
                else:
                    fail_count += 1
            if (success_count == All_Data_len):
                single_out_msg = json.dumps([{"Message": "Success", "Error_Code": str(0)}])
                response = HttpResponse(single_out_msg, content_type="application/json")
            else:
                fail_data_all = json.dumps(fail_data_all)
                response = HttpResponse(fail_data_all, content_type="application/json")
        else:
            pass
        return response

    # if emp_obj.branch_code == None or emp_obj.branch_code == " ":
    #     final_execute = 0
    #     error_mst = {"Message": 'Failed', "Employee_Code": emp_code,
    #                  "Error_Description": "Missing the branch_code", "Error_Code": "4"}
    #     fail_data_all.append(error_mst)

    # check_special_char=(emp_obj.phone_no.isdecimal())
    # if(check_special_char==False):
    #     final_execute = 0
    #     error_mst = {"Message": 'Failed', "Employee_Code": emp_code,
    #                  "Error_Description": "Invalid phone_no", "Error_Code": "4"}
    #     fail_data_all.append(error_mst)

    # if emp_obj.phone_no == None or emp_obj.phone_no == " " or len(emp_obj.code) == 0:
    #     final_execute=0
    #     error_mst = {"Message": 'Failed', "Employee_Code": emp_code,
    #                  "Error_Description": "Missing the phone_no", "Error_Code": "4"}
    #     fail_data_all.append(error_mst)

    # if emp_obj.employee_type == None or emp_obj.employee_type == " " or len(emp_obj.employee_type) == 0:
    #     final_execute=0
    #     error_mst = {"Message": 'Failed', "Employee_Code": emp_code,
    #                  "Error_Description": "Missing the employee_type",
    #                  "Error_Code": "4"}
    #     fail_data_all.append(error_mst)

    # if emp_obj.branch == None or emp_obj.branch == " " or emp_obj.branch == 0:
    #     final_execute = 0
    #     error_mst = {"Message": 'Failed', "Employee_Code": emp_code,
    #                  "Error_Description": "Missing the branch", "Error_Code": "4"}
    #     fail_data_all.append(error_mst)

    # if emp_obj.businesssegment == None or emp_obj.businesssegment == " " or len(
    #         emp_obj.businesssegment) == 0:
    #     final_execute=0
    #     error_mst = {"Message": 'Failed', "Employee_Code": emp_code,
    #                  "Error_Description": "Missing the Businesssegment",
    #                  "Error_Code": "4"}
    #     fail_data_all.append(error_mst)

    # if emp_obj.costcentre == None or emp_obj.costcentre == " " or len(emp_obj.costcentre) == 0:
    #     final_execute=0
    #     error_mst = {"Message": 'Failed', "Employee_Code": emp_code,
    #                  "Error_Description": "Missing the Costcentre", "Error_Code": "4"}
    #     fail_data_all.append(error_mst)

    # if emp_obj.supervisor == None or emp_obj.supervisor == " " or len(
    #         emp_obj.supervisor) == 0 or regex.search(emp_obj.supervisor):
    #     final_execute=0
    #     error_mst = {"Message": 'Failed', "Employee_Code": emp_code,
    #                  "Error_Description": "Missing the Supervisor", "Error_Code": "4"}
    #     fail_data_all.append(error_mst)

    # if emp_obj.designation == None or emp_obj.designation == " " or len(
    #         emp_obj.designation) == 0 or regex.search(emp_obj.designation):
    #     final_execute = 0
    #     error_mst = {"Message": 'Failed', "Employee_Code": emp_code,
    #                  "Error Description": "Enter the Designation", "Error_Code": "4"}
    #     fail_data_all.append(error_mst)

    # if emp_obj.hierarchy == None or emp_obj.hierarchy == "" or len(emp_obj.hierarchy) == 0 or regex.search(
    #         emp_obj.hierarchy):
    #     final_execute=0
    #     error_mst = {"Message": 'Failed', "Employee_Code": emp_code,
    #                  "Error_Description": "Missing the hierarchy", "Error_Code": "4"}
    #     fail_data_all.append(error_mst)