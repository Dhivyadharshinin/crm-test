from masterservice.data.response.questionsubresponse import QuestionsubResponse
from masterservice.models import Questions_suboptions
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessMessage, SuccessStatus
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from masterservice.util.masterutil import ModifyStatus


class QuestionsubService(NWisefinThread):
    def __init__(self,scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def create_questionsub_options(self,questionsuboption_req, emp_id,question_id):
        resp = NWisefinSuccess()
        if not questionsuboption_req.get_id() is None:
            obj = Questions_suboptions.objects.using(self._current_app_schema()).filter(id=questionsuboption_req.get_id(),entity_id=self._entity_id()).update(options=questionsuboption_req.get_options(),
                                                                                                                        question_id=question_id,
                                                                                                                        # input_type=questionsuboption_req.get_input_type(),
                                                                                                                        order=questionsuboption_req.get_order(), updated_by=emp_id)


            obj=Questions_suboptions.objects.using(self._current_app_schema()).get(id=questionsuboption_req.get_id(),entity_id=self._entity_id())
            resp.set_message(SuccessMessage.UPDATE_MESSAGE)
            resp.set_status(SuccessStatus.SUCCESS)


        else:
            obj= Questions_suboptions.objects.using(self._current_app_schema()).create(options=questionsuboption_req.get_options(),
                                                                                        question_id=question_id,
                                                                                        # input_type = questionsuboption_req.get_input_type(),
                                                                                        order=questionsuboption_req.get_order(), created_by=emp_id, entity_id=self._entity_id())

            resp.set_status(SuccessStatus.SUCCESS)
            resp.set_message(SuccessMessage.CREATE_MESSAGE)

        return resp

    def fetch_questionsuboption(self, vys_page):
        obj = Questions_suboptions.objects.using(self._current_app_schema()).filter(entity_id=self._entity_id(),status=ModifyStatus.create).order_by('-created_date')[vys_page.get_offset():vys_page.get_query_limit()]
        list_data = NWisefinList()
        for i in obj:
            data_resp = QuestionsubResponse()
            data_resp.set_id(i.id)
            data_resp.set_order(i.order)
            # data_resp.set_input_type(i.input_type)
            data_resp.set_options(i.options)
            data_resp.set_question_id(i.question_id)
            list_data.append(data_resp)
        vpage = NWisefinPaginator(obj, vys_page.get_index(), 10)
        list_data.set_pagination(vpage)
        return list_data

    def get_questionsub_options(self, id):
        obj = Questions_suboptions.objects.using(self._current_app_schema()).get(id=id, entity_id=self._entity_id())
        data_resp = QuestionsubResponse()
        data_resp.set_id(obj.id)
        data_resp.set_options(obj.options)
        data_resp.set_order(obj.order)
        # data_resp.set_input_type(obj.input_type)
        data_resp.set_question_id(obj.question_id)

        return data_resp

    def del_questionsub_options(self, id):
        obj = Questions_suboptions.objects.using(self._current_app_schema()).filter(id=id, entity_id=self._entity_id()).update(status=ModifyStatus.delete)
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
        return success_obj



    def get_questionsuboptions2(self, question_id):
        obj = Questions_suboptions.objects.using(self._current_app_schema()).filter(question_id=question_id, entity_id=self._entity_id())
        list_data = []
        for x in obj:
            data_resp = QuestionsubResponse()
            data_resp.set_id(x.id)
            data_resp.set_options(x.options)
            data_resp.set_order(x.order)
            # data_resp.set_input_type(x.input_type)
            data_resp.set_question_id(x.question_id)
            list_data.append(data_resp)
        return list_data

    def get_questionsuboptions(self, question_id):
        obj = Questions_suboptions.objects.using(self._current_app_schema()).filter(question_id=question_id, entity_id=self._entity_id())
        list_data = []
        for x in obj:
            data_resp = QuestionsubResponse()
            data_resp.set_id(x.id)
            data_resp.set_options(x.options)
            data_resp.set_order(x.order)
            # data_resp.set_input_type(x.input_type)
            data_resp.set_question_id(x.question_id)
            list_data.append(data_resp.__dict__)
        return list_data