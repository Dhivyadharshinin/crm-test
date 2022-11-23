from django.db.models import Q
from hrmsservice.models import EmployeeDocuments
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess
from hrmsservice.util.hrmsutil import EmployeeDocUtil,ActiveStatus
from utilityservice.service.hrms_api_service import HrmsAPIService

class EmployeeDocService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.HRMS_SERVICE)
        
    def create_employee_document(self, doc_data,d_type, employee_id,user_id):
        arr = []
        for m in doc_data:
            file_name = m.file_name
            gen_file_name = m.gen_file_name
            file_id = m.id
            document_var = EmployeeDocuments(type=d_type, rel_id=employee_id,rel_type=EmployeeDocUtil.employee_document, file_name=file_name,gen_file_name=gen_file_name, file_id=file_id, created_by=user_id)

            arr.append(document_var)
        if len(arr) > 0:
            document_var = EmployeeDocuments.objects.using(self._current_app_schema()).bulk_create(arr)

        return

    def fetch_docutype_byid(self,obj,id):
        for i in obj :
            if id ==i['id']:
                return i
        return

    def employee_doc_summary(self, employee_id):
        document_list = EmployeeDocuments.objects.using(self._current_app_schema()).filter(rel_id=employee_id,rel_type=EmployeeDocUtil.employee_document,status=ActiveStatus.Active).order_by('created_date')
        type_arr=[i.type for i in document_list]
        list_data = NWisefinList()
        apiserv=HrmsAPIService(self._scope())
        docutype_data=apiserv.get_multi_docutype(type_arr)
        for t in type_arr:
            # type data
            type =self.fetch_docutype_byid(docutype_data,t)

            file_arr = [{"id":i.id,"file_id":i.file_id,"file_name":i.file_name} for i in document_list if i.type ==t]
            data={"type":type,"file":file_arr}

            list_data.append(data)
        return list_data

    def employee_doc_delete(self, doc_id):
        document = EmployeeDocuments.objects.using(self._current_app_schema()).filter(id=doc_id).update(status=ActiveStatus.Delete)

        return
