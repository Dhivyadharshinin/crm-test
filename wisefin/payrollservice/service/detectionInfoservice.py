from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from payrollservice.data.response.payrollcomponentresponse import SalaryLabelResponse, SalaryComponentResponse, \
    SalarystructureMappingResponse, DetectionInfoResponse
from payrollservice.models.payrollmodels import SalaryLabel, SalaryComponent, SalarystructureMapping,DetectionInfo
from django.utils import timezone
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessMessage, SuccessStatus
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator


class PayrollService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MEMO_SERVICE)

    def create_detectioninfo(self, payroll_reqobj, user_id):
        if payroll_reqobj.get_id() is None:
            salary_obj = DetectionInfo.objects.using(self._current_app_schema()).create(
                salarymapping_id=payroll_reqobj.get_salarymapping(),
                from_month=payroll_reqobj.get_from_month(),
                created_by=user_id,
                entity_id=self._entity_id())

        else:
            salary_obj = DetectionInfo.objects.using(self._current_app_schema()).filter(id=payroll_reqobj.get_id(),
                                                                                          entity_id=self._entity_id()) \
                .update(salarymapping_id=payroll_reqobj.get_salarymapping(),
                        from_month=payroll_reqobj.get_from_month(),
                        entity_id=self._entity_id(),
                        updated_by=user_id, updated_date=timezone.now())
            salary_obj = DetectionInfo.objects.using(self._current_app_schema()).get(id=payroll_reqobj.get_id(),entity_id=self._entity_id())
        resp = DetectionInfoResponse()
        resp.set_id(salary_obj.id)
        resp.set_salarymapping(salary_obj.salarymapping.id)
        resp.set_from_month(salary_obj.from_month)
        return resp

    def fetch_detectioninfo(self, id):
        salary_obj = DetectionInfo.objects.using(self._current_app_schema()).get(id=id, entity_id=self._entity_id(),
                                                                                   status=1)
        resp = DetectionInfoResponse()
        resp.set_id(salary_obj.id)
        resp.set_salarymapping(salary_obj.salarymapping.id)
        resp.set_from_month(salary_obj.from_month)
        return resp

    def getall_detectioninfo(self, vys_page):
        salary_obj = DetectionInfo.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),
                                                                                      status=1)[
                     vys_page.get_offset():vys_page.get_query_limit()]
        salary_obj_data = NWisefinList()
        for salary in salary_obj:
            resp = DetectionInfoResponse()
            resp.set_id(salary.id)
            resp.set_salarymapping(salary.salarymapping.id)
            resp.set_from_month(salary.from_month)
            salary_obj_data.append(resp)
            vpage = NWisefinPaginator(salary_obj, vys_page.get_index(), 10)
            salary_obj_data.set_pagination(vpage)
        return salary_obj_data

    def delete_detectionInfo(self, id):
        salary_obj = DetectionInfo.objects.using(self._current_app_schema()).filter(id=id,
                                                                                      entity_id=self._entity_id(),
                                                                                      ).update(status=0)
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
        return success_obj