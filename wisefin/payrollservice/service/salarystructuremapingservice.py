from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from payrollservice.data.response.payrollcomponentresponse import SalaryLabelResponse, SalaryComponentResponse, \
    SalarystructureMappingResponse, DetectionInfoResponse
from payrollservice.models.payrollmodels import SalaryLabel, SalaryComponent, SalarystructureMapping
from django.utils import timezone
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessMessage, SuccessStatus
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator


class PayrollService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MEMO_SERVICE)

    def create_salarystructuremapping(self, payroll_reqobj, user_id):
        if payroll_reqobj.get_id() is None:
            salary_obj = SalarystructureMapping.objects.using(self._current_app_schema()).create(
                name=payroll_reqobj.get_name(),
                salarycomponent_id=payroll_reqobj.get_salarycomponent(),
                salarylabel_id=payroll_reqobj.get_salarylabel(),
                is_amount=payroll_reqobj.get_is_amount(),
                amount_value=payroll_reqobj.get_amount_value(),
                type=payroll_reqobj.get_type(),
                created_by=user_id,
                entity_id=self._entity_id())

        else:
            salary_obj = SalarystructureMapping.objects.using(self._current_app_schema()).filter(id=payroll_reqobj.get_id(),
                                                                                          entity_id=self._entity_id()) \
                .update(name=payroll_reqobj.get_name(),
                        salarycomponent_id=payroll_reqobj.get_salarycomponent(),
                        salarylabel_id=payroll_reqobj.get_salarylabel(),
                        is_amount=payroll_reqobj.get_is_amount(),
                        amount_value=payroll_reqobj.get_amount_value(),
                        type=payroll_reqobj.get_type(),
                        entity_id=self._entity_id(),
                        updated_by=user_id, updated_date=timezone.now())
            salary_obj = SalarystructureMapping.objects.using(self._current_app_schema()).get(id=payroll_reqobj.get_id(),entity_id=self._entity_id())
        resp = SalarystructureMappingResponse()
        resp.set_id(salary_obj.id)
        resp.set_name(salary_obj.name)
        resp.set_salarycomponent(salary_obj.salarycomponent_id)
        resp.set_salarylabel(salary_obj.salarylabel_id)
        resp.set_is_amount(salary_obj.is_amount)
        resp.set_amount_value(salary_obj.amount_value)
        resp.set_type(salary_obj.type)
        return resp

    def fetch_salarymapping(self, id):
        salary_obj = SalarystructureMapping.objects.using(self._current_app_schema()).get(id=id, entity_id=self._entity_id(),
                                                                                   status=1)
        resp = SalarystructureMappingResponse()
        resp.set_id(salary_obj.id)
        resp.set_name(salary_obj.name)
        resp.set_salarycomponent(salary_obj.salarycomponent_id)
        resp.set_salarylabel(salary_obj.salarylabel_id)
        resp.set_is_amount(salary_obj.is_amount)
        resp.set_amount_value(salary_obj.amount_value)
        resp.set_type(salary_obj.type)
        return resp

    def getall_salarystructuremapping(self, vys_page):
        salary_obj = SalarystructureMapping.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                      status=1)[
                     vys_page.get_offset():vys_page.get_query_limit()]
        salary_obj_data = NWisefinList()
        for salary in salary_obj:
            resp = SalarystructureMappingResponse()
            resp.set_id(salary.id)
            resp.set_name(salary.name)
            resp.set_salarycomponent(salary.salarycomponent_id)
            resp.set_salarylabel(salary.salarylabel_id)
            resp.set_is_amount(salary.is_amount)
            resp.set_amount_value(salary.amount_value)
            resp.set_type(salary.type)
            salary_obj_data.append(resp)
            vpage = NWisefinPaginator(salary_obj, vys_page.get_index(), 10)
            salary_obj_data.set_pagination(vpage)
        return salary_obj_data

    def delete_salarymapping(self, id):
        salary_obj = SalarystructureMapping.objects.using(self._current_app_schema()).filter(id=id,
                                                                                      entity_id=self._entity_id(),
                                                                                      ).update(status=0)
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
        return success_obj