from django.db.models import Q

from cmsservice.util.cmsutil import ActiveStatus
from productservice.data.response.sourceresponse import SourceResponse
from productservice.models.productmodels import Source
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessMessage
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from productservice.util.product_util import CodePrefix
from cmsservice.service.codegenhistoryservice import Codegenservice


class SourceService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.CRM_SERVICE)
    def create_source(self,data_obj,emp_id):
        resp=NWisefinSuccess()
        # if 'id' in data_obj:
        #     emp=Source.objects.using(self._current_app_schema).filter(id=data_obj['id']).update(**data_obj)
        #     resp.set_message(SuccessMessage.UPDATE_MESSAGE)
        # else:
        table_type = CodePrefix.source
        codegen_service = Codegenservice(self._scope)
        code = codegen_service.codegen(table_type, emp_id)
        data_obj['code']=code
        emp=Source.objects.using(self._current_app_schema()).create(**data_obj)
        resp.set_message(SuccessMessage.CREATE_MESSAGE)
        return resp

    def fetch_source(self,request,vys_page):
        name=request.GET.get('name')
        condition  = Q(status=ActiveStatus.Active)
        if name is not None and name !='':
            condition&=Q(name__icontains=name)
        emp=Source.objects.using(self._current_app_schema()).filter(condition).order_by('-created_date')[vys_page.get_offset():vys_page.get_query_limit()]
        list_data=NWisefinList()
        for i in emp:
            resp=SourceResponse()
            resp.set_id(i.id)
            resp.set_type(i.type)
            resp.set_name(i.name)
            resp.set_code(i.code)
            list_data.append(resp)
        vpage = NWisefinPaginator(emp, vys_page.get_index(), 10)
        list_data.set_pagination(vpage)
        return list_data

    def particular_get_source(self,id):
        emp=Source.objects.using(self._current_app_schema()).get(id=id)
        resp = SourceResponse()
        resp.set_id(emp.id)
        resp.set_type(emp.type)
        resp.set_name(emp.name)
        resp.set_code(emp.code)
        return resp


