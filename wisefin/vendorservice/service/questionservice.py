from masterservice.models import Vendorclassification_Mapping, Questions
from utilityservice.service.vendorclassification_api import Vendormaster
from vendorservice.models.vendormodels import  Vendor
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace



class Qestionservice(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.VENDOR_SERVICE)

    def fetch_vendoreval(self, request,vendor_id):
        vendor_data = Vendor.objects.using(self._current_app_schema()).get(id=vendor_id, entity_id=self._entity_id())
        if vendor_data:

                data={
                "rel_cat":vendor_data.group,
                "vendor_type":vendor_data.classification,
                "criticality":vendor_data.type}
        else:
            data={}
        return data



