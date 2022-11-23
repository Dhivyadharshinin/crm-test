from masterservice.models.mastermodels import vendoroutsourcequestionnaire
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.applicationconstants import ApplicationNamespace


class QuestionService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def get_questions(self, quest_type):
        questions = vendoroutsourcequestionnaire.objects.using(self._current_app_schema()).filter(
            ques_type=quest_type, entity_id=self._entity_id()).order_by('id')
        return questions
