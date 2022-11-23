from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from hrmsservice.models import EmployeeEducationDetails,EmployeeExperiences
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess,SuccessMessage
from hrmsservice.data.response.employeeeducationdetailsresponse import EmployeeEducationDetailResponse,EmployeeExperiencesResponse
from hrmsservice.util.hrmsutil import ActiveStatus
from utilityservice.data.response.nwisefinlist import NWisefinList
class EmployeeEducationInfoService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.HRMS_SERVICE)

    def create_employeeeducationinfo(self,data_obj):
        resp = NWisefinSuccess()
        create_arr = data_obj['create_arr']
        update_arr = data_obj['update_arr']
        if len(update_arr) > 0:
            for data in update_arr:
                EmployeeEducationDetails.objects.using(self._current_app_schema()).filter(id=data['id']).update(**data)
                resp.set_message(SuccessMessage.UPDATE_MESSAGE)
        if len(create_arr) > 0:
            emplist = [EmployeeEducationDetails(**data) for data in create_arr]
            EmployeeEducationDetails.objects.using(self._current_app_schema()).bulk_create(emplist)
            resp.set_message(SuccessMessage.CREATE_MESSAGE)
        return resp


    def get_employeeeducationinfo(self, employee_id):
        obj = EmployeeEducationDetails.objects.using(self._current_app_schema()).filter(employee_id=employee_id,status=ActiveStatus.Active)
        empedu=NWisefinList()
        for i in obj:
            data_resp = EmployeeEducationDetailResponse()
            data_resp.set_id(i.id)
            data_resp.set_inst_name(i.inst_name)
            data_resp.set_passing_year(i.passing_year)
            data_resp.set_passing_month(i.passing_month)
            data_resp.set_percentage(i.percentage)
            data_resp.set_city(i.city)
            data_resp.set_title(i.title)
            data_resp.set_stream(i.stream)
            empedu.append(data_resp)
        return empedu


    def create_employeeexperiences(self,data_obj):
        resp = NWisefinSuccess()
        create_arr = data_obj['create_arr']
        update_arr = data_obj['update_arr']
        if len(update_arr) > 0:
            for data in update_arr:
                EmployeeExperiences.objects.using(self._current_app_schema()).filter(id=data['id']).update(**data)
                resp.set_message(SuccessMessage.UPDATE_MESSAGE)
        if len(create_arr) > 0:
            emplist = [EmployeeExperiences(**data) for data in create_arr]
            EmployeeExperiences.objects.using(self._current_app_schema()).bulk_create(emplist)
            resp.set_message(SuccessMessage.CREATE_MESSAGE)
        return resp


    def get_employeeexperiences(self, employee_id):
        employeeex = EmployeeExperiences.objects.using(self._current_app_schema()).filter(employee_id=employee_id,status=ActiveStatus.Active)
        empexperience=NWisefinList()
        for i in employeeex:
            data_resp = EmployeeExperiencesResponse()
            data_resp.set_id(i.id)
            data_resp.set_company(i.company)
            data_resp.set_work_experience(i.work_experience)
            data_resp.set_doj(i.doj)
            data_resp.set_dor(i.dor)
            data_resp.set_role(i.role)
            data_resp.set_city(i.city)
            empexperience.append(data_resp)
        return empexperience