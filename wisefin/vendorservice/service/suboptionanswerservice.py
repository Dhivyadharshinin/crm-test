from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from vendorservice.data.response.suboptionanswerresponse import SuboptionanswerResponse
from vendorservice.models import Suboption_Answers


class SuboptionanswerService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.VENDOR_SERVICE)

    def suboption_create(self, suboption_req,emp_id,question_ans_id):
        resp = NWisefinSuccess()
        if not suboption_req.get_id() is None:
            obj = Suboption_Answers.objects.using(self._current_app_schema()).filter(id=suboption_req.get_id(), entity_id=self._entity_id()).update(question_ans_id=question_ans_id,
                                                                                                                        option_id=suboption_req.get_option_id(),
                                                                                                                        # answer=suboption_req.get_answer(),
                                                                                                                        updated_by=emp_id)

            Suboption_Answers.objects.using(self._current_app_schema()).get(id=suboption_req.get_id(),
                                                                               entity_id=self._entity_id())


        else:
            obj = Suboption_Answers.objects.using(self._current_app_schema()).create(question_ans_id=question_ans_id,
                                                                                     option_id=suboption_req.get_option_id(),
                                                                                     entity_id=self._entity_id(),
                                                                                     created_by=emp_id)

            resp.set_status(SuccessStatus.SUCCESS)
            resp.set_message(SuccessMessage.CREATE_MESSAGE)

        return resp


    def fetch_suboption_answer(self,vys_page):
        suboptions_obj = Suboption_Answers.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id()).order_by('-created_date')[vys_page.get_offset():vys_page.get_query_limit()]
        list_data = NWisefinList()
        for obj in suboptions_obj:
            data_resp = SuboptionanswerResponse()
            data_resp.set_id(obj.id)
            data_resp.set_answer(obj.answer)
            data_resp.set_option_id(obj.option_id)
            data_resp.set_question_ans_id(obj.question_ans_id)
            list_data.append(data_resp)
        vpage = NWisefinPaginator(suboptions_obj, vys_page.get_index(), 10)
        list_data.set_pagination(vpage)
        return list_data

    def suboption_get(self, id):
        suboption_obj = Suboption_Answers.objects.using(self._current_app_schema()).get(id=id)
        data_resp = SuboptionanswerResponse()
        data_resp.set_id(suboption_obj.id)
        data_resp.set_answer(suboption_obj.answer)
        data_resp.set_option_id(suboption_obj.option_id)
        data_resp.set_question_ans_id(suboption_obj.question_ans_id)
        return data_resp

    def del_suboption(self, id):
        obj = Suboption_Answers.objects.using(self._current_app_schema()).filter(id=id, entity_id=self._entity_id()).delete()
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
        return success_obj

    def get_suboptions_answer(self,question_id):
        obj = Suboption_Answers.objects.using(self._current_app_schema()).filter(question_ans_id=question_id,entity_id=self._entity_id())
        list_data = []
        for x in obj:
            data_resp = SuboptionanswerResponse()
            data_resp.set_id(x.id)
            data_resp.set_answer(x.answer)
            data_resp.set_option_id(x.option_id)
            data_resp.set_question_ans_id(x.question_ans_id)
            list_data.append(data_resp)
        return list_data