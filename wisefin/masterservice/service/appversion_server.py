from django.db.models import Q
from masterservice.data.request.appversionrequest import AppVersionRequest
from masterservice.models import AppVersion
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.threadlocal import NWisefinThread

class AppVersionServerService():
    def AppVersion_Server(self, entity):
        condition = Q(entity_id=entity)
        appversion = AppVersion.objects.using('masterdb').filter(condition).order_by('-id')[0:1]
        list_length = len(appversion)
        appversion_list_data = NWisefinList()
        if list_length > 0:
            for i in appversion:
                app_data = AppVersionRequest()
                app_data.set_id(i.id)
                app_data.set_no(i.no)
                app_data.set_ref_no(i.ref_no)
                app_data.set_remarks(i.remarks)
                appversion_list_data.append(app_data)
            return appversion_list_data
        else:
            return appversion_list_data