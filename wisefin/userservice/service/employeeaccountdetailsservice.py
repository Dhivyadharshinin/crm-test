import json
import traceback

from django.db import IntegrityError
from django.db.models import Q

from nwisefin.settings import logger
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpage import NWisefinPage
from masterservice.util.masterutil import ModifyStatus
# from vysfin.settings import logger
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.service.api_service import ApiService
from django.utils import timezone
from userservice.models import EmployeeAccountDetails,Employee, EmployeeEntityMapping
from masterservice.models import PayMode, Bank, BankBranch, BankDetails
from userservice.data.response.employeeaccountresponse import EmployeeAccountDetailsResponse,EmployeeAccountDetailsResponseSummary
from userservice.data.response.employeeresponse import EmployeeResponse
from masterservice.data.response.paymoderesponse import PaymodeResponse
from masterservice.data.response.bankresponse import BankResponse
from masterservice.data.response.bankbranchresponse import BankBranchResponse
# employee_account_details
class EmployeeAccountDetailsService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.USER_SERVICE)
    def create_employee_account_details(self, emp_obj, user_id):
        account_check = EmployeeAccountDetails.objects.using(self._current_app_schema()).filter(account_number=emp_obj.get_account_number())
        if len(account_check) > 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.DUPLICATE_BANK_NO)
            error_obj.set_description(ErrorDescription.DUPLICATE_BANK_NO)
            return error_obj
        if not emp_obj.get_id() is None:
            try:
                logger.error('EMPLOYEEACCOUNTDETAILS: EmployeeAccountDetails Update Started')
                employee_account_details = EmployeeAccountDetails.objects.using(self._current_app_schema()).filter(id=emp_obj.get_id()).update(
                                                                                 employee=emp_obj.get_employee(),
                                                                                 paymode=emp_obj.get_paymode(),
                                                                                 bank=emp_obj.get_bank(),
                                                                                 bankbranch=emp_obj.get_bankbranch(),
                                                                                account_number=emp_obj.get_account_number(),
                                                                                beneficiary_name=emp_obj.get_beneficiary_name(),
                                                                                 updated_by=user_id,
                                                                                 updated_date=timezone.now())
                employee_account_details = EmployeeAccountDetails.objects.using(self._current_app_schema()).get(id=emp_obj.get_id())
                employee_id = Employee.objects.using(self._current_app_schema()).get(id=emp_obj.get_employee())
                employee_id.accountnumber = emp_obj.get_account_number()
                employee_id.save()
                logger.error('EMPLOYEEACCOUNTDETAILS: EmployeeAccountDetails Update Success' + str(employee_account_details))
            except IntegrityError as error:
                logger.info('ERROR_EmployeeAccountDetails_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj

            except:
                logger.info('ERROR_EmployeeAccountDetails_Update_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        else:
            try:
                logger.error('EMPLOYEEACCOUNTDETAILS: EmployeeAccountDetails Creation Started')
                # employee_id=Employee.objects.using(self._current_app_schema()).get(id)
                employee_account_details = EmployeeAccountDetails.objects.using(self._current_app_schema()).create(
                                                                employee=emp_obj.get_employee(),
                                            # employee_id=Employee.objects.using(self._current_app_schema()).get(id.),
                                                                paymode=emp_obj.get_paymode(),
                                                                bank=emp_obj.get_bank(),
                                                                bankbranch=emp_obj.get_bankbranch(),
                                                                account_number=emp_obj.get_account_number(),
                                                                beneficiary_name=emp_obj.get_beneficiary_name(),
                                                                created_by=user_id)

                employee_id = Employee.objects.using(self._current_app_schema()).get(id=emp_obj.get_employee())
                employee_id.accountnumber=emp_obj.get_account_number()
                employee_id.save()
                logger.error('EMPLOYEEACCOUNTDETAILS: EmployeeAccountDetails Creation Success' + str(employee_account_details))
            except IntegrityError as error:
                logger.error('ERROR_EmployeeAccountDetails_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                return error_obj
            except:
                logger.error('ERROR_EmployeeAccountDetails_Create_EXCEPT:{}'.format(traceback.print_exc()))
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description(ErrorDescription.UNEXPECTED_ERROR)
                return error_obj
        data_obj = EmployeeAccountDetailsResponse()
        data_obj.set_id(employee_account_details.id)
        data_obj.set_employee(employee_account_details.employee)
        data_obj.set_paymode(employee_account_details.paymode)
        data_obj.set_bank(employee_account_details.bank)
        data_obj.set_bankbranch(employee_account_details.bankbranch)
        data_obj.set_account_number(employee_account_details.account_number)
        data_obj.set_beneficiary_name(employee_account_details.beneficiary_name)
        data_obj.set_status(employee_account_details.status)
        data = NWisefinSuccess()
        data.set_status(SuccessStatus.SUCCESS)
        data.set_message(SuccessMessage.CREATE_MESSAGE)
        return data
    def fetch_employee_account_summary(self,request,vys_page,emp_id):
        try:
            condition=Q()
            if "data" in request.GET:
                condition &= Q(employee=request.GET.get("data"))
            # if 'code' in request.GET:
            #     condition &= Q(employee__code__icontains=request.GET.get("code"))
            summary=EmployeeAccountDetails.objects.using(self._current_app_schema()).filter(condition)[
                                  vys_page.get_offset():vys_page.get_query_limit()]
            list_length = len(summary)
            summary_list = NWisefinList()
            if list_length <= 0:
                pass
            else:
                for employeeaccount in summary:
                    data_obj = EmployeeAccountDetailsResponseSummary()
                    data_obj.set_id(employeeaccount.id)
                    employeeid=employeeaccount.employee
                    # data_obj.set_employee(employeeaccount.employee)
                    try:
                        employee_details = Employee.objects.using(self._current_app_schema()).get(id=employeeid)
                        data_obj.set_employee_code(employee_details.code)
                        data_obj.set_employee_full_name(employee_details.full_name)
                    except:
                        data_obj.set_employee_code('')
                        data_obj.set_employee_full_name('')
                    # data_obj.set_employee_id(employee_details.id)

                    paymodeid=employeeaccount.paymode
                    api_serv = ApiService(self._scope())
                    paymode_details=api_serv.get_paymodesingle_id(request,paymodeid)
                    # paymode_details=PayMode.objects.using(self._current_app_schema()).get(id=paymodeid)
                    # data_obj.set_paymode_id(paymode_details.id)
                    data_obj.set_paymode_name(paymode_details['name'])
                    # data_obj.set_bank(employeeaccount.bank)
                    bankid=employeeaccount.bank
                    bank_details = api_serv.get_bank(bankid,emp_id)
                    data_obj.set_bank_name(bank_details.name)
                    bankbranchid=employeeaccount.bankbranch
                    Bankbranch_details = api_serv.get_bankbranch_single(request,bankbranchid,vys_page)
                    dta=json.loads(Bankbranch_details.get())
                    if(len(dta['data'])>0):
                        data_obj.set_bankbranch(dta['data'][0]['name'])
                    else:
                        data_obj.set_bankbranch("")
                    data_obj.set_account_number(employeeaccount.account_number)
                    data_obj.set_beneficiary_name(employeeaccount.beneficiary_name)
                    data_obj.set_status(employeeaccount.status)
                    summary_list.append(data_obj)
                vpage = NWisefinPaginator(summary, vys_page.get_index(), 10)
                summary_list.set_pagination(vpage)
                return summary_list
        except:
            logger.error('ERROR_EmployeeAccountDetails_Summary_EXCEPT:{}'.format(traceback.format_exc()))
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_EmployeeAccountDetails_ID)
            error_obj.set_description(ErrorDescription.INVALID_EmployeeAccountDetails_ID)
            return error_obj


    def employee_get(self,request,vys_page):
        condition = Q(entity_id=self._entity_id())
        if "data" in request.GET:
            condition &= Q(employee__full_name__icontains=request.GET.get("data"))|Q(employee__code__icontains=request.GET.get("data"))
        employee_data = EmployeeEntityMapping.objects.using(self._current_app_schema()).filter(condition).values('employee__id', 'employee__code', 'employee__full_name')[
                      vys_page.get_offset():vys_page.get_query_limit()]

        list_len = len(employee_data)
        employee_list = NWisefinList()
        if list_len <= 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_DATA)
            return error_obj
        else:
            for i in employee_data:
                response = EmployeeResponse()
                response.set_id(i['employee__id'])
                response.employee_code=i['employee__code']
                response.employee_full_name=i['employee__full_name']
                response.set_code(i['employee__code'])
                response.set_full_name(i['employee__full_name'])
                employee_list.append(response)
            vpage = NWisefinPaginator(employee_data, vys_page.get_index(), 10)
            employee_list.set_pagination(vpage)
            return employee_list
            # print(employee_list)
    def employee_paymode_get(self,request,vys_page):
        condition = Q()
        if "data" in request.GET:
            condition &= Q(name__icontains=request.GET.get("data"))
        paymode_data = PayMode.objects.using(self._current_app_schema()).filter(condition).values('id', 'code', 'name')[
                        vys_page.get_offset():vys_page.get_query_limit()]

        list_len = len(paymode_data)
        paymode_list = NWisefinList()
        if list_len <= 0:
            return paymode_list
        else:
            for i in paymode_data:
                response = PaymodeResponse()
                response.set_id(i['id'])
                response.set_code(i['code'])
                response.set_name(i['name'])
                paymode_list.append(response)
            vpage = NWisefinPaginator(paymode_data, vys_page.get_index(), 10)
            paymode_list.set_pagination(vpage)
            return paymode_list
    def employee_bank(self,request,vys_page):
        condition = Q()
        if "data" in request.GET:
            condition &= Q(name__icontains=request.GET.get("data"))
        bank_data = Bank.objects.using(self._current_app_schema()).filter(condition).values('id', 'code', 'name')[
                       vys_page.get_offset():vys_page.get_query_limit()]

        list_len = len(bank_data)
        bank_list = NWisefinList()
        if list_len <= 0:
            # error_obj = NWisefinError()
            # error_obj.set_code(ErrorMessage.INVALID_DATA)
            # error_obj.set_description(ErrorDescription.INVALID_DATA)
            return bank_list
        else:
            for i in bank_data:
                response = BankResponse()
                response.set_id(i['id'])
                response.set_code(i['code'])
                response.set_name(i['name'])
                bank_list.append(response)
            vpage = NWisefinPaginator(bank_data, vys_page.get_index(), 10)
            bank_list.set_pagination(vpage)
            return bank_list
    def employee_bankbranch(self,request,vys_page,bank_id):
        condition = Q(bank_id=bank_id)
        if "data" in request.GET:
            condition &= Q(name__icontains=request.GET.get("data"))
        bankbranch_data = BankBranch.objects.using(self._current_app_schema()).filter(condition).values('id', 'code', 'name','bank_id')[
                       vys_page.get_offset():vys_page.get_query_limit()]

        list_len = len(bankbranch_data)
        bankbranch_list = NWisefinList()
        if list_len < 0:
            vpage = NWisefinPaginator(bankbranch_data, vys_page.get_index(), 10)
            bankbranch_list.set_pagination(vpage)
        else:
            for i in bankbranch_data:
                response = BankBranchResponse()
                response.set_id(i['id'])
                response.set_code(i['code'])
                response.set_name(i['name'])
                response.set_bank_id(i['bank_id'])
                bankbranch_list.append(response)
            vpage = NWisefinPaginator(bankbranch_data, vys_page.get_index(), 10)
            bankbranch_list.set_pagination(vpage)
            return bankbranch_list

    def employeeaccount_active_inactivate(self, request, emp_obj, user_id):

        if (int(emp_obj.status) == 0):

            emp_data = EmployeeAccountDetails.objects.using(self._current_app_schema()).filter(id=emp_obj.id).update(
                status=1)
        else:
            emp_data = EmployeeAccountDetails.objects.using(self._current_app_schema()).filter(id=emp_obj.id).update(
                status=0)
        emp_var = EmployeeAccountDetails.objects.using(self._current_app_schema()).get(id=emp_obj.id)
        data = EmployeeAccountDetailsResponse()
        data.set_status(emp_var.status)
        status = emp_var.status
        data.set_id(emp_var.id)
        # return data
        if status == 1:
            data = NWisefinSuccess()
            data.set_status(SuccessStatus.SUCCESS)
            data.set_message(SuccessMessage.ACTIVATED)

            return data
        if status == 0:
            data = NWisefinSuccess()
            data.set_status(SuccessStatus.SUCCESS)
            data.set_message(SuccessMessage.INACTIVATED)
            return data
        else:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_taxrate_ID)
            error_obj.set_description(ErrorDescription.INVALID_taxrate_ID)
            return error_obj


    def fetch_emp_accntdtls_using_accntno(self,request,emp_accountno,emp_id):
        print('emp_accountno ',emp_accountno)
        print('emp_id ',emp_id)
        conditon=Q(entity_id=self._entity_id(),employee=emp_id)
        if emp_accountno != None:
            conditon&=Q(account_number=emp_accountno)
        empaccountdtls=EmployeeAccountDetails.objects.using(self._current_app_schema()).filter(conditon)
        data_obj = NWisefinList()
        if len(empaccountdtls) > 0 :
            empaccount_dtls=empaccountdtls[0]
            data_obj = EmployeeAccountDetailsResponseSummary()
            api_serv = ApiService(self._scope())
            data_obj.set_id(empaccount_dtls.id)
            employeeid=empaccount_dtls.employee
            paymodeid = empaccount_dtls.paymode
            bankid = empaccount_dtls.bank
            bank_details = api_serv.get_bank(bankid, emp_id)
            paymode_details = api_serv.get_paymodesingle_id(request, paymodeid)
            bankbranchid = empaccount_dtls.bankbranch
            Bankbranch_details = api_serv.get_single_bank_branch(bankbranchid,emp_id)
            Bankbranch_dta = json.loads(Bankbranch_details.get())
            employee_details = Employee.objects.using(self._current_app_schema()).get(id=employeeid)

            data_obj.set_employee_code(employee_details.code)
            data_obj.set_employee_full_name(employee_details.full_name)
            data_obj.set_paymode_name(paymode_details['name'])
            data_obj.set_bank_name(bank_details.name)
            data_obj.set_bankbranch(Bankbranch_dta)
            data_obj.set_account_number(empaccount_dtls.account_number)
            data_obj.set_beneficiary_name(empaccount_dtls.beneficiary_name)
            data_obj.set_status(empaccount_dtls.status)
        return data_obj



    def fetch_emp_accntdtls_using_emp_id(self,request,emp_id):
        print('emp_id ',emp_id)
        conditon=Q(entity_id=self._entity_id(),employee=emp_id)
        empaccountdtls=EmployeeAccountDetails.objects.using(self._current_app_schema()).filter(conditon)
        data_list = NWisefinList()
        if len(empaccountdtls) > 0 :
            empaccount_dtls=empaccountdtls[0]
            data_obj = EmployeeAccountDetailsResponseSummary()
            api_serv = ApiService(self._scope())
            data_obj.set_id(empaccount_dtls.id)
            employeeid=empaccount_dtls.employee
            paymodeid = empaccount_dtls.paymode
            bankid = empaccount_dtls.bank
            bank_details = api_serv.get_bank(bankid, emp_id)
            paymode_details = api_serv.get_paymodesingle_id(request, paymodeid)
            bankbranchid = empaccount_dtls.bankbranch
            Bankbranch_details = api_serv.get_single_bank_branch(bankbranchid,emp_id)
            Bankbranch_dta = json.loads(Bankbranch_details.get())
            employee_details = Employee.objects.using(self._current_app_schema()).get(id=employeeid)
            data_obj.set_employee_code(employee_details.code)
            data_obj.set_employee_full_name(employee_details.full_name)
            data_obj.set_paymode_name(paymode_details['name'])
            data_obj.set_bank_name(bank_details.name)
            data_obj.set_bankbranch(Bankbranch_dta)
            data_obj.set_account_number(empaccount_dtls.account_number)
            data_obj.set_beneficiary_name(empaccount_dtls.beneficiary_name)
            data_obj.set_status(empaccount_dtls.status)
            data_list.append(data_obj)
        return data_list


