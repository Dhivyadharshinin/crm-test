from cmsservice.models import QuestionnaireTimer,QuestionClassification
from cmsservice.util.cmsutil import DocUtil,ApprovalStatus,ActiveStatus,TranStatus
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
import datetime
from utilityservice.service.cms_api_service import ApiService
from cmsservice.data.response.cmsquestiontyperesponse import QuestionnaireTimerResponse

class QuestionnaireTimerService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.CMS_SERVICE)

    # PROJECT LEVEL Q TIMER
    def project_questionnaire_timer(self, project_id, data, empid):
        q_arr = data['arr']
        timer_on = data['timer_on']
        tag_timer = data['tag_timer']
        arr = []
        for i in q_arr:
            obj = QuestionnaireTimer(project_id=project_id, order=i['order'], question_type=i['question_type'],tag_timer=tag_timer, timer_on=timer_on, created_by=empid)
            arr.append(obj)

        if len(arr) > 0:
            QuestionnaireTimer.objects.bulk_create(arr)
        return

    # PROPOSAL LEVEL Q TIMER
    def proposal_questionnaire_timer(self, project_id, proposal_id, empid):
        qtimer_obj = QuestionnaireTimer.objects.filter(project_id=project_id)
        arr = []
        if len(qtimer_obj) > 0:
            for qtimer_data in qtimer_obj:
                approval_status = TranStatus.awaiting
                if qtimer_data.order ==1 or qtimer_obj.pa :
                    approval_status=TranStatus.pending
                obj = QuestionClassification(classify_id=proposal_id, classify_type=DocUtil.proposer,question_type=qtimer_data.question_type, timer_on=qtimer_data.timer_on,tag_timer=qtimer_data.tag_timer, order=qtimer_data.order,approval_status=ApprovalStatus.DRAFT,created_by=empid)

                arr.append(obj)
                QuestionClassification.objects.bulk_create(arr)

        return

    def proposal_questionnaire_submite(self,proposal_id,type,status,empid):

        obj=QuestionClassification.objects.filter(classify_id=proposal_id, classify_type=DocUtil.proposer,question_type=type,status=ActiveStatus.Active)

        if len(obj)==0:
            pass

        if status not in [ApprovalStatus.APPROVED,ApprovalStatus.REVIEW]:
            pass

        classification_obj = obj[0]
        classification_id = classification_obj.id
        parallel_approval = classification_obj.parallel_approval
        order = classification_obj.order
        tag_timer = classification_obj.tag_timer
        approval_status = classification_obj.approval_status

        if approval_status in [ApprovalStatus.PENDING,ApprovalStatus.APPROVED,ApprovalStatus.REVIEW]:
            pass

        if parallel_approval ==False:
            QuestionClassification.objects.filter(id=classification_id).update(approval_status=status,updated_by=empid,updated_date=datetime.datetime.now())


            QuestionClassification.objects.filter(classify_id=proposal_id, classify_type=DocUtil.proposer,question_type=type,status=ActiveStatus.Active,order=(order+1)).update(approval_status= TranStatus.pending,updated_by=empid,updated_date=datetime.datetime.now(),start_timer=datetime.datetime.now())

        return


    def get_questiontype_byproject(self,project_id):
        obj=QuestionClassification.objects.filter(project_id=project_id,status=ActiveStatus.Active)
        qtype=[i.question_type for i in obj]
        apiserv=ApiService(self._scope)
        question_type=apiserv.get_questype(qtype)

        list_data = []
        for i in question_type:
            data_resp = QuestionnaireTimerResponse()

        return

