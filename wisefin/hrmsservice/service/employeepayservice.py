from attendanceservice.util.responsemessage import MessageResponse, StatusType
from hrmsservice.models import EmployeePay, EmployeeAdvanceRequest, EmployeeAdvanceApproval
from hrmsservice.data.response.employeepayresponse import EmployeePayResponse, EmployeeAdvanceRequestResponse,\
    EmployeeAdvanceApprovalResponse
from utilityservice.data.response.nwisefinerror import NWisefinError

from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinsuccess import SuccessMessage, NWisefinSuccess, SuccessStatus
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from django.db import IntegrityError





class EmployeePayService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.HRMS_SERVICE)
    def create_employeepay(self,pay_obj,user_id):
        update=0
        if pay_obj.get_id()is not None:
            update=1
            try:
                update_data=EmployeePay.objects.using(self._current_app_schema()).filter(
                       id= pay_obj.get_id(),entity_id=self._entity_id()).update(employee_id=pay_obj.get_employee_id(),
                                                                                 basic_pay=pay_obj.get_basic_pay(),
                                                                                 effective_from=pay_obj.get_effective_from(),
                                                                                 effective_to=pay_obj.get_effective_to(),
                                                                                 updated_by=user_id)
                update_data=EmployeePay.objects.using(self._current_app_schema()).get(
                       id= pay_obj.get_id(),entity_id=self._entity_id())
            except:
                error_obj = MessageResponse()
                error_obj.set_status(StatusType.FAILED)
                error_obj.set_message(ErrorDescription.INVALID_ID)
                return error_obj
        else:
            try:
                update_data=EmployeePay.objects.using(self._current_app_schema()).create(
                                                            entity_id=self._entity_id(),
                                                            employee_id=pay_obj.get_employee_id(),
                                                            basic_pay=pay_obj.get_basic_pay(),
                                                            effective_from=pay_obj.get_effective_from(),
                                                            effective_to=pay_obj.get_effective_to(),
                                                            created_by=user_id)
            except:
                error_obj = MessageResponse()
                error_obj.set_status(StatusType.FAILED)
                error_obj.set_message(ErrorDescription.INVALID_DATA)
                return error_obj
        success_obj = MessageResponse()
        success_obj.set_status(StatusType.SUCCESS)
        if update == 1:
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        else:
            success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj


    def summary_employeepay(self):
        try:
            emp=EmployeePay.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),status=1)
            emp_obj=NWisefinList()
            for i in emp:
                resp=EmployeePayResponse()
                resp.set_id(i.id)
                resp.set_employee_id(i.employee_id)
                resp.set_basic_pay(i.basic_pay)
                resp.set_effective_from(i.effective_from)
                resp.set_effective_to(i.effective_to)
                resp.set_created_by(i.created_by)
                emp_obj.append(resp)
            return emp_obj
        except:
            error_obj = MessageResponse()
            error_obj.set_status(StatusType.FAILED)
            error_obj.set_message(ErrorDescription.INVALID_DATA)
            return error_obj

    def fetch_employeepay(self,id):
        try:
            emp = EmployeePay.objects.using(self._current_app_schema()).get(id=id,entity_id=self._entity_id())
            resp = EmployeePayResponse()
            resp.set_id(emp.id)
            resp.set_employee_id(emp.employee_id)
            resp.set_basic_pay(emp.basic_pay)
            resp.set_effective_from(emp.effective_from)
            resp.set_effective_to(emp.effective_to)
            resp.set_created_by(emp.created_by)
            return resp
        except:
                error_obj = MessageResponse()
                error_obj.set_status(StatusType.FAILED)
                error_obj.set_message(ErrorDescription.INVALID_ID)
                return error_obj

    def del_employeepay(self,id):
        try:
            emp = EmployeePay.objects.using(self._current_app_schema()).filter(id=id,entity_id=self._entity_id()).delete()
            error_obj = MessageResponse()
            error_obj.set_status(StatusType.SUCCESS)
            error_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return error_obj
        except:
            error_obj =MessageResponse()
            error_obj.set_status(StatusType.FAILED)
            error_obj.set_message(ErrorDescription.INVALID_ID)
            return error_obj




class  EmployeeAdvanceRequestService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.HRMS_SERVICE)
    def create_employee_advancerequest(self,emp_obj,user_id):
        update=0
        if emp_obj.get_id() is not None:
            update=1
            try:
                update_data=EmployeeAdvanceRequest.objects.using(self._current_app_schema()).filter(
                       id= emp_obj.get_id(),entity_id=self._entity_id()).update(entity_id=self._entity_id(),
                                                                                employee_id=emp_obj.get_employee_id(),
                                                                                requested_advance_amount=emp_obj.get_requested_advance_amount(),
                                                                                approved_advance_amount=emp_obj.get_approved_advance_amount(),
                                                                                reason=emp_obj.get_reason(),
                                                                                updated_by=user_id)
                update_data=EmployeeAdvanceRequest.objects.using(self._current_app_schema()).get(
                       id= emp_obj.get_id(),entity_id=self._entity_id())
            except:
                error_obj = MessageResponse()
                error_obj.set_status(StatusType.FAILED)
                error_obj.set_message(ErrorDescription.INVALID_ID)
                return error_obj
        else:
            try:
                update_data = EmployeeAdvanceRequest.objects.using(self._current_app_schema()).create(
                                                                    entity_id=self._entity_id(),
                                                                    employee_id=emp_obj.get_employee_id(),
                                                                   requested_advance_amount=emp_obj.get_requested_advance_amount(),
                                                                   approved_advance_amount=emp_obj.get_approved_advance_amount(),
                                                                   reason=emp_obj.get_reason(),
                                                                   created_by=user_id)
            except :
                error_obj = MessageResponse()
                error_obj.set_status(StatusType.FAILED)
                error_obj.set_message(ErrorDescription.INVALID_DATA)
                return error_obj
        success_obj = MessageResponse()
        success_obj.set_status(StatusType.SUCCESS)
        if update == 1:
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        else:
            success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj

    def summary_employee_advancerequest(self):
        try:
            emp=EmployeeAdvanceRequest.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),status=1)
            emp_obj=NWisefinList()
            for i in emp:
                resp=EmployeeAdvanceRequestResponse()
                resp.set_id(i.id)
                resp.set_employee_id(i.employee_id)
                resp.set_requested_advance_amount(i.requested_advance_amount)
                resp.set_approved_advance_amount(i.approved_advance_amount)
                resp.set_reason(i.reason)
                resp.set_created_by(i.created_by)
                emp_obj.append(resp)
            return emp_obj
        except:
            error_obj = MessageResponse()
            error_obj.set_status(StatusType.FAILED)
            error_obj.set_message(ErrorDescription.INVALID_DATA)
            return error_obj

    def fetch_employee_advancerequest(self, id):
        try:
            emp = EmployeeAdvanceRequest.objects.using(self._current_app_schema()).get(id=id, entity_id=self._entity_id())
            resp = EmployeeAdvanceRequestResponse()
            resp.set_id(emp.id)
            resp.set_employee_id(emp.employee_id)
            resp.set_requested_advance_amount(emp.requested_advance_amount)
            resp.set_approved_advance_amount(emp.approved_advance_amount)
            resp.set_reason(emp.reason)
            resp.set_created_by(emp.created_by)
            return resp
        except:
            error_obj = MessageResponse()
            error_obj.set_status(StatusType.FAILED)
            error_obj.set_message(ErrorDescription.INVALID_ID)
            return error_obj


    def del_employee_advancerequest(self,id):
        try:
            emp = EmployeeAdvanceRequest.objects.using(self._current_app_schema()).filter(id=id,entity_id=self._entity_id()).delete()
            error_obj = MessageResponse()
            error_obj.set_status(StatusType.SUCCESS)
            error_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return error_obj
        except:
            error_obj = MessageResponse()
            error_obj.set_status(StatusType.FAILED)
            error_obj.set_message(ErrorDescription.INVALID_ID)
            return error_obj






class  EmployeeAdvanceApprovalService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.HRMS_SERVICE)
    def create_employee_advanceapproval(self,emp_obj,user_id):
        update=0
        if emp_obj.get_id() is not None:
            update=1
            try:
                update_data=EmployeeAdvanceApproval.objects.using(self._current_app_schema()).filter(
                       id= emp_obj.get_id(),entity_id=self._entity_id()).update(entity_id=self._entity_id(),
                                                                                employee_request_id=emp_obj.get_employee_request_id(),
                                                                                employee_id=emp_obj.get_employee_id(),
                                                                                remarks=emp_obj.get_remarks(),
                                                                                updated_by=user_id)
                update_data=EmployeeAdvanceApproval.objects.using(self._current_app_schema()).get(
                       id= emp_obj.get_id(),entity_id=self._entity_id())
            except:
                error_obj = MessageResponse()
                error_obj.set_status(StatusType.FAILED)
                error_obj.set_message(ErrorDescription.INVALID_ID)
                return error_obj
        else:
            try:
                update_data = EmployeeAdvanceApproval.objects.using(self._current_app_schema()).create(
                                                                    entity_id=self._entity_id(),
                                                                   employee_request_id=emp_obj.get_employee_request_id(),
                                                                   employee_id=emp_obj.get_employee_id(),
                                                                   remarks=emp_obj.get_remarks(),
                                                                   created_by=user_id)
            except :
                error_obj = MessageResponse()
                error_obj.set_status(StatusType.FAILED)
                error_obj.set_message(ErrorDescription.INVALID_DATA)
                return error_obj
        success_obj = MessageResponse()
        success_obj.set_status(StatusType.SUCCESS)
        if update == 1:
            success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        else:
            success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj



    def summary_employee_advanceapproval(self):
        try:
            emp_get=EmployeeAdvanceApproval.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),status=1)
            getover_data = NWisefinList()
            for i in emp_get :
                emp_resp=EmployeeAdvanceApprovalResponse()
                # mapping_resp.set_grade_id(i.grade_id)
                emp_resp.set_id(i.id)
                emp_resp.set_status(i.status)
                emp_resp.set_created_by(i.created_by)
                serv = EmployeeAdvanceRequestService(self._scope())
                emp_details = serv.fetch_employee_advancerequest(i.employee_request_id)
                emp_resp.set_employee_request_id(emp_details)
                getover_data.append(emp_resp)
            return getover_data
        except:
            error_obj=MessageResponse()
            error_obj.set_status(StatusType.FAILED)
            error_obj.set_message(ErrorDescription.INVALID_DATA)
            return error_obj

    def fetch_employee_advanceapproval(self,id):
        try:
            emp=EmployeeAdvanceApproval.objects.using(self._current_app_schema()).get(id=id,entity_id=self._entity_id())
            emp_resp=EmployeeAdvanceApprovalResponse()
            # mapping_resp.set_grade_id(i.grade_id)
            emp_resp.set_id(emp.id)
            emp_resp.set_status(emp.status)
            emp_resp.set_created_by(emp.created_by)
            serv = EmployeeAdvanceRequestService(self._scope())
            emp_details = serv.fetch_employee_advancerequest(emp.employee_request_id)
            emp_resp.set_employee_request_id(emp_details)
            return emp_resp
        except:
            error_obj = MessageResponse()
            error_obj.set_status(StatusType.FAILED)
            error_obj.set_message(ErrorDescription.INVALID_ID)
            return error_obj

    def del_employee_advanceapproval(self,id):
        try:
            del_emp=EmployeeAdvanceApproval.objects.using(self._current_app_schema()).filter(id=id).delete()
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj
        except:
            error_obj = MessageResponse()
            error_obj.set_status(StatusType.FAILED)
            error_obj.set_message(ErrorDescription.INVALID_ID)
            return error_obj





















