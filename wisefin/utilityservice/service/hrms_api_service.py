from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from userservice.service.employeeservice import EmployeeService
from wisefinapi.employeeapi import EmployeeAPI
from userservice.models.usermodels import Employee
from masterservice.service.cityservice import CityService
from masterservice.service.pincodeservice import PincodeService
from masterservice.service.stateservice import StateService
from masterservice.service.leaveattendanceservice import OrgDetails
from masterservice.service.documenttypeservice import DocumenttypeService
from utilityservice.service.attendanceapiservice import AttendanceAPIService
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage
class HrmsAPIService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.HRMS_SERVICE)

    MICRO_SERVICE = True

    def get_emp_id(self, request):
        user_id = request.user.id
        if self.MICRO_SERVICE:
            emp_ser = EmployeeService(self._scope())
            emp = emp_ser.get_employee_from_userid(user_id)
            emp = emp.__dict__
            emp['is_user'] = True
            return emp

        else:
            is_user = True
            emp_api = EmployeeAPI()
            emp = emp_api.get_emp_by_userid(request, user_id)
            emp['is_user'] = is_user
            return emp

    def get_multi_emp(self, request, empid_arr):
        if self.MICRO_SERVICE:
            emp_ser = EmployeeService(self._scope())
            emp = emp_ser.get_employee_info(empid_arr)
            return emp
        else:
            emp_api = EmployeeAPI()
            emp = emp_api.fetch_multi_empolyee(request, empid_arr)
            return emp

    def get_multi_docutype(self,arr):
        if self.MICRO_SERVICE:
            serv = DocumenttypeService(self._scope())
            emp = serv.fetch_multi_doctypedata(arr)
            return emp
        else:
            pass

    def employee_address_info(self,employeeid,user_id):
        emp_details = Employee.objects.using(self._current_app_schema()).get(id=employeeid)
        city_id = emp_details.address.city_id
        city = CityService(self._scope()).fetch_city(city_id, user_id)
        city_name = city.name
        pincode_id = emp_details.address.pincode_id
        pincode = PincodeService(self._scope()).fetch_pincode(pincode_id, user_id)
        pincodeno = pincode.no
        state_id = emp_details.address.state_id
        state = StateService(self._scope()).fetchstate(state_id)
        statename = state.name

        empdata = {"name": emp_details.full_name, "address": {"line1": emp_details.address.line1,
                                                        "line2": emp_details.address.line2, "city": city_name,
                                                        "pincode": pincodeno, "state": statename},
             "designation": emp_details.designation}
        return empdata

    def get_org_info(self,employee_id):
        emp_obj = AttendanceAPIService(self._scope()).get_employee_info(employee_id)
        emp_details = emp_obj.org_id
        if emp_details == None:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description("INVALID_DATA")
            return error_obj
        org_obj = OrgDetails.objects.using(self._current_app_schema()).filter(id=emp_details, status=1).order_by('-id')
        org_details = org_obj[0]
        if org_details.address_id == None:
            line1, line2, line3, city, pincode, state = None, None, None, None, None, None
        else:
            org_city = org_details.address.city_id
            orgcity = CityService(self._scope()).fetch_city(org_city, None)
            city = orgcity.name
            org_pincode = org_details.address.pincode_id
            orgpincode = PincodeService(self._scope()).fetch_pincode(org_pincode, None)
            pincode = orgpincode.no
            org_state = org_details.address.state_id
            orgstate = StateService(self._scope()).fetchstate(org_state)
            state = orgstate.name
            line1 = org_details.address.line1
            line2 = org_details.address.line2
            line3 = org_details.address.line3
        orgdata = {"name": org_details.name, "address": {
                   "line1": line1, "line2": line2,
                   "line3": line3, "city": city, "pincode": pincode, "state": state}}
        return orgdata
