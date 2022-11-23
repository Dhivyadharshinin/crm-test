from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from vendorservice.models import Question_vendor_mapping, Questions_Queue

class QuestionvendormapService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.VENDOR_SERVICE)

    def question_answer_mapping(self, question_req,emp_id):
        if not question_req.get_id() is None:
            obj = Question_vendor_mapping.objects.using(self._current_app_schema()).filter(id=question_req.get_id(),
                                                                                    entity_id=self._entity_id()).update(
                vendor_id=question_req.get_vendor_id(),
                Activity=question_req.get_Activity(),
                question_type=question_req.get_question_type(),
                period=question_req.get_period(),
                # periodicity=question_req.get_periodicity(),
                remarks=question_req.get_remarks(),
                type_status=question_req.get_type_status(),
                updated_by=emp_id,period_start=question_req.get_period_start(),period_end=question_req.get_period_end())

            obj = Question_vendor_mapping.objects.using(self._current_app_schema()).get(id=question_req.get_id(),
                                                                                 entity_id=self._entity_id())

            Questions_Queue.objects.using(self._current_app_schema()).create(from_user_id=emp_id, to_user_id=-1,
                                                                             comments='NEW',
                                                                             remarks=question_req.get_remarks(),
                                                                             is_sys=True,
                                                                             entity_id=self._entity_id())
        else:
            obj = Question_vendor_mapping.objects.using(self._current_app_schema()).create(
                vendor_id=question_req.get_vendor_id(),
                Activity=question_req.get_Activity(),
                question_type=question_req.get_question_type(),
                period=question_req.get_period(),
                # periodicity=question_req.get_periodicity(),
                remarks=question_req.get_remarks(),
                type_status=question_req.get_type_status(),
                entity_id=self._entity_id(),
                created_by=emp_id,period_start=question_req.get_period_start(),period_end=question_req.get_period_end())

            Questions_Queue.objects.using(self._current_app_schema()).create(from_user_id=emp_id, to_user_id=-1,
                                                                             comments='NEW',
                                                                             remarks=question_req.get_remarks(),
                                                                             is_sys=True,
                                                                             entity_id=self._entity_id())
        resp = obj.id
        print("id",resp)
        success_obj = NWisefinSuccess()
        success_obj.set_status("Success")
        success_obj.set_message("Created Successfully")
        return obj
