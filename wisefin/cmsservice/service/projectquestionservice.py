from django.db.models import Q
from cmsservice.data.response.projectquestionresponse import CMSActivityresponse
from cmsservice.data.response.quesansresponse import Questionansmapresponse

from cmsservice.models import ProjectQuestions, ProjectProposalAnswers, CMSActivity, ProposedContract
from cmsservice.util.cmsutil import ActiveStatus, DocUtil, ProjectQuestionType, get_projectquestiontype
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.service.utilityservice import NWisefinUtilityService
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess
from utilityservice.service import cms_api_service
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage

utilityservice=NWisefinUtilityService()
class Projectquesservice(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.CMS_SERVICE)

    def create_projques(self,projans_data,prjt_id,emp_id):
        arr=[]
        for ans_obj in projans_data:
            proj = ProjectQuestions(q_type=ans_obj.get_q_type(),
                                                project_id = prjt_id,
                                                text = ans_obj.get_text(),
                                                order = ans_obj.get_order(),
                                                created_by=emp_id)
            arr.append(proj)

        ProjectQuestions.objects.using(self._current_app_schema()).bulk_create(arr)

        success_obj = NWisefinSuccess()
        success_obj.set_status("Success")
        success_obj.set_message("Created Successfully")
        return success_obj


    def fetch_projquestionmap(self,pro_id):
        quesclass = ProjectQuestions.objects.using(self._current_app_schema()).filter(project_id=pro_id).values_list('q_type',flat=True)
        print(quesclass)
        return quesclass
    def fetch_projques(self,pro_id):
        quesclass = ProjectQuestions.objects.using(self._current_app_schema()).filter(q_type__in=pro_id)
        print("qtype",quesclass)
        return quesclass

    def create_catlog(self,projans_data,proposal_id,emp_id):

        val_activate=CMSActivity.objects.using(self._current_app_schema()).filter(proposal_id=proposal_id,entity_id=self._entity_id())
        
        if len(val_activate) >0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.DUPLICATE_ENTRY)
            error_obj.set_description(ErrorMessage.DUPLICATE_ENTRY)
            return error_obj

        if projans_data.get_supplier_code() == '' and projans_data.get_supplier_code() == None:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description("SUPPLIER CODE EMPTY")
            return error_obj
            
        catlog = CMSActivity.objects.using(self._current_app_schema()).create(proposal_id = proposal_id,supplier_code = projans_data.get_supplier_code(), type = projans_data.get_type(),name = projans_data.get_name(),description = projans_data.get_description(),start_date = projans_data.get_start_date(),end_date = projans_data.get_end_date(),contract_spend = projans_data.get_contract_spend(),rm = projans_data.get_rm(),fidelity = projans_data.get_fidelity(),bidding = projans_data.get_bidding(),raisor = projans_data.get_raisor(),approver = projans_data.get_approver(),productname = projans_data.get_productname(),category = projans_data.get_category(),subcategory = projans_data.get_subcategory(),created_by = emp_id)

        success_obj = NWisefinSuccess()
        success_obj.set_status("Success")
        success_obj.set_message("Created Successfully")
        return success_obj

    def fetch_proposalcatlog(self,request,proposal_id):
        activity_obj = CMSActivity.objects.using(self._current_app_schema()).filter(proposal_id=proposal_id,
                                                                            entity_id=self._entity_id())
        
        if len(activity_obj)==0:
            act_data = CMSActivityresponse()
            act_data.is_created = False
            act_data.is_vendor = False
            return act_data

        response=self.common_fetch_proposal(request,activity_obj[0])
        response.is_created =True
        return response

    def fetch_proposalcatlog_by_suppliercode(self,request,supplier_code):
        activity_obj = CMSActivity.objects.using(self._current_app_schema()).get(supplier_code=supplier_code, entity_id=self._entity_id(),status=ActiveStatus.Active)

        response=self.common_fetch_proposal(request,activity_obj)

        return response
    
    def common_fetch_proposal(self,request,activity_obj):
        api_serv = cms_api_service.ApiService(self._scope())
        activity_data = CMSActivityresponse()
        emp_arr=[activity_obj.rm,activity_obj.raisor,activity_obj.approver]
        emp_data=api_serv.get_multi_emp(request, emp_arr)

        activity_data.set_id(activity_obj.id)
        activity_data.set_proposal_id(activity_obj.proposal_id)
        activity_data.set_supplier_code(activity_obj.supplier_code)
        activity_data.set_type(activity_obj.type)
        activity_data.set_name(activity_obj.name)
        activity_data.set_description(activity_obj.description)
        activity_data.set_start_date(activity_obj.start_date)
        activity_data.set_end_date(activity_obj.end_date)
        activity_data.set_contract_spend(activity_obj.contract_spend)
        activity_data.set_rm(activity_obj.rm,emp_data)
        activity_data.set_fidelity(activity_obj.fidelity)
        activity_data.set_bidding(activity_obj.bidding)
        activity_data.set_raisor(activity_obj.raisor, emp_data)
        activity_data.set_approver(activity_obj.approver, emp_data)
        activity_data.set_productname(api_serv.get_product(activity_obj.productname))
        activity_data.set_category(api_serv.get_cat_id(activity_obj.category))
        activity_data.set_subcategory(api_serv.get_subcat_id(activity_obj.subcategory))
        activity_data.is_created = activity_obj.is_created

        is_vendor = ProposedContract.objects.using(self._current_app_schema()).get(id=activity_obj.proposal_id).is_vendor
        activity_data.is_vendor =is_vendor
        return activity_data

    # used for vendor create
    def fetch_proposalvendor_proposal(self, request, proposal_id):
        condi = Q(entity_id=self._entity_id()) & Q(status=ActiveStatus.Active) & Q(proposal_id=proposal_id)
        # if (supplier_code is not None) & (supplier_code != ''):
        #     condi &= Q(supplier_code=supplier_code)
        activity_obj = CMSActivity.objects.using(self._current_app_schema()).get(condi)
        response = self.fetch_proposalvendor(request, activity_obj)
        return response

    # used for vendor create
    def fetch_proposalvendor(self, request, activity_obj):
        api_serv = cms_api_service.ApiService(self._scope())
        emp_arr = [activity_obj.rm, activity_obj.raisor, activity_obj.approver]
        emp_data = api_serv.get_multi_emp(request, emp_arr)

        activity_data = CMSActivityresponse()
        activity_data.set_id(activity_obj.id)
        activity_data.set_proposal_id(activity_obj.proposal_id)
        activity_data.set_supplier_code(activity_obj.supplier_code)
        activity_data.set_type(activity_obj.type)
        activity_data.set_name(activity_obj.name)
        activity_data.set_description(activity_obj.description)
        activity_data.set_start_date(activity_obj.start_date)
        activity_data.set_end_date(activity_obj.end_date)
        activity_data.set_contract_spend(activity_obj.contract_spend)
        activity_data.set_rm(activity_obj.rm,emp_data)
        activity_data.set_fidelity(activity_obj.fidelity)
        activity_data.set_bidding(activity_obj.bidding)
        activity_data.set_raisor(activity_obj.raisor, emp_data)
        activity_data.set_approver(activity_obj.approver, emp_data)
        activity_data.set_productname(api_serv.get_product(activity_obj.productname))
        activity_data.set_category(api_serv.get_cat_id(activity_obj.category))
        activity_data.set_subcategory(api_serv.get_subcat_id(activity_obj.subcategory))
        activity_data.is_created = activity_obj.is_created
        return activity_data

    def question_fetch(self,project_id,proposal_id):
        questions_obj = ProjectQuestions.objects.using(self._current_app_schema()).filter(project_id=project_id)

        ques_arr =[i.id for i in questions_obj]
        ans_resp = ProjectProposalAnswers.objects.using(self._current_app_schema()).filter(question__in=ques_arr, ref_id=proposal_id,ref_type=DocUtil.proposer)

        q_type = list(set([q.q_type for q in questions_obj]))

        resp_list = NWisefinList()
        for j in q_type:
            q_arr = []
            questions=self.get_project_question_by_type(j,questions_obj)
            answer_arr=self.validate_is_answer(j,ans_resp)
            is_answer=True
            if len(answer_arr)==0:
                is_answer = False

            type = {"id": j, "name": ProjectQuestionType.project_execution_val}
            for i in questions:
                data_resp = Questionansmapresponse()
                data_resp.set_id(i.id)
                data_resp.set_text(i.text)
                data_resp.set_order(i.order)
                data_resp.ans = self.get_answer(i.id, ans_resp)
                q_arr.append(data_resp)
            d = {"type": type, "questions": q_arr, "is_answer": is_answer}
            resp_list.append(d)

        return resp_list

    def get_project_question_by_type(self,typeid,q_obj):
        arr=[i for i in q_obj if i.q_type==typeid]
        return arr
    def validate_is_answer(self,typeid,a_obj):
        arr=[i for i in a_obj if i.question.q_type==typeid]
        return arr

    def get_answer(self, q_id, ans_obj):
        d=None
        for i in ans_obj:
            if i.question_id == q_id:
                d = {"id": i.id, "answer": i.answer}
        return d

from userservice.controller.vowusercontroller import VowUser
class Vow_question_answer:
    def __init__(self, request):
        vowuser_info = VowUser().get_user(request)
        self.emp_id = vowuser_info['user_id']
        self.entity_id = vowuser_info['entity_id']
        self.is_user = vowuser_info['is_user']
        self.schema = vowuser_info['schema']
    def create_projproposal(self, projans_data, prjt_id, proposal_id, emp_id):
        arr = []
        for ans_obj in projans_data:
            proj = ProjectProposalAnswers(question_id=ans_obj.get_question_id(),
                                          answer=ans_obj.get_answer(),
                                          ref_type=DocUtil.proposer,
                                          ref_id=proposal_id,
                                          val_type=ans_obj.get_val_type(),
                                          created_by=emp_id)
            arr.append(proj)

        ProjectProposalAnswers.objects.using(self.schema).bulk_create(arr)

        success_obj = NWisefinSuccess()
        success_obj.set_status("Success")
        success_obj.set_message("Created Successfully")
        return success_obj

    def fetch_projectquestion(self, project_id, proposal_code):
        proposalid=ProposedContract.objects.using(self.schema).filter(code=proposal_code)[0].id
        questions_obj = ProjectQuestions.objects.using(self.schema).filter(project_id=project_id)

        ques_arr = [i.id for i in questions_obj]
        ans_resp = ProjectProposalAnswers.objects.using(self.schema).filter(question__in=ques_arr,
                                                                                           ref_id=proposalid,
                                                                                           ref_type=DocUtil.proposer)

        q_type = list(set([q.q_type for q in questions_obj]))

        resp_list = NWisefinList()
        for j in q_type:
            q_arr = []
            questions = self.get_project_question_by_type(j, questions_obj)
            answer_arr = self.validate_is_answer(j, ans_resp)
            is_answer = True
            if len(answer_arr) == 0:
                is_answer = False

            type=get_projectquestiontype(j)
            for i in questions:
                data_resp = Questionansmapresponse()
                data_resp.set_id(i.id)
                data_resp.set_text(i.text)
                data_resp.set_order(i.order)
                data_resp.ans = self.get_answer(i.id, ans_resp)
                q_arr.append(data_resp)
            d = {"type": type, "questions": q_arr, "is_answer": is_answer}
            resp_list.append(d)

        return resp_list

    def get_answer(self, q_id, ans_obj):
        d = None
        for i in ans_obj:
            if i.question_id == q_id:
                d = {"id": i.id, "answer": i.answer}
        return d

    def get_project_question_by_type(self,typeid,q_obj):
        arr=[i for i in q_obj if i.q_type==typeid]
        return arr
    def validate_is_answer(self,typeid,a_obj):
        arr=[i for i in a_obj if i.question.q_type==typeid]
        return arr
