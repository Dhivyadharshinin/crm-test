from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace
from hrmsservice.models import EmployeeBankDetails
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess,SuccessMessage
from hrmsservice.data.response.empbankdetailsresponse import EmpBankDetailResponse
from hrmsservice.util.hrmsutil import ActiveStatus
from utilityservice.data.response.nwisefinlist import NWisefinList
class EmpBankDetailsService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.HRMS_SERVICE)

    def create_empbankdetails(self,data_obj):
        resp = NWisefinSuccess()
        if 'id' in data_obj:
            EmployeeBankDetails.objects.using(self._current_app_schema()).filter(id=data_obj['id']).update(**data_obj)
            resp.set_message(SuccessMessage.UPDATE_MESSAGE)
        else:
            obj = EmployeeBankDetails.objects.using(self._current_app_schema()).create(**data_obj)
            resp.set_message(SuccessMessage.CREATE_MESSAGE)
            resp.id = obj.id
        return resp


    def get_empbankdetails(self, employee_id):
        obj = EmployeeBankDetails.objects.using(self._current_app_schema()).filter(employee_id=employee_id,status=ActiveStatus.Active)
        empbank= NWisefinList()
        for i in obj:
            data_resp = EmpBankDetailResponse()
            data_resp.set_id(i.id)
            data_resp.set_account_name(i.account_name)
            data_resp.set_bank_id(i.bank_id)
            data_resp.set_bank_branch(i.bank_branch)
            data_resp.set_account_no(i.account_no)
            data_resp.set_ifsc(i.ifsc)
            empbank.append(data_resp)
        return empbank

