from vendorservice.data.response.vendorhistoryresponse import VendorHistoryResponse
from vendorservice.models import VendorQueue
from utilityservice.service.utilityservice import NWisefinUtilityService
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.data.response.nwisefinuser import NWisefinUser
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace


class VendorHistoryService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.VENDOR_SERVICE)

    def get_vendor_history(self, request, memo_id, user_id, vys_page):
        vendor_history_arr = VendorQueue.objects.using(self._current_app_schema()).filter(vendor_id_id = memo_id, entity_id=self._entity_id())[vys_page.get_offset():vys_page.get_query_limit()]
        history_resp_list = NWisefinList()
        user_list = []


        for history in vendor_history_arr:
            if (history.from_user_id !=0):
                user_list.append(history.from_user_id)
            if (history.to_user_id !=0):
                user_list.append(history.to_user_id)
        user_list = set(user_list)
        user_list = list(user_list)
        utility_service = NWisefinUtilityService()
        user_list_obj = utility_service.get_emp_info_by_id(request, user_list)
        vys_user = NWisefinUser()
        vys_user.set_id(0)
        vys_user.set_full_name('')

        for memo_history in vendor_history_arr:
            history_resp = VendorHistoryResponse()
            history_resp.set_comments(memo_history.comments)
            history_resp.set_status(memo_history.status)
            if (memo_history.from_user_id == 0):
                history_resp.set_from_id(vys_user)
            if (memo_history.to_user_id == 0):
                history_resp.set_to_id(vys_user)

            for ul in user_list_obj['data']:
                if ul['id'] == memo_history.from_user_id:
                    history_resp.set_from_id(ul)
            for ul in user_list_obj['data']:
                if ul['id'] == memo_history.to_user_id:
                    history_resp.set_to_id(ul)
            # history_resp.set_created_date(memo_history.created_date)
            created_date = memo_history.created_date
            created_date =str(created_date)
            dstr = created_date.split(" ")
            history_resp.set_created_date(dstr[0])
            history_resp_list.append(history_resp)
            vpage = NWisefinPaginator(vendor_history_arr, vys_page.get_index(), 10)
            history_resp_list.set_pagination(vpage)
        return history_resp_list