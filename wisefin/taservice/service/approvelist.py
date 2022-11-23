
from taservice.data.request.approvinglist import Approverequest

from taservice.data.response.approvinglist import Approveresponse
from taservice.models.tamodels import ApproverList
# from taservice.service.emp_name_get import emp_dtl
from taservice.util.ta_util import App_type

from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinsuccess  import NWisefinSuccess, SuccessStatus, SuccessMessage
from django.db import IntegrityError
import json
from django.utils import timezone

from utilityservice.data.response.nwisefinlist  import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
# from utilityservice.service.dbutil import DataBase
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.ta_api_service import ApiService


class Approve_list(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.TA_SERVICE)
    def insert_approve(self,request_obj,user_id):

        for dtl in request_obj:
            request = Approverequest(dtl)
            allowance = ApproverList.objects.using(self._current_app_schema()).filter(employeeid=request.get_employeeid(),entity_id=self._entity_id())

            if len(allowance)!=0:
                try:
                    allowance = ApproverList.objects.using(self._current_app_schema()).filter(employeeid=request.get_employeeid(),entity_id=self._entity_id()).update(
                                                                                        branchid = request.get_branchid(),
                                                                                        tourapprove = request.get_tourapprove(),
                                                                                        advanceapprove = request.get_advanceapprove(),
                                                                                        expenseapprove = request.get_expenseapprove(),
                                                                                        updated_by = user_id,
                                                                                        status=1,
                                                                                        updated_date=timezone.now(),entity_id=self._entity_id())



                except Exception as e:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(str(e))
                    return error_obj
                # except IntegrityError as error:
                #     error_obj = NWisefinError()
                #     error_obj.set_code(ErrorMessage.INVALID_DATA)
                #     error_obj.set_description(ErrorDescription.INVALID_DATA)
                #     return error_obj
                # except ApproverList.DoesNotExist:
                #     error_obj = NWisefinError()
                #     error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
                #     error_obj.set_description(ErrorDescription.INVALID_REQUEST_ID)
                #     return error_obj
                # except:
                #     error_obj = NWisefinError()
                #     error_obj.set_code(ErrorMessage.INVALID_DATA)
                #     error_obj.set_description(ErrorDescription.INVALID_DATA)
                #     return error_obj


                # success_obj = NWisefinSuccess()
                # success_obj.set_status(SuccessStatus.SUCCESS)
                # success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
                # return success_obj
            else:
                try:
                    approve = ApproverList.objects.using(self._current_app_schema()).create( employeeid = request.get_employeeid(),
                                                             branchid=request.get_branchid(),
                                                             tourapprove=request.get_tourapprove(),
                                                             advanceapprove=request.get_advanceapprove(),
                                                             expenseapprove=request.get_expenseapprove(),
                                                             created_by = user_id,entity_id=self._entity_id())

                    # resp_list = Approveresponse()
                    # resp_list.set_branchid(approve.branchid)
                    # return resp_list



                # except IntegrityError as error:
                #     error_obj = NWisefinError()
                #     error_obj.set_code(ErrorMessage.INVALID_DATA)
                #     error_obj.set_description(ErrorDescription.INVALID_DATA)
                #     return error_obj
                except Exception as e:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(str(e))
                    return error_obj
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj

    def get_approve(self,request,approver,vys_page):
        approve = ApproverList.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).all()[vys_page.get_offset():vys_page.get_query_limit()]

        res_list=NWisefinList()
        for i in approve:
            resp_list = Approveresponse()
            resp_list.set_id(i.id)
            resp_list.set_employeeid(i.employeeid)
            empdtl = ApiService(self._scope())
            employee = empdtl.employee_details_get(i.employeeid, request)
            resp_list.set_employee_name(employee.full_name)
            # code = empdtl.employee_code_get(approve.employeeid)
            resp_list.set_employee_code(employee.code)
            resp_list.set_branchid(i.branchid)
            branch = empdtl.get_branch_data(i.branchid, request)
            resp_list.set_branch_name(branch.name)
            # brcode = empdtl.get_branch_code(approve.empbranchgid)
            resp_list.set_branch_code(branch.code)
            resp_list.set_tourapprove(i.tourapprove)
            resp_list.set_advanceapprove(i.advanceapprove)
            resp_list.set_expenseapprove(i.expenseapprove)
            if approver is None:
                res_list.append(json.loads(resp_list.get()))
            else:
                if employee.full_name or employee.code != None:
                    if approver.lower() in employee.full_name.lower() or approver.lower() in employee.code.lower():
                        res_list.append(json.loads(resp_list.get()))

            # res_list.append(json.loads(resp_list.get()))
            vpage = NWisefinPaginator(approve, vys_page.get_index(), 10)
            res_list.set_pagination(vpage)
        return res_list

    def delete_approve(self, delete_id):
        try:
            allowance = ApproverList.objects.using(self._current_app_schema()).get(id=delete_id,entity_id=self._entity_id()).delete()
        # except IntegrityError as error:
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.INVALID_DATA)
        #     error_obj.set_description(ErrorDescription.INVALID_DATA)
        #     return error_obj
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
        return success_obj

    def get_approve_byid(self,employee_id,request):
        approve = ApproverList.objects.using(self._current_app_schema()).get(id = employee_id,entity_id=self._entity_id())
        resp_list = Approveresponse()
        resp_list.set_id(approve.id)
        resp_list.set_employeeid(approve.employeeid)
        empdtl = ApiService(self._scope())
        employee = empdtl.employee_details_get(approve.employeeid, request)
        resp_list.set_employee_name(employee.full_name)
        # code = empdtl.employee_code_get(approve.employeeid)
        resp_list.set_employee_code(employee.code)
        resp_list.set_branchid(approve.branchid)
        branch = empdtl.get_branch_data(approve.branchid,request)
        resp_list.set_branch_name(branch.name)
        # brcode = empdtl.get_branch_code(approve.empbranchgid)
        resp_list.set_branch_code(branch.code)
        resp_list.set_tourapprove(approve.tourapprove)
        resp_list.set_advanceapprove(approve.advanceapprove)
        resp_list.set_expenseapprove(approve.expenseapprove)
        return resp_list

    # def approve_filterby_type(self,request_obj):
    #     try:
    #         if request_obj['type'].lower()==App_type.tour:
    #             approve = ApproverList.objects.using(self._current_app_schema()).get(branchid = request_obj['branchid'],tourapprove = 1)
    #             resp_list = Approveresponse()
    #             resp_list.set_id(approve.id)
    #             resp_list.set_employeeid(approve.employeeid)
    #             resp_list.set_branchid(approve.branchid)
    #             resp_list.set_tourapprove(approve.tourapprove)
    #             resp_list.set_advanceapprove(approve.advanceapprove)
    #             resp_list.set_expenseapprove(approve.expenseapprove)
    #             return resp_list
    #         if request_obj['type'].lower() ==App_type.advance:
    #             approve = ApproverList.objects.using(self._current_app_schema()).get(branchid = request_obj['branchid'],advanceapprove = 1)
    #             resp_list = Approveresponse()
    #             resp_list.set_id(approve.id)
    #             resp_list.set_employeeid(approve.employeeid)
    #             resp_list.set_branchid(approve.branchid)
    #             resp_list.set_tourapprove(approve.tourapprove)
    #             resp_list.set_advanceapprove(approve.advanceapprove)
    #             resp_list.set_expenseapprove(approve.expenseapprove)
    #             return resp_list
    #         if request_obj['type'].lower() ==App_type.expense:
    #             approve = ApproverList.objects.using(self._current_app_schema()).get(branchid = request_obj['branchid'],expenseapprove = 1)
    #             resp_list = Approveresponse()
    #             resp_list.set_id(approve.id)
    #             resp_list.set_employeeid(approve.employeeid)
    #             resp_list.set_branchid(approve.branchid)
    #             resp_list.set_tourapprove(approve.tourapprove)
    #             resp_list.set_advanceapprove(approve.advanceapprove)
    #             resp_list.set_expenseapprove(approve.expenseapprove)
    #             return resp_list
    #     # except IntegrityError as error:
    #     #     error_obj = NWisefinError()
    #     #     error_obj.set_code(ErrorMessage.INVALID_DATA)
    #     #     error_obj.set_description(ErrorDescription.INVALID_DATA)
    #     #     return error_obj
    #     except Exception as e:
    #         print(e)
    #         error_obj = NWisefinError()
    #         error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
    #         error_obj.set_description(str(e))
    #         return error_obj
    #
    #     success_obj = NWisefinSuccess()
    #     success_obj.set_status(SuccessStatus.SUCCESS)
    #     success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
    #     return success_obj

    def approve_filterby_type(self,request_obj,request):
        try:
            if request_obj['type'].lower()==App_type.tour:
                list = ApproverList.objects.using(self._current_app_schema()).filter(branchid = request_obj['branchid'],tourapprove = 1,entity_id=self._entity_id())
            elif request_obj['type'].lower() ==App_type.advance:
                list = ApproverList.objects.using(self._current_app_schema()).filter(branchid = request_obj['branchid'],advanceapprove = 1,entity_id=self._entity_id())
            elif request_obj['type'].lower() ==App_type.expense:
                list = ApproverList.objects.using(self._current_app_schema()).filter(branchid = request_obj['branchid'],expenseapprove = 1,entity_id=self._entity_id())
            arr=[]
            for approve in list:
                resp_list = Approveresponse()
                resp_list.set_id(approve.id)
                resp_list.set_employeeid(approve.employeeid)
                resp_list.set_branchid(approve.branchid)
                resp_list.set_tourapprove(approve.tourapprove)
                resp_list.set_advanceapprove(approve.advanceapprove)
                resp_list.set_expenseapprove(approve.expenseapprove)
                empdtl = ApiService(self._scope())
                employee = empdtl.employee_details_get(approve.employeeid,request)
                resp_list.set_employee_name(employee.full_name)
                # code = empdtl.employee_code_get(approve.employeeid)
                resp_list.set_employee_code(employee.code)
                branch = empdtl.get_branch_data(approve.branchid,request)
                resp_list.set_branch_name(branch.name)
                arr.append(resp_list)
            return arr
        except Exception as e:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description(str(e))
            return error_obj







