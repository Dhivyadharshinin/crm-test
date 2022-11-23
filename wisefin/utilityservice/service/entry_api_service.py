from wisefinapi.employeeapi import EmployeeAPI
from userservice.data.response.branchresponse import EmployeeBranchResponse
from userservice.service.employeeservice import EmployeeService,EmployeeBranchService
from  userservice.service.generalledgerservice import General_LedgerService
from apservice.service.apservice import APService
from apservice.service.apinvoiceheaderservice import APInvoiceheaderService
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
class ApiService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.ENTRY_SERVICE)

    MICRO_SERVICE = True

    def get_emp_id(self,request,emp_id):
        if self.MICRO_SERVICE:
            emp_ser = EmployeeService(self._scope())
            emp = emp_ser.get_employee_from_userid(emp_id)
            emp=emp.__dict__
            return emp
        else:
            emp_api=EmployeeAPI()
            emp = emp_api.get_emp_by_userid(request, emp_id)
            return emp

    def get_employee_branch(self,request, empid_arr):
        if self.MICRO_SERVICE:
            emp_ser = EmployeeBranchService(self._scope())
            d={"arr":empid_arr}
            branch_data = emp_ser.fetch_branch_data(d)
            arr=[]
            for i in branch_data.data:
                arr.append(i.__dict__)
            return arr
        else:
            pass
    def fetch_employeebranchdata(self, request, branch_id):
        if self.MICRO_SERVICE:
            pose_ser = EmployeeService(self._scope())
            pose = pose_ser.fetch_empbranch(branch_id)
            return pose
        else:
            emp_api = EmployeeAPI()
            user_employeebranch = emp_api.fetch_employeebranchdata(request, branch_id)
            return user_employeebranch

    def apcreditdirect_entry(self,apcredit_json,apinvhdr_id,emp_id):
        if self.MICRO_SERVICE:
            pose_ser = APService(self._scope())
            pose = pose_ser.apcredit_direct_entry(apcredit_json,apinvhdr_id,emp_id)
            return pose
        else:
            pass

    def apdebitdirect_entry(self,debit_json, apinvhdr_id,apinvdtls_id, emp_id):
        if self.MICRO_SERVICE:
            pose_ser = APService(self._scope())
            pose = pose_ser.apdebit_direct_entry(debit_json, apinvhdr_id,apinvdtls_id, emp_id)
            return pose
        else:
            pass

    def glno_description(self,request,glno):
        if self.MICRO_SERVICE:
            pose_ser = General_LedgerService(self._scope())
            pose = pose_ser.fetch_gl_no(request,glno)
            return pose
        else:
            pass

    def ap_header_id_to_header_data(self, header_id):
        if self.MICRO_SERVICE:
            pose_ser = APInvoiceheaderService(self._scope())
            pose = pose_ser.get_apinvhdr_using_apinvhdr(header_id)
            return pose
        else:
            pass


