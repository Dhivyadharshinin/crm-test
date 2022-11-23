import json
from taservice.data.response.tourallowance import GradeEligibiltyresponse
from taservice.models import TourReason, TourExpense, TourRequest, Gradeeligibility
# from userservice.models import Employee, EmployeeBranch
# from utilityservice.service.dbutil import DataBase

from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.ta_api_service import ApiService

from utilityservice.service.threadlocal import NWisefinThread
class emp_dtl(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.TA_SERVICE)
    # def employee_name_get(self,id):
    #     try:
    #         name = Employee.objects.using(self._current_app_schema()).get(id=id)
    #         return name.full_name
    #     except:
    #         pass
    #
    # def employee_code_get(self,id):
    #     try:
    #         emp = Employee.objects.using(self._current_app_schema()).get(id=id)
    #         return emp.code
    #     except:
    #         pass
    #
    # def employee_designation_get(self,id):
    #     try:
    #         emp = Employee.objects.using(self._current_app_schema()).get(id=id)
    #         return emp.designation
    #     except:
    #         pass

    # def employee_bracnh_get(self,id):
    #     try:
    #         name = Employee.objects.using(self._current_app_schema()).get(id=id)
    #         return name.employee_branch_id
    #     except:
    #         pass

    def get_reason_name(self,reason):
        try:
            tour_reason = TourReason.objects.using(self._current_app_schema()).get(id=reason,entity_id=self._entity_id())
            return tour_reason.name
        except:
            pass
    def is_file_required(self,reason):
        try:
            tour_reason = TourReason.objects.using(self._current_app_schema()).get(id=reason,entity_id=self._entity_id())
            return tour_reason.fileupload
        except:
            pass

    # def get_branch_name(self,branch_id):
    #     try:
    #         tour_branch_name = EmployeeBranch.objects.using(self._current_app_schema()).get(id=branch_id)
    #         return tour_branch_name.name
    #     except:
    #         pass
    # def get_branch_code(self,branch_id):
    #     try:
    #         tour_branch_code = EmployeeBranch.objects.using(self._current_app_schema()).get(id=branch_id)
    #         return tour_branch_code.code
    #     except:
    #         pass

class Expense_type_get(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.TA_SERVICE)

    def Expense_type(self,type):
        if type.lower()=="travel":
            return (TourExpense.objects.using(self._current_app_schema()).get(code="TRVL",entity_id=self._entity_id())).id
        elif type.lower()=="dailydeim":
            return (TourExpense.objects.using(self._current_app_schema()).get(code="DLYDM",entity_id=self._entity_id())).id
        elif type.lower()=="incidental":
            return (TourExpense.objects.using(self._current_app_schema()).get(code="INCDL",entity_id=self._entity_id())).id
        elif type.lower()=="localconv":
            return (TourExpense.objects.using(self._current_app_schema()).get(code="LCONV",entity_id=self._entity_id())).id
        elif type.lower()=="lodging":
            return (TourExpense.objects.using(self._current_app_schema()).get(code="LODG",entity_id=self._entity_id())).id
        elif type.lower()=="miscellaneous":
            return (TourExpense.objects.using(self._current_app_schema()).get(code="MISC",entity_id=self._entity_id())).id
        elif type.lower()=="packing_mov":
            return (TourExpense.objects.using(self._current_app_schema()).get(code="PCKG",entity_id=self._entity_id())).id

class Tourno_details(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.TA_SERVICE)
    def requestno_get(self,tourid,request):
        data= TourRequest.objects.using(self._current_app_schema()).get(id=tourid,entity_id=self._entity_id())
        grade_eligible=Gradeeligibility.objects.using(self._current_app_schema()).get(grade=data.empgrade,entity_id=self._entity_id())
        resp_list = GradeEligibiltyresponse()
        resp_list.set_employee_grade(grade_eligible.grade)
        resp_list.set_grade(grade_eligible.grade)
        resp_list.set_gradelevel(grade_eligible.gradelevel)
        resp_list.set_travelclass(grade_eligible.travelclass)
        resp_list.set_travelmode(grade_eligible.travelmode)
        resp_list.set_freight1000(grade_eligible.freight1000)
        resp_list.set_freight1001(grade_eligible.freight1001)
        resp_list.set_twowheller(grade_eligible.twowheller)
        resp_list.set_hillyregion(grade_eligible.hillyregion)
        resp_list.set_tonnagefamily(grade_eligible.tonnagefamily)
        resp_list.set_maxtonnage(grade_eligible.maxtonnage)
        emp_details = ApiService(self._scope())
        resp_list.set_employee_id(data.empgid)
        # resp_list.set_request_no(data.requestno)
        employee=emp_details.employee_details_get(data.empgid,request)
        resp_list.set_employee_name(employee.full_name)
        resp_list.set_employee_code(employee.code)
        return resp_list

    def emp_elig_travel(self,grade):
        grade_eligible=Gradeeligibility.objects.using(self._current_app_schema()).get(grade=grade,entity_id=self._entity_id())
        resp_list = GradeEligibiltyresponse()
        resp_list.set_employee_grade(grade_eligible.grade)
        resp_list.set_gradelevel(grade_eligible.gradelevel)
        resp_list.set_travelclass(grade_eligible.travelclass)
        resp_list.set_travelmode(grade_eligible.travelmode)
        resp_list.set_freight1000(grade_eligible.freight1000)
        resp_list.set_freight1001(grade_eligible.freight1001)
        resp_list.set_twowheller(grade_eligible.twowheller)
        resp_list.set_hillyregion(grade_eligible.hillyregion)
        resp_list.set_tonnagefamily(grade_eligible.tonnagefamily)
        resp_list.set_maxtonnage(grade_eligible.maxtonnage)
        return resp_list
        # emp_details=emp_dtl()
        # tour= {
        # "request_no":data.requestno,
        # "employee_id":data.empgid,
        # "employee_name":emp_details.employee_name_get(data.empgid),
        # "employee_code":emp_details.employee_code_get(data.empgid),
        # "employee_grade":data.empgrade
        # }
        # return json.dumps(tour)

    # def employee_grade_get(self,id):
    #     try:
    #         name = Employee.objects.using(self._current_app_schema()).get(id=id)
    #         return name.grade1
    #     except:
    #         pass

    def grade_get_tourid(self,tourid):
        tour=TourRequest.objects.using(self._current_app_schema()).get(id=tourid,entity_id=self._entity_id())
        return tour.empgrade
