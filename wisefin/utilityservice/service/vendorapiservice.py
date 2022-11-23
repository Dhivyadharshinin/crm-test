from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from userservice.models.usermodels import Employee


class VendorAPIService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.VENDOR_SERVICE)

    def get_emp_name_id(self, emp_id):
        employee = Employee.objects.using(self._current_app_schema()).filter(id=emp_id)
        if len(employee) != 0:
            return employee[0].full_name
        else:
            return
