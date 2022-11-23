import traceback
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from userservice.models import DepartmentDocument
from docservice.service.documentservice import DocumentsService
from userservice.data.response.departmentresponse import DepartmentuploadResponse
from masterservice.util.masterutil import MasterDocUtil
from docservice.util.docutil import DocModule
from cmsservice.util.cmsutil import ActiveStatus
from datetime import datetime, timedelta
from django.db.models import Q
class DepartmentService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.USER_SERVICE)

    def deptuploadfile(self,dept_obj,emp_id,dept_id):
        dept = DepartmentDocument.objects.using(self._current_app_schema()).create(
                                                        department_id=dept_id,
                                                        name=dept_obj.get_name(),
                                                        remarks=dept_obj.get_remarks(),
                                                        created_by=emp_id)
        depart=dept.id
        return depart
    def getdeptuploadfile(self,dept_id,scope,request):
        condition = Q(department_id=dept_id) & Q(status=ActiveStatus.Active)
        fromdate = request.GET.get('fromdate')
        todate = request.GET.get('todate')
        name = request.GET.get('name')
        if (fromdate is not None):
            condition &= Q(created_date__gte=fromdate)
        if (todate is not None):
            adddate = (datetime.strptime(todate, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
            condition &= Q(created_date__lt=adddate)
        if (name is not None):
            condition &= Q(name__icontains=name)
        dept = DepartmentDocument.objects.using(self._current_app_schema()).filter(condition)
        departmentdocumentid = [department.id for department in dept]
        module = DocModule().MASTER
        rel_type = MasterDocUtil().DEPARTMENT
        array= []
        files = DocumentsService(scope)
        file_data= files.get_file_info_by_reltype(departmentdocumentid,rel_type,module)
        for i in dept:
            data = DepartmentuploadResponse()
            data.set_name(i.name)
            data.set_remarks(i.remarks)
            file_arr=[]
            for j in file_data:
                if j.rel_id == i.id:
                    file_arr.append(j)
            data.set_file(file_arr)
            array.append(data.get())
        return array


