from memoservice.models import MemoRequest
from memoservice.data.response.memoresponse import MemoResponse
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace


class MemoService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MEMO_SERVICE)

    def create_memo(self, memo_data):
        if memo_data.get_id() is None:
            memo = MemoRequest.objects.using(self._current_app_schema()).create(subject=memo_data.get_subject(),
                                                                                req_date=memo_data.get_req_date(),
                                                                                category=memo_data.get_category(),
                                                                                sub_category=memo_data.get_sub_category(),
                                                                                entity_id=self._entity_id())
        else:
            memo = MemoRequest.objects.using(self._current_app_schema()).filter(id=memo_data.get_id(),entity_id=self._entity_id())\
                .update(subject=memo_data.get_subject(), req_date=memo_data.get_req_date(),
                        category=memo_data.get_category(), sub_category=memo_data.get_sub_category(),
                        entity_id=self._entity_id())
        resp = MemoResponse()
        resp.set_id(memo.id)
        resp.set_subject(memo.subject)
        resp.set_req_date(memo.req_date)
        resp.set_category(memo.category)
        resp.set_sub_category(memo.sub_category)
        return resp

    def fetch_memo(self):
        value = MemoRequest.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id())
        memo_list = []
        for memo in value:
            resp = MemoResponse()
            resp.set_id(memo.id)
            resp.set_subject(memo.subject)
            resp.set_req_date(memo.req_date)
            resp.set_category(memo.category)
            resp.set_sub_category(memo.sub_category)
            memo_list.append(resp.get())
        return memo_list

    def delete_memo(self, memo_id):
        if memo_id is not None:
            MemoRequest.objects.using(self._current_app_schema()).filter(id=memo_id,entity_id=self._entity_id()).delete()
            resp = NWisefinSuccess()
            resp.set_status(200)
            resp.set_message('Memo Deleted Successfully')
        else:
            resp = NWisefinError()
            resp.set_code(404)
            resp.set_description('Invalid Memo ID')
        return resp
