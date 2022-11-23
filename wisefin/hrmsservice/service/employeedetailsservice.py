from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from hrmsservice.models import EmployeeDetails,EmployeeFamilyInfo,EmployeeEmergencyContact,EmployeeShiftMapping
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess,SuccessMessage,SuccessStatus
from hrmsservice.data.response.employeedetailsresponse import EmployeeDetialsResponse,EmployeeFamilyInfoResponse,EmpEmergencyContactResponse,EmpShiftMappingResponse
from hrmsservice.util.hrmsutil import ActiveStatus
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from hrmsservice.service.hrmscommonservice import HrmsCommonService
from hrmsservice.data.request.employeedetailsrequest import HrmsAddressRequest
from django.db.models import Q
from utilityservice.service.attendanceapiservice import AttendanceAPIService
from hrmsservice.service.payrollservice import WorkShiftService
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
class EmployeeDetailsService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.HRMS_SERVICE)

    def create_employeedetails(self, emp_obj, user_id,employeeid):
        if not emp_obj.get_id() is None:
            emp_details =EmployeeDetails.objects.using(self._current_app_schema()).filter(id=emp_obj.get_id()).update(
                                                    employee_id=employeeid,
                                                    nationality=emp_obj.get_nationality(),
                                                    marital_status = emp_obj.get_marital_status(),
                                                    height = emp_obj.get_height(),
                                                    weight = emp_obj.get_weight(),
                                                    blood_grp = emp_obj.get_blood_grp(),
                                                    updated_by=user_id)
            success_obj = NWisefinSuccess()
            success_obj.set_status("Success")
            success_obj.set_message("Updated Successfully")
            return success_obj

        else:
            emp_details1 = EmployeeDetails.objects.using(self._current_app_schema()).create(
                                                                        employee_id=employeeid,
                                                                        nationality=emp_obj.get_nationality(),
                                                                        marital_status=emp_obj.get_marital_status(),
                                                                        height=emp_obj.get_height(),
                                                                        weight=emp_obj.get_weight(),
                                                                        blood_grp=emp_obj.get_blood_grp(),
                                                                        created_by=user_id)
            empdetails_data = EmployeeDetialsResponse()
            empdetails_data.set_nationality(emp_details1.nationality)
            return empdetails_data

    def get_employeedetails(self,employeeid):
        try:
            employee_details = EmployeeDetails.objects.using(self._current_app_schema()).get(id=employeeid)
            empdetail_data = EmployeeDetialsResponse()
            empdetail_data.set_id(employee_details.id)
            empdetail_data.set_nationality(employee_details.nationality)
            empdetail_data.set_marital_status(employee_details.marital_status)
            empdetail_data.set_height(employee_details.height)
            empdetail_data.set_weight(employee_details.weight)
            empdetail_data.set_blood_grp(employee_details.blood_grp)
            return empdetail_data
        except:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.NULL_DATA)
            error_obj.set_description(ErrorDescription.NULL_DATA)
            return error_obj


    def create_employeefamilyinfo(self,data_obj):
        resp = NWisefinSuccess()
        create_arr = data_obj['create_arr']
        update_arr = data_obj['update_arr']
        if len(update_arr) > 0:
            for vals in update_arr:
                EmployeeFamilyInfo.objects.using(self._current_app_schema()).filter(id=vals['id']).update(**vals)
                resp.set_message(SuccessMessage.UPDATE_MESSAGE)
            return resp
        if len(create_arr) > 0:
            clist = [EmployeeFamilyInfo(**vals) for vals in create_arr]
            EmployeeFamilyInfo.objects.using(self._current_app_schema()).bulk_create(clist)

            EmployeeFamilyInfo.objects.using(self._current_app_schema()).create(**vals)

            resp.set_message(SuccessMessage.CREATE_MESSAGE)
        return resp

    def get_employeefamilyinfo(self, employee_id):
        obj = EmployeeFamilyInfo.objects.using(self._current_app_schema()).filter(employee_id=employee_id,status=ActiveStatus.Active)
        empinfo = NWisefinList()
        for i in obj:
            data_resp = EmployeeFamilyInfoResponse()
            data_resp.set_id(i.id)
            data_resp.set_name(i.name)
            data_resp.set_relationship(i.relationship)
            data_resp.set_dob(i.dob)
            data_resp.set_no(i.no)
            empinfo.append(data_resp)
        return empinfo

    def create_empemergencycontact(self, data_obj, user_id):
        resp = NWisefinSuccess()
        serv = HrmsCommonService(self._scope())
        create_arr = data_obj['create_arr']
        update_arr = data_obj['update_arr']
        if len(update_arr) > 0:
            for data in update_arr:
                address = data['address']
                add_obj = HrmsAddressRequest(address)
                del data['address']
                serv.create_hrmsaddress(add_obj,user_id)
                EmployeeEmergencyContact.objects.using(self._current_app_schema()).filter(id=data['id']).update(**data)
                resp.set_message(SuccessMessage.UPDATE_MESSAGE)
        if len(create_arr) > 0:
            for i in create_arr:
                address = i['address']
                add_obj = HrmsAddressRequest(address)
                address_id = serv.create_hrmsaddress(add_obj, user_id)
                i['address_id'] = address_id
                del i['address']
            emplist = [EmployeeEmergencyContact(**data) for data in create_arr]
            EmployeeEmergencyContact.objects.using(self._current_app_schema()).bulk_create(emplist)
            resp.set_message(SuccessMessage.CREATE_MESSAGE)
        return resp

    def get_empemergencycontact(self, employee_id):
            obj = EmployeeEmergencyContact.objects.using(self._current_app_schema()).filter(employee_id=employee_id,status=ActiveStatus.Active)
            addressarr = [i.address_id for i in obj]
            module_serv = HrmsCommonService(self._scope())
            module_data = module_serv.address_get(addressarr)
            empemergency = NWisefinList()
            for i in obj:
                data_resp = EmpEmergencyContactResponse()
                data_resp.set_id(i.id)
                data_resp.set_name(i.name)
                data_resp.set_phone_no(i.phone_no)
                data_resp.set_relationship(i.relationship)
                data_resp.set_address_id(i.address_id, module_data)
                empemergency.append(data_resp)
            return empemergency


    def createshiftmapping(self,user_id,data,employeeid):
        shift_id = data['shift_id']
        effective_from = data['effective_from']
        emp_details1 = EmployeeShiftMapping.objects.using(self._current_app_schema()).create(
            employee_id=employeeid,
            shift_id=shift_id,
            effective_from=effective_from,
            created_by=user_id)
        success_obj = NWisefinSuccess()
        success_obj.set_status("Success")
        success_obj.set_message("Created Successfully")
        return success_obj

    def get_shiftmapping(self, employeeid):
        emp_details = EmployeeShiftMapping.objects.using(self._current_app_schema()).filter(employee_id=employeeid,status=ActiveStatus.Active,effective_to=None)
        if len(emp_details) == 0:
            resp = {'code': 'INVALID_ID', 'description': 'INVALID_DATA'}
            return resp
        empdetail = emp_details[0]
        resp = {"shift_id": empdetail.shift_id, "shift_name": empdetail.shift.shift_name, "start_time": str(empdetail.shift.start_time), "end_time": str(empdetail.shift.end_time)}
        return resp

    def employeeshiftmapping(self, vys_page, data):
        emp_id = data['arr']
        cond = Q(status=ActiveStatus.Active, effective_to=None)
        if len(emp_id) != 0:
            cond &= Q(employee_id__in=emp_id)
        emp_shift_summary = EmployeeShiftMapping.objects.using(self._current_app_schema()).filter(cond)[vys_page.get_offset():vys_page.get_query_limit()]
        employee_id_arr = [data.employee_id for data in emp_shift_summary]
        emp_serv = AttendanceAPIService(self._scope()).get_employee_list(employee_id_arr)
        shift_id_arr = [data.shift_id for data in emp_shift_summary]
        shift_serv = WorkShiftService(self._scope()).hrms_shiftmap_summary(shift_id_arr)
        shift_summary_data = NWisefinList()
        for data in emp_shift_summary:
            data_resp = EmpShiftMappingResponse()
            data_resp.set_employee_id(data.employee_id, emp_serv)
            data_resp.set_shift_id(data.shift_id, shift_serv)
            data_resp.set_effective_from(data.effective_from)
            shift_summary_data.append(data_resp)
        paginator = NWisefinPaginator(emp_shift_summary, vys_page.get_index(), 10)
        shift_summary_data.set_pagination(paginator)
        return shift_summary_data

    def empshifthistory(self,vys_page,employeeid):
        emp_details = EmployeeShiftMapping.objects.using(self._current_app_schema()).filter(employee_id=employeeid).order_by('-id')[vys_page.get_offset():vys_page.get_query_limit()]
        shift_id_arr = [i.shift_id for i in emp_details]
        shift_serv = WorkShiftService(self._scope()).hrms_shiftmap_summary(shift_id_arr)
        emp_shift_history = NWisefinList()
        for i in emp_details:
            data_resp = EmpShiftMappingResponse()
            data_resp.set_shift_id(i.shift_id, shift_serv)
            data_resp.set_effective_from(i.effective_from)
            data_resp.set_effective_to(i.effective_to)
            emp_shift_history.append(data_resp)
        paginator = NWisefinPaginator(emp_details, vys_page.get_index(), 10)
        emp_shift_history.set_pagination(paginator)
        return emp_shift_history

    def get_shiftmapping_logdate(self, employeeid,log_date):
        # cond = Q(employee_id=employeeid,status=ActiveStatus.Active)&(Q(effective_from__gte=log_date,effective_to__lte=log_date)or Q(effective_from__gte=log_date,effective_to=None))
        cond=Q(employee_id=employeeid,status=ActiveStatus.Active,effective_to=None)
        emp_details = EmployeeShiftMapping.objects.using(self._current_app_schema()).filter(cond)
        if len(emp_details) == 0:
            return
        empdetail = emp_details[0]
        resp = {"shift_id": empdetail.shift_id, "shift_name": empdetail.shift.shift_name, "start_time": str(empdetail.shift.start_time), "end_time": str(empdetail.shift.end_time)}
        return resp

