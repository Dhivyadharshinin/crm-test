from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from userservice.models.usermodels import Employee, EmployeeEntityMapping
from masterservice.models.mastermodels import OrgIP,LeaveType
from masterservice.util.masterutil import ModifyStatus
from userservice.data.response.employeeresponse import EmployeeResponse
from masterservice.service.leavegrademappingservice import GradeMappingService
from django.db.models import Q
class AttendanceAPIService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.ATTENDANCE_SERVICE)

    MICRO_SERVICE = True
    def get_emp_data_by_id(self, emp_id):
        if emp_id == -1:
            data = EmployeeResponse()
            data.set_id(emp_id)
            data.set_full_name('')
            return data
        employee = Employee.objects.using(self._current_app_schema()).filter(id=emp_id)
        if len(employee) != 0:
            data = EmployeeResponse()
            data.set_id(employee[0].id)
            data.set_full_name(employee[0].full_name)
            return data
        else:
            data = EmployeeResponse()
            data.set_id('')
            data.set_full_name('')
            return data

    def get_employee_list(self, emp_arr):
        employee_list = Employee.objects.using(self._current_app_schema()).filter(id__in=emp_arr)
        emp_list = []
        for employee in employee_list:
            data = EmployeeResponse()
            data.set_id(employee.id)
            data.set_full_name(employee.full_name)
            data.set_code(employee.code)
            emp_list.append(data)
        return emp_list

    def get_id_with_list(self, id_val, list_data):
        for i in list_data:
            if int(id_val) == int(i.id):
                return i
        return id_val

    def get_all_employee(self,entity_id):
        employee_list = EmployeeEntityMapping.objects.using(self._current_app_schema()).filter(
            entity_id=entity_id).values_list('employee_id',flat=True)
        # employee_list = []
        # for i in employee:
        #     employee_list.append(i.employee_id)
        employee_list = set(employee_list)
        employee_list = list(employee_list)
        employee_list_data = Employee.objects.using(self._current_app_schema()).filter(id__in=employee_list)
        return employee_list_data


    def get_grade_leave(self,grade,month,year):
        if self.MICRO_SERVICE:
            grd_serv = GradeMappingService(self._scope())
            data = grd_serv.get_leave_grade(grade,month,year)
            return data

    def get_active_grade_mapping(self):
        if self.MICRO_SERVICE:
            grd_serv = GradeMappingService(self._scope())
            data=grd_serv.get_active_grademapping()
            return data

    def get_employee_info_hrms(self,arr,vys_page,query):
        # search_employee_list
        condition = Q(entity_id=self._entity_id()) & Q(employee__status=1)
        if query is not None:
            condition &= (Q(employee__full_name__icontains=query) | Q(employee__code__icontains=query) | Q(
                employee__designation__icontains=query))
        if len(arr)>0:
            condition &= Q(employee_id__in=arr)

        employee_list_data = EmployeeEntityMapping.objects.values('employee__id', 'employee__full_name', 'employee__code').filter(condition)[ vys_page.get_offset():vys_page.get_query_limit()]
        print(employee_list_data)

        employee_list_data=list(employee_list_data)
        return employee_list_data

    def attendance_employee_info(self):
        # search_employee_list
        condition = Q(entity_id=self._entity_id()) & Q(employee__status=1)
        employee_list_data = EmployeeEntityMapping.objects.values('employee__id', 'employee__full_name','employee__code').filter(condition)

        employee_list_data = list(employee_list_data)
        return employee_list_data

    def get_employee_info(self, id):
        employee_list = Employee.objects.using(self._current_app_schema()).get(id=id)
        return employee_list

    def get_org_ip_info(self,org_id):
        ip_details = OrgIP.objects.using(self._current_app_schema()).filter(org_detail_id=org_id, status=ModifyStatus.create).values_list('ip',flat=True)
        ip_arr= list(ip_details)
        return ip_arr

    def get_leave_type(self):
        obj=LeaveType.objects.using(self._current_app_schema()).filter(status=ModifyStatus.create)
        return obj

    def get_isleave_type(self):
        obj = LeaveType.objects.using(self._current_app_schema()).filter(status=ModifyStatus.create,is_leave=True)
        return obj
