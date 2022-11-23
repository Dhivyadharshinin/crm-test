from pprservice.models.pprmodel import bscc_maping,AllocationLevel,CostDriver
from masterservice.models import CostCentre,BusinessSegment
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


class CostAllocation_utilityservice(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.PPR_SERVICE)
    def get_bsccmaping(self, id):
        obj = bscc_maping.objects.using(self._current_app_schema()).filter(id__in=id,entity_id=self._entity_id()).values('id', 'name','code')
        arr = []
        for i in obj:
            data = {"id": i['id'], "name": i['name'],"code":i['code']}
            arr.append(data)
        return arr

    def get_allocationlevel(self, id):
        obj = AllocationLevel.objects.using(self._current_app_schema()).filter(id__in=id,entity_id=self._entity_id()).values('id', 'name','code','reportlevel')
        arr = []
        for i in obj:
            data = {"id": i['id'], "name": i['name'],"code":i['code'],"reportlevel":i['reportlevel']}
            arr.append(data)
        return arr

    def get_costdriver(self, id):
        obj = CostDriver.objects.using(self._current_app_schema()).filter(id__in=id,entity_id=self._entity_id()).values('id', 'name','code','parameter_name')
        arr = []
        for i in obj:
            data = {"id": i['id'], "name": i['name'],"code":i['code'],"parameter_name":i['parameter_name']}
            arr.append(data)
        return arr

    def get_costcenter(self,id):
        obj = CostCentre.objects.using(self._current_app_schema()).filter(id__in=id,entity_id=self._entity_id()).values('id','name')
        arr = []
        for i in obj:
            data = {"id": i['id'], "name": i['name']}
            arr.append(data)
        return arr

    def get_businesssegment(self,id):
        obj = BusinessSegment.objects.using(self._current_app_schema()).filter(id__in=id,entity_id=self._entity_id()).values('id','name')
        arr = []
        for i in obj:
            data = {"id": i['id'], "name": i['name']}
            arr.append(data)
        return arr
