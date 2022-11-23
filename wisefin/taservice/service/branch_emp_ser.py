import re
from taservice.data.response.branch_emp_resp import Branch_emp_resp
from taservice.models import ApproverList, TravelHistory
# from taservice.service.emp_name_get import emp_dtl
from taservice.util.ta_util import App_type
# from userservice.models import Employee
# from utilityservice.service.dbutil import DataBase
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.ta_api_service import ApiService
# test

class Branch_emp_ser(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.TA_SERVICE)
    # def branch_employee_get(self, branch,search):
    #     employee = Employee.objects.filter(employee_branch_id=branch)
    #     arr = []
    #     for emp in employee:
    #         report_res = Branch_emp_resp()
    #         report_res.set_full_name(emp.full_name)
    #         # report_res.set_first_name(emp.first_name)
    #         # report_res.set_middle_name(emp.middle_name)
    #         report_res.set_id(emp.id)
    #         report_res.set_designation(emp.designation)
    #         report_res.set_code(emp.code)
    #         if search is None:
    #             arr.append(report_res)
    #         else:
    #             if search in emp.full_name:
    #                 arr.append(report_res)
    #     return arr

    def branch_approver_get(self, type,branch,approver,approver_except,request,tourid):
        if type==App_type.tour:
            previous_approver=TravelHistory.objects.using(self._current_app_schema()).filter(tour_id=tourid, request_type=App_type.TOUR, applevel=0, entity_id=self._entity_id())
            if len(previous_approver) !=0:
                approver_except.append(previous_approver[0].approvedby)
                # if previous_approver[0].onbehalfof !=0:
                #     approver_except.append(previous_approver[0].onbehalfof)

            previous_approver_list2=TravelHistory.objects.using(self._current_app_schema()).filter(tour_id=tourid, request_type=App_type.TOUR, status=6, entity_id=self._entity_id())
            for app in previous_approver_list2:
                approver_except.append(app.approvedby)
            emp_ser = ApiService(self._scope())
            arr,emp_id_arr=emp_ser.role_bh_emp_get( branch, approver, approver_except, request)

            # employee = Employee.objects.using(self._current_app_schema()).filter(employee_branch_id=branch, role="BH")
            # arr = []
            # emp_id_arr = []
            # filter_grade_list = ["S3", "S4", "S5", "S6", "S7", "L3", "L4", "L5", "L6"]
            # for emp in employee:
            #     report_res = Branch_emp_resp()
            #     report_res.set_id(emp.id)
            #     report_res.set_employee_name(emp.full_name)
            #     report_res.set_employee_designation(emp.designation)
            #     report_res.set_employee_code(emp.code)
            #     report_res.set_employeeid(emp.id)
            #     report_res.set_branchid(emp.employee_branch_id)
            #     if emp.grade1 in filter_grade_list:
            #         if approver is None:
            #             if maker != emp.id:
            #                 arr.append(report_res)
            #                 emp_id_arr.append(emp.id)
            #         elif approver in emp.full_name:
            #             if maker != emp.id:
            #                 arr.append(report_res)
            #                 emp_id_arr.append(emp.id)

            employee = ApproverList.objects.using(self._current_app_schema()).filter(tourapprove=1,branchid=branch,status=1,entity_id=self._entity_id())
            # arr = []
            for emp in employee:
                report_res = Branch_emp_resp()
                # report_res.set_header_id(emp.id)
                empdtl = ApiService(self._scope())
                employee = empdtl.employee_details_get(emp.employeeid,request)
                report_res.set_full_name(employee.full_name)
                # designation = empdtl.employee_designation_get(emp.employeeid)
                report_res.set_designation(employee.designation)
                # code = empdtl.employee_code_get(emp.employeeid)
                report_res.set_code(employee.code)
                report_res.set_id(emp.employeeid)
                report_res.set_employee_branch_id(emp.branchid)
                # report_res.set_tourapprove(emp.tourapprove)
                # report_res.set_advanceapprove(emp.advanceapprove)
                # report_res.set_expenseapprove(emp.expenseapprove)
                # report_res.set_status(emp.status)
                if approver is None:
                    if emp.employeeid not in approver_except:
                        if emp.employeeid not in emp_id_arr:
                            arr.append(report_res)
                else:
                    if employee.full_name is not None and employee.code is not None:
                        if approver in employee.full_name.lower() or approver in employee.code.lower():
                            if emp.employeeid not in approver_except:
                                if emp.employeeid not in emp_id_arr:
                                    arr.append(report_res)
                # else:
                #     if approver in employee.full_name == None or  approver in employee.code ==None:
                #         arr.append(report_res)
                #     else:
                #         if approver in employee.full_name.lower() or approver in employee.code.lower():
                #             if emp.employeeid not in approver_except:
                #                 if emp.employeeid not in emp_id_arr:
                #                     arr.append(report_res)
            return arr

        elif type==App_type.advance:
            emp_ser = ApiService(self._scope())
            arr, emp_id_arr = emp_ser.role_bh_emp_get( branch, approver, approver_except, request)
            # # employee = ApproverList.objects.using(self._current_app_schema()).filter(advanceapprove=1,branchid=branch)
            # employee = Employee.objects.using(self._current_app_schema()).filter(employee_branch_id=branch,role="BH")
            # arr=[]
            # emp_id_arr=[]
            # filter_grade_list=["S3","S4","S5","S6","S7","L3","L4","L5","L6"]
            # for emp in employee:
            #     report_res = Branch_emp_resp()
            #     report_res.set_id(emp.id)
            #     report_res.set_employee_name(emp.full_name)
            #     report_res.set_employee_designation(emp.designation)
            #     report_res.set_employee_code(emp.code)
            #     report_res.set_employeeid(emp.id)
            #     report_res.set_branchid(emp.employee_branch_id)
            #     if emp.grade1 in filter_grade_list:
            #         if approver is None:
            #             if maker != emp.id:
            #                 arr.append(report_res)
            #                 emp_id_arr.append(emp.id)
            #         elif approver in emp.full_name:
            #             if maker != emp.id:
            #                 arr.append(report_res)
            #                 emp_id_arr.append(emp.id)
            employee=ApproverList.objects.using(self._current_app_schema()).filter(advanceapprove=1, branchid=branch,status=1,entity_id=self._entity_id())
            # arr = []
            for emp in employee:
                report_res = Branch_emp_resp()
                # report_res.set_id(emp.id)
                empdtl = ApiService(self._scope())
                employee = empdtl.employee_details_get(emp.employeeid,request)
                report_res.set_full_name(employee.full_name)
                # designation = empdtl.employee_designation_get(emp.employeeid)
                report_res.set_designation(employee.designation)
                # code = empdtl.employee_code_get(emp.employeeid)
                report_res.set_code(employee.code)
                report_res.set_id(emp.employeeid)
                report_res.set_employee_branch_id(emp.branchid)
                # report_res.set_tourapprove(emp.tourapprove)
                # report_res.set_advanceapprove(emp.advanceapprove)
                # report_res.set_expenseapprove(emp.expenseapprove)
                # report_res.set_status(emp.status)
                if approver is None:
                    if emp.employeeid not in approver_except:
                        if emp.employeeid not in emp_id_arr:
                            arr.append(report_res)
                else:
                    if employee.full_name is not None and employee.code is not None:
                        if approver in employee.full_name.lower() or approver in employee.code.lower():
                            if emp.employeeid not in approver_except:
                                if emp.employeeid not in emp_id_arr:
                                    arr.append(report_res)

            return arr

        elif type==App_type.expense:
            previous_approver = TravelHistory.objects.using(self._current_app_schema()).filter(tour_id=tourid,
                                                                                               request_type=App_type.CLAIM, applevel=0, entity_id=self._entity_id())
            if len(previous_approver)!=0:
                previous_approver=previous_approver[0]
                approver_except.append(previous_approver.approvedby)
                # if previous_approver.onbehalfof != 0:
                #     approver_except.append(previous_approver.onbehalfof)

            # previous_approver_list2 = ApprovedBy.objects.using(self._current_app_schema()).filter(tour_id=tourid,
            #                                                                           apptype=App_type.CLAIM, status=6)
            # for app in previous_approver_list2:
            #     approver_except.append(app.approvedby)
                
            employee = ApproverList.objects.using(self._current_app_schema()).filter(expenseapprove=1,branchid=branch,status=1,entity_id=self._entity_id())
            arr = []
            for emp in employee:
                report_res = Branch_emp_resp()
                report_res.set_id(emp.id)
                empdtl = ApiService(self._scope())
                employee = empdtl.employee_details_get(emp.employeeid, request)

                report_res.set_full_name(employee.full_name)
                # designation = empdtl.employee_designation_get(emp.employeeid)
                report_res.set_designation(employee.designation)
                # code = empdtl.employee_code_get(emp.employeeid)
                report_res.set_code(employee.code)
                report_res.set_id(emp.employeeid)
                report_res.set_employee_branch_id(emp.branchid)
                # report_res.set_tourapprove(emp.tourapprove)
                # report_res.set_advanceapprove(emp.advanceapprove)
                # report_res.set_expenseapprove(emp.expenseapprove)
                # report_res.set_status(emp.status)
                if approver is None:
                    if emp.employeeid not in approver_except:
                        arr.append(report_res)
                else:
                    if employee.full_name is not None and employee.code is not None:
                        if approver in employee.full_name.lower() or approver in employee.code.lower():
                            if  emp.employeeid not in approver_except:
                                arr.append(report_res)
            return arr
