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

    def create_salarylabel(self, payroll_reqobj, user_id):
        if payroll_reqobj.get_id() is None:
            salary_obj = SalaryLabel.objects.using(self._current_app_schema()).create(
                code=payroll_reqobj.get_code(),
                name=payroll_reqobj.get_name(),
                created_by=user_id,
                entity_id=self._entity_id())

        else:
            salary_obj = SalaryLabel.objects.using(self._current_app_schema()).filter(id=payroll_reqobj.get_id(),
                                                                                          entity_id=self._entity_id()) \
                .update(code=payroll_reqobj.get_subject(), name=payroll_reqobj.get_req_date(),
                        entity_id=self._entity_id(),
                        updated_by=user_id, updated_date=timezone.now())
            salary_obj = SalaryLabel.objects.using(self._current_app_schema()).get(id=payroll_reqobj.get_id(),entity_id=self._entity_id())
        resp = SalaryLabelResponse()
        resp.set_id(salary_obj.id)
        resp.set_code(salary_obj.code)
        resp.set_name(salary_obj.name)
        return resp

    def fetch_salarylabel(self, id):
        salary_obj = SalaryLabel.objects.using(self._current_app_schema()).get(id=id, entity_id=self._entity_id(),
                                                                                   status=1)
        resp = SalaryLabelResponse()
        resp.set_id(salary_obj.id)
        resp.set_code(salary_obj.code)
        resp.set_name(salary_obj.name)
        return resp

    def getall_salarylabel(self, vys_page):
        salary_obj = SalaryLabel.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                      status=1)[
                     vys_page.get_offset():vys_page.get_query_limit()]
        salary_obj_data = NWisefinList()
        for salary in salary_obj:
            resp = SalaryLabelResponse()
            resp.set_id(salary.id)
            resp.set_code(salary.code)
            resp.set_name(salary.name)
            salary_obj_data.append(resp)
            vpage = NWisefinPaginator(salary_obj, vys_page.get_index(), 10)
            salary_obj_data.set_pagination(vpage)
        return salary_obj_data

    def delete_salarylabel(self, id):
        salary_obj = SalaryLabel.objects.using(self._current_app_schema()).filter(id=id,
                                                                                      entity_id=self._entity_id(),
                                                                                      ).update(status=0)
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
        return success_obj