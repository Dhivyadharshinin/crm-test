from django.db.models import Q
from django.utils.timezone import now

from faservice.data.response.cgumasterresponse import CGUMasterResponse
from faservice.models import CGUMASTER
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


class CGUMASTERService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.FA_SERVICE)
    def create_cgumst(self, cgumst_obj, emp_id):
        cgu = CGUMASTER.objects.create(
            name=cgumst_obj.get_name(),
            # code=cgumst_obj.get_code(),
            created_by=emp_id)
        code = "CGU" + str(cgu.id)
        cgu.code = code
        cgu.save()
        cgumst_data = CGUMasterResponse()
        cgumst_data.set_id(cgu.id)
        cgumst_data.set_name(cgu.name)
        cgumst_data.set_code(cgu.code)
        cgumst_data.set_status(cgu.status)
        return cgumst_data

    def search_cgu_name(self, vys_page, query):
        condition = Q(status=1) & Q(name__icontains=query)
        cguassetmaplist = CGUMASTER.objects.filter(condition)[vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(cguassetmaplist)
        cgu_list_data = NWisefinList()
        if list_length > 0:
            for cgu in cguassetmaplist:
                cgumst_data = CGUMasterResponse()
                cgumst_data.set_id(cgu.id)
                cgumst_data.set_name(cgu.name)
                cgumst_data.set_code(cgu.code)
                cgu_list_data.append(cgumst_data)
            vpage = NWisefinPaginator(cguassetmaplist, vys_page.get_index(), 10)
            cgu_list_data.set_pagination(vpage)
        return cgu_list_data
