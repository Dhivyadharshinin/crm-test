from django.utils import timezone
from django.db.models import Q, Max
from cmsservice.data.response.cmsapprovalresponse import ApprovalTranHistoryResponse
from cmsservice.service.cmscommonservice import VowCommonService, CommonService
from cmsservice.service.codegenhistoryservice import Codegenservice, VowCodegenservice
from cmsservice.data.response.proposerreponse import ProposerResponse
from cmsservice.models.cmsmodels import ProposedContract, ProposedContractApprovalTran, \
    ProposedContractHistory, ProposedContractTranComments,ProjectApprovalTran,ProposalAgreement,QuestionClassification,QuestionaireTranComments
from cmsservice.service.projectservice import ProjectService
from cmsservice.util.cmsutil import ApprovalStatus, ActiveStatus, SearchUtil, TranStatus, DocUtil, CodePrefix, \
    TranApproverType, Trantype, ShortlistedTran, is_Closed, CovernoteUtil,UpdateHistoryUtil,HistoryStatus
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.cms_api_service import ApiService


class ProposerService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.CMS_SERVICE)

    #  cms proposal insert
    def create_proposer(self, pr_obj, emp_id, scope):
        if not pr_obj.get_id() is None:
            prop_obj = ProposedContract.objects.using(self._current_app_schema()).filter(id=pr_obj.get_id()).update(
                                                    name=pr_obj.get_name(),
                                                    budget=pr_obj.get_budget(),
                                                    updated_by=emp_id,
                                                    updated_date=timezone.now())
            prop_obj = ProposedContract.objects.using(self._current_app_schema()).get(id=pr_obj.get_id())
        else:
            table_type = CodePrefix.Proposal
            codegen_service = Codegenservice(scope)
            code = codegen_service.codegen(table_type, emp_id)
            prop_obj = ProposedContract.objects.using(self._current_app_schema()).create(
                                                    code=code,
                                                    name=pr_obj.get_name(),
                                                    submitted_date=timezone.now(),
                                                    budget=pr_obj.get_budget(),
                                                    approval_status=ApprovalStatus.DRAFT,
                                                    created_by=emp_id,
                                                    proposer_code=pr_obj.get_proposer_code())
        pr_data = ProposerResponse()
        pr_data.set_id(prop_obj.id)
        pr_data.set_name(prop_obj.name)
        pr_data.set_code(prop_obj.code)
        return prop_obj

    # cms proposal summary
    def fetch_proposer_list(self, vys_page, project_id, request, emp_id):
        condition = Q(proposed__status=ActiveStatus.Active) & \
                    Q(proposed__project_id=project_id) & \
                    Q(status=ActiveStatus.Active) & Q(proposed__project__is_closed=is_Closed.OPEN)& ~Q(proposed__approval_status=ApprovalStatus.DRAFT)

        name = request.GET.get('name')
        shortlist = request.GET.get('shortlist')
        proposer_code = request.GET.get('proposer_code')
        approval_status = request.GET.get('approval_status')

        if name is not None:
            condition &= Q(proposed__name__icontains=name) | Q(proposed__code__icontains=name)
        if proposer_code is not None:
            condition &= Q(proposed__proposer_code__icontains=proposer_code)
        if (shortlist is not None) & (shortlist != ''):
            shortlistt = int(shortlist)
            if shortlistt == ShortlistedTran.shortlisted:
                condition &= Q(proposed__is_shortlisted=True)
            elif shortlistt == ShortlistedTran.finalized:
                condition &= Q(proposed__is_finalized=True)
        if (approval_status is not None) & (approval_status != ''):
            approval_status=int(approval_status)
            if approval_status == SearchUtil.PendingApproval:
                condition &= Q(proposed__approval_status=ApprovalStatus.PENDING) & ~Q(order=0)
            elif approval_status == SearchUtil.FullApproved:
                condition &= Q(proposed__approval_status=ApprovalStatus.APPROVED) & ~Q(order=0)
            elif approval_status == SearchUtil.EVALUATION:
                condition &= Q(proposed__approval_status=ApprovalStatus.EVALUATION) & ~Q(order=0)

        print("proposal - condition ", condition)
        prjlist1 = ProposedContractApprovalTran.objects.filter(condition).values("proposed__id").annotate(id=Max('id')).order_by('-proposed_id')[vys_page.get_offset():vys_page.get_query_limit()]

        arr = [i['id'] for i in prjlist1 ]

        prjlist = ProposedContractApprovalTran.objects.filter(id__in=arr).order_by('-created_date')

        pr_list_data = NWisefinList()
        for prhdr in prjlist:
            pr_data = ProposerResponse()
            pr_data.set_id(prhdr.proposed.id)
            pr_data.set_code(prhdr.proposed.code)
            pr_data.set_name(prhdr.proposed.name)
            pr_data.set_submitted_date(prhdr.proposed.submitted_date)
            pr_data.set_budget(prhdr.proposed.budget)
            pr_data.set_approval_status(prhdr.proposed.approval_status)
            pr_data.set_proposer_code(prhdr.proposed.proposer_code)
            pr_data.set_is_shortlisted(prhdr.proposed.is_shortlisted)
            pr_data.set_is_finalized(prhdr.proposed.is_finalized)
            pr_data.project_id = prhdr.proposed.project_id
            pr_data.is_created = True
            pr_list_data.append(pr_data)
        vpage = NWisefinPaginator(prjlist, vys_page.get_index(), 10)
        pr_list_data.set_pagination(vpage)
        return pr_list_data

    def fetch_proposer(self, pr_id, request):
        # test
        # emp_id=request.employee_id
        # prop_obj = ProposedContract.objects.using(self._current_app_schema()).get(id=pr_id)
        # common_service = CommonService(request.scope)
        # arr=[]
        # prop_data=common_service.obj_to_dict_conversion(prop_obj)
        # resp_id = common_service.insert_update_ref_data(prop_data,prop_obj.id,2,emp_id)
        # ProposedContract.objects.using(self._current_app_schema()).filter(id=pr_id).update(update_refid=resp_id,is_ref=True)
        #
        # return

        type = DocUtil.proposer
        prop_obj = ProposedContract.objects.using(self._current_app_schema()).get(id=pr_id)
        pr_data = ProposerResponse()
        common_service = CommonService(request.scope)
        if prop_obj.is_ref==True:
            prop_update_id=prop_obj.update_refid
            prop_obj=common_service.get_update_ref_data(prop_update_id)

        pr_data.set_id(prop_obj.id)
        pr_data.set_code(prop_obj.code)
        pr_data.set_name(prop_obj.name)
        pr_data.set_submitted_date(prop_obj.submitted_date)
        pr_data.set_budget(prop_obj.budget)
        pr_data.set_approval_status(prop_obj.approval_status)
        pr_data.set_proposer_code(prop_obj.proposer_code)
        pr_data.set_is_shortlisted(prop_obj.is_shortlisted)
        pr_data.set_is_finalized(prop_obj.is_finalized)
        pr_data.is_created = True

        prjlist = ProposedContractHistory.objects.using(self._current_app_schema()).filter(
            history_id=prop_obj.id).order_by('-created_date').values('id', 'version')
        if len(prjlist) != 0:
            prjlist1 = prjlist[0]
            pr_data.version = prjlist1['version']
        else:
            pr_data.version = 1

        apiserv = ApiService(self._scope())
        grup_list = apiserv.grouplist_by_empid(request.employee_id)
        approver = self.get_propsal_approver_list(request, prop_obj.id)
        pending_approver = CommonService(self._scope()).get_pending_grp(grup_list, approver)
        covernote_pr = common_service.covernote_project(prop_obj.id, type)
        execution_pr = common_service.covernote_project(prop_obj.id,CovernoteUtil.proposal_execution)
        financial_pr = common_service.covernote_project(prop_obj.id, CovernoteUtil.proposal_financial)
        attach_pr = common_service.attachement_project(prop_obj.id, type)
        pr_data.covernote = covernote_pr
        pr_data.execution_note = execution_pr
        pr_data.financial_note = financial_pr
        pr_data.filedata = attach_pr
        pr_data.pending_approver = pending_approver
        pr_data.approver = approver
        return pr_data

    def get_propsal_approver_list(self, request, project_id):
        cond = Q(proposed_id=project_id) & Q(status=ActiveStatus.Active) & ~Q(order=0)
        obj = ProposedContractApprovalTran.objects.using(self._current_app_schema()).filter(cond)
        arr = []
        approver_list = [i.to for i in obj if i.to_type == TranApproverType.employee]
        approver_data = ApiService(request.scope).get_multi_emp(request, approver_list)

        approver_grp_list = [i.to for i in obj if i.to_type == TranApproverType.group]
        approver_grp_data = ApiService(request.scope).get_multi_group_info_by_id(approver_grp_list)

        for i in obj:
            resp_obj = ApprovalTranHistoryResponse()
            resp_obj.set_id(i.id)
            resp_obj.set_approver(i.to, i.to_type, approver_data, approver_grp_data)
            resp_obj.set_to_type(i.to_type)
            resp_obj.set_status(i.tran_status)
            resp_obj.set_order(i.order)
            arr.append(resp_obj)
        return arr

    def check_proposer(self, project_id, proposer_code):
        pro = ProposedContract.objects.using(self._current_app_schema()).filter(proposer_code=proposer_code,
                                                                                status=ActiveStatus.Active,
                                                                                project_id=project_id)
        if len(pro) > 0:
            return True
        else:
            return False

    def check_finalizeproposal(self, project_id):
        proposal = ProposedContract.objects.using(self._current_app_schema()).filter(is_finalized=True,
                                                                                is_shortlisted=True,
                                                                                status=ActiveStatus.Active,
                                                                                project_id=project_id)
        if len(proposal) > 0:
            return True
        else:
            return False

    def shortlist_proposer_list(self, vys_page, project_id, request):
        condition = Q(project__status=ActiveStatus.Active) \
                    & Q(project_id=project_id) \
                    & Q(status=ActiveStatus.Active)
        name = request.GET.get('name')
        code = request.GET.get('code')
        proposer_code = request.GET.get('proposer_code')
        if name is not None:
            condition &= Q(proposed__name__icontains=name)
        elif code is not None:
            condition &= Q(proposed__code__icontains=code)
        elif proposer_code is not None:
            condition &= Q(proposed__proposer_code__icontains=proposer_code)
        prjlist = ProposedContract.objects.using(self._current_app_schema()
                                                 ).filter(condition).order_by('-created_date')[
                  vys_page.get_offset():vys_page.get_query_limit()]
        pr_list_data = NWisefinList()
        for prhdr in prjlist:
            pr_data = ProposerResponse()
            pr_data.set_id(prhdr.id)
            pr_data.set_code(prhdr.code)
            pr_data.set_name(prhdr.name)
            pr_data.set_submitted_date(prhdr.submitted_date)
            pr_data.set_budget(prhdr.budget)
            pr_data.set_approval_status(prhdr.approval_status)
            pr_data.set_proposer_code(prhdr.proposer_code)
            pr_data.set_is_shortlisted(prhdr.is_shortlisted)
            pr_data.set_is_finalized(prhdr.is_finalized)
            pr_list_data.append(pr_data)
        vpage = NWisefinPaginator(prjlist, vys_page.get_index(), 10)
        pr_list_data.set_pagination(vpage)
        return pr_list_data

    def proposal_return(self,request,proposal_id,j_data):
        employee_id= request.employee_id
        common_service = CommonService(request.scope)
        remarks= j_data['remarks']

        obj=ProposedContract.objects.using(self._current_app_schema()).get(id=proposal_id)
        # update refid
        data=common_service.obj_to_dict_conversion(obj)
        update_refid=common_service.insert_update_ref_data(data, obj.id, UpdateHistoryUtil.proposal, employee_id)
        #  approval status update
        ProposedContract.objects.using(self._current_app_schema()).filter(id=proposal_id).update(approval_status=ApprovalStatus.REVIEW,updated_by=employee_id,updated_date=timezone.now(),update_refid=update_refid,is_ref=True)

        # history
        ProposedContractTranComments.objects.using(self._current_app_schema()).create(proposed_id=proposal_id,approver=employee_id,comments=remarks,created_by=employee_id,approval_status=ApprovalStatus.REVIEW)

        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.message = "Successfully Returned"
        return success_obj


    # def common_f(self,m_table,id):
    #     m_table.objects.using(self._current_app_schema()).create()

    def proposal_report(self, request, vys_page, proposer_code, emp_id):
        condition = Q(project__status=ActiveStatus.Active) & Q(proposer_code=proposer_code) & Q(status=ActiveStatus.Active)

        prjlist = ProposedContract.objects.using(self._current_app_schema()).filter(condition).order_by(
            '-created_date')[vys_page.get_offset():vys_page.get_query_limit()]

        pr_list_data = NWisefinList()
        for prhdr in prjlist:
            pr_data = ProposerResponse()
            prj_serv = ProjectService(request.scope)
            pr_data.set_id(prhdr.id)
            pr_data.set_project_id(prj_serv.fetch_project(request, prhdr.project_id, emp_id))
            pr_data.set_code(prhdr.code)
            pr_data.set_proposer_code(prhdr.proposer_code)
            pr_data.set_name(prhdr.name)
            pr_data.set_submitted_date(prhdr.submitted_date)
            pr_data.set_budget(prhdr.budget)
            pr_data.set_approval_status(prhdr.approval_status)
            pr_data.entity_id = prhdr.entity_id
            pr_list_data.append(pr_data)
        vpage = NWisefinPaginator(prjlist, vys_page.get_index(), 10)
        pr_list_data.set_pagination(vpage)
        return pr_list_data

    def approved_proposal(self, request, vys_page):
        condition = Q(project__approval_status=ApprovalStatus.APPROVED) & Q(project__status=ActiveStatus.Active)& Q(status=ActiveStatus.Active) & Q(approval_status=ApprovalStatus.APPROVED)

        prjlist = ProposedContract.objects.using(self._current_app_schema()).filter(condition).order_by(
            '-created_date')[vys_page.get_offset():vys_page.get_query_limit()]
        proposal_id =[i.id for i in prjlist]
        prop_agr = ProposalAgreement.objects.using(self._current_app_schema()).filter(proposal_id__in=proposal_id,status=ActiveStatus.Active)
        pr_list_data = NWisefinList()
        for prhdr in prjlist:
            pr_data = ProposerResponse()
            proposal = {"id": prhdr.id, "name": prhdr.name, "proposer_code": prhdr.proposer_code}
            project = {"id": prhdr.project.id, "name": prhdr.project.title, "code": prhdr.project.code}
            pr_data.proposal = proposal
            pr_data.project = project
            # status
            agr=self.get_agreement_project(prhdr.id,prop_agr)
            if agr == None:
                status='Not Issued'
            elif agr.is_accepted ==False:
                status='Pending'
            else:
                status='Accepted'
            pr_data.agreement_status =status
            pr_list_data.append(pr_data)
        vpage = NWisefinPaginator(prjlist, vys_page.get_index(), 10)
        pr_list_data.set_pagination(vpage)
        return pr_list_data

    def get_agreement_project(self,proposal_id,arr):
        for i in arr:
            if i.proposal_id ==proposal_id:
                return i


    def questionary_group_approval(self, proposal_id, data, employee_id):
        type_id = data["type_id"]
        remarks = data["remarks"]
        status = data['status']

        if status not in [ApprovalStatus.APPROVED,ApprovalStatus.REVIEW]:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description("INVAILD APPROVAL STATUS")
            return error_obj

        val_obj=QuestionClassification.objects.using(self._current_app_schema()).filter(classify_id=proposal_id, classify_type=DocUtil.proposer,question_type=type_id)

        if len(val_obj)==0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description("INVAILD TYPE")
            return error_obj

        else:
            if val_obj[0].approval_status ==ApprovalStatus.APPROVED:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description("ALREADY  APPROVED")
                return error_obj

        # approval status
        QuestionClassification.objects.using(self._current_app_schema()).filter(classify_id=proposal_id, classify_type=DocUtil.proposer,question_type=type_id).update(approval_status=status, updated_by=employee_id, updated_date=timezone.now())

        QuestionaireTranComments.objects.using(self._current_app_schema()).create(comments=remarks, proposed_id=proposal_id,approver=employee_id,created_by=employee_id,approval_status=status)

        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.message = SuccessMessage.CREATE_MESSAGE
        return success_obj

from userservice.controller.vowusercontroller import VowUser


class VowProposerService:
    def __init__(self, request):
        vowuser_info = VowUser().get_user(request)

        self.emp_id = vowuser_info['user_id']
        self.is_user = vowuser_info['is_user']
        self.schema = vowuser_info['schema']

    def create_proposer(self, pr_obj, project_id, request):
        if not pr_obj.get_id() is None:
            ProposedContract.objects.using(self.schema).filter(id=pr_obj.get_id()).update(name=pr_obj.get_name(),submitted_date=timezone.now(),budget=pr_obj.get_budget(),updated_by=self.emp_id,updated_date=timezone.now(),is_user=self.is_user)

            prop_obj = ProposedContract.objects.using(self.schema).get(id=pr_obj.get_id())
        else:
            table_type = CodePrefix.Proposal
            codegen_service = VowCodegenservice(request)
            code = codegen_service.vow_codegen(table_type, self.emp_id)

            prop_obj = ProposedContract.objects.using(self.schema).create(project_id=project_id,code=code,name=pr_obj.get_name(),submitted_date=timezone.now(), budget=pr_obj.get_budget(), approval_status=ApprovalStatus.DRAFT,is_vendor=pr_obj.get_is_vendor(),proposer_code=pr_obj.get_proposer_code(), created_by=self.emp_id)

        return prop_obj

    def fetch_proposer_list(self, vys_page, project_id):
        condition = Q(project__status=ActiveStatus.Active) & Q(project_id=project_id) & Q(status=ActiveStatus.Active)

        prjlist = ProposedContract.objects.using(self.schema).filter(condition).order_by(
            '-created_date')[vys_page.get_offset():vys_page.get_query_limit()]

        pr_list_data = NWisefinList()
        for prhdr in prjlist:
            pr_data = ProposerResponse()
            pr_data.set_id(prhdr.id)
            pr_data.set_project_id(prhdr.project_id)
            pr_data.set_code(prhdr.code)
            pr_data.set_name(prhdr.name)
            pr_data.set_submitted_date(prhdr.submitted_date)
            pr_data.set_budget(prhdr.budget)
            pr_data.set_approval_status(prhdr.approval_status)
            pr_data.entity_id = prhdr.entity_id
            pr_list_data.append(pr_data)
        vpage = NWisefinPaginator(prjlist, vys_page.get_index(), 10)
        pr_list_data.set_pagination(vpage)
        return pr_list_data

    def fetch_proposer(self, pr_id, proposer_code, request):
        prop_objl = ProposedContract.objects.using(self.schema).filter(project_id=pr_id,
                                                                       proposer_code=proposer_code,
                                                                       status=ActiveStatus.Active)
        pr_data = ProposerResponse()
        if len(prop_objl) == 0:
            return pr_data
        type = DocUtil.proposer
        prop_obj = prop_objl[0]
        common_service = VowCommonService(request)
        pr_data.set_id(prop_obj.id)
        pr_data.set_project_id(prop_obj.project_id)
        pr_data.set_code(prop_obj.code)
        pr_data.set_name(prop_obj.name)
        pr_data.set_submitted_date(prop_obj.submitted_date)
        pr_data.set_budget(prop_obj.budget)
        pr_data.set_approval_status(prop_obj.approval_status)
        pr_data.entity_id = prop_obj.entity_id
        covernote_pr = common_service.vow_covernote_project(prop_obj.id, type)
        execution_pr = common_service.vow_covernote_project(prop_obj.id, CovernoteUtil.proposal_execution)
        financial_pr = common_service.vow_covernote_project(prop_obj.id, CovernoteUtil.proposal_financial)
        attach_pr = common_service.vow_attachement_project(prop_obj.id, type)
        prjlistt = ProposedContractHistory.objects.using(self.schema).filter(
                                                history_id=prop_obj.id
                                                ).order_by('-created_date'
                                                ).values('id', 'version')
        if len(prjlistt) != 0:
            prjlist1 = prjlistt[0]
            pr_data.version = prjlist1['version']
        else:
            pr_data.version = 1

        pr_data.covernote = covernote_pr
        pr_data.execution_note = execution_pr
        pr_data.financial_note = financial_pr
        pr_data.filedata = attach_pr
        return pr_data

    def vow_check_proposer(self, proposer_code, project_id):
        pro = ProposedContract.objects.using(self.schema).filter(proposer_code=proposer_code,
                                                                 status=ActiveStatus.Active,
                                                                 project_id=project_id)
        if len(pro) > 0:
            return True
        else:
            return False

    def old_proposal_submit(self, project_id, request):
        emp_id = self.emp_id
        proposal_review = request.GET.get('proposal_review')
        proposer_code = request.GET.get('proposer_code')
        proposal_id = request.GET.get('proposal_id')
        print("proposer_review")
        proposal_review=False
        pro = ProposedContract.objects.using(self.schema).filter(project_id=project_id, proposer_code=proposer_code,
                                                                 status=ActiveStatus.Active, id=proposal_id,
                                                                 approval_status=ApprovalStatus.REVIEW)
        if len(pro)!=0:
            proposal_review=True
        if proposal_review == True:
            # pro = ProposedContract.objects.using(self.schema).filter(project_id=project_id, proposer_code=proposer_code,
            #                                                          status=ActiveStatus.Active, id=proposal_id,
            #                                                          approval_status=ApprovalStatus.REVIEW)

            # if len(pro) < 0:
            #     error_obj = NWisefinError()
            #     error_obj.set_code(ErrorMessage.INVALID_DATA)
            #     error_obj.set_description("This Proposal is Not in Review Status. so can't Resumbit")
            #     return
            # & Q(tran_status=TranStatus.reviwed)
            cond = Q(proposed_id=proposal_id) & Q(status=ActiveStatus.Active) & Q(tran_status=Trantype.approver)
            obj = ProposedContractApprovalTran.objects.using(self.schema).filter(cond).order_by('-created_date')

            if obj[0].proposed.parallel_approval:
                edd = obj.index()
                print(edd)

            else:
                index_emp = 0
                user_arr = []
                app_arr = []
                other_arr = []
                for i in obj:
                    ite_emp = i.to
                    ite_tran_status = i.tran_status
                    index_emp = index_emp + 1
                    if (ite_emp == emp_id) & (ite_tran_status == TranStatus.reviwed):
                        user_arr.append(ite_emp)
                        pro = ProposedContractApprovalTran.objects.using(self.schema).filter(to=ite_emp,
                                                                        proposed_id=proposal_id,
                                                                        status=ActiveStatus.Active).update(
                                                                        tran_status=TranStatus.pending,
                                                                        updated_by=self.emp_id,
                                                                        updated_date=timezone.now(),
                                                                        is_user=self.is_user)
                    if (ite_emp != emp_id) & (ite_tran_status == TranStatus.approved):
                        app_arr.append(ite_emp)
                    if (ite_emp != emp_id) & (ite_tran_status != TranStatus.approved):
                        pro = ProposedContractApprovalTran.objects.using(self.schema).filter(to=ite_emp,
                                                                        proposed_id=proposal_id,
                                                                        status=ActiveStatus.Active).update(
                                                                        tran_status=TranStatus.awaiting,
                                                                        updated_by=self.emp_id,
                                                                        updated_date=timezone.now(),
                                                                        is_user=self.is_user)
                        other_arr.append(ite_emp)
            pro = ProposedContract.objects.using(self.schema).filter(project_id=project_id, proposer_code=proposer_code,status=ActiveStatus.Active).update(
                approval_status=ApprovalStatus.EVALUATION,
                updated_by=self.emp_id,
                updated_date=timezone.now(),
                is_user=self.is_user)
            print("pro", pro)
        else:
             pro = ProposedContract.objects.using(self.schema).filter(project_id=project_id, proposer_code=proposer_code,status=ActiveStatus.Active).update(
                approval_status=ApprovalStatus.EVALUATION,
                updated_by=self.emp_id,
                updated_date=timezone.now(),
                is_user=self.is_user)

        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        return success_obj

    def proposal_submit(self, project_id, request):
        emp_id = self.emp_id
        proposal_id = request.GET.get('proposal_id')

        proposal_obj = ProposedContract.objects.using(self.schema).get(id=proposal_id)
        parallel_approval=proposal_obj.parallel_approval
        # proposal_review = False
        # if proposal_obj.approval_status ==ApprovalStatus.REVIEW:
        #     proposal_review=True

        #  approval tran update
        if parallel_approval == True:
            cond = Q(proposed_id=proposal_id) & Q(status=ActiveStatus.Active) & Q(tran_type=Trantype.approver)
            ProposedContractApprovalTran.objects.using(self.schema).filter(cond).update(tran_status=TranStatus.pending)
        else:
            cond = Q(proposed_id=proposal_id) & Q(status=ActiveStatus.Active) & Q(tran_type=Trantype.approver)
            p_cond = cond & Q(order=1)
            ProposedContractApprovalTran.objects.using(self.schema).filter(p_cond).update(
                tran_status=TranStatus.pending)

            c_cond = cond & ~Q(order=1)
            ProposedContractApprovalTran.objects.using(self.schema).filter(c_cond).update(
                tran_status=TranStatus.awaiting)

        # proposal approval status update
        ProposedContract.objects.using(self.schema).filter(id=proposal_id,status=ActiveStatus.Active).update(approval_status=ApprovalStatus.EVALUATION,updated_by=self.emp_id,updated_date=timezone.now(),is_user=self.is_user)

        # tran history
        ProposedContractTranComments.objects.using(self.schema).create(
                                                                       proposed_id=proposal_id,
                                                                       approver=emp_id,
                                                                       created_by=emp_id,
                                                                       is_user=False,
                                                                       approval_status=HistoryStatus.RESUBMITTED)
        # history_serv = VowHistoryService(request)
        # project_version = history_serv.proposalversion_insert(request, proposal_id)
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        return success_obj

    def proposal_tran_create(self,project_id ,proposal_id,):

        to_arr,arr = [],[]
        c=ProposedContractApprovalTran(
            proposed_id=proposal_id, tran_type=Trantype.creator,
            to_type=TranApproverType.employee, to=self.emp_id, order=0,
            tran_status=TranStatus.creator, created_by=self.emp_id, is_user=self.is_user)
        arr.append(c)

        tab=ProjectApprovalTran.objects.using(self.schema).filter(project_id=project_id,tran_type=Trantype.proposal_approver,status=ActiveStatus.Active)

        for i in tab:
            to_arr.append(i.to)

        q_order = 1
        for i in to_arr:
            tran_status = TranStatus.awaiting

            obj = ProposedContractApprovalTran(proposed_id=proposal_id, tran_type=Trantype.approver,to_type=TranApproverType.group, to=i, order=q_order,tran_status=tran_status, created_by=self.emp_id)
            arr.append(obj)
            q_order += 1

        ProposedContractApprovalTran.objects.using(self.schema).bulk_create(arr)

        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.message = SuccessMessage.CREATE_MESSAGE
        return success_obj


    def vow_questionary_resubmit(self,proposal_id, data):
        type_id = data["type_id"]
        remarks = data['remarks']

        val_obj = QuestionClassification.objects.using(self.schema).filter(classify_id=proposal_id,
                                                                                          classify_type=DocUtil.proposer,
                                                                                          question_type=type_id)

        if len(val_obj) == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description("INVAILD TYPE")
            return error_obj

        else:
            if val_obj[0].approval_status != ApprovalStatus.REVIEW:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description("INVAILD  Approval Status")
                return error_obj

        # approval status
        QuestionClassification.objects.using(self.schema()).filter(classify_id=proposal_id,classify_type=DocUtil.proposer,question_type=type_id).update(
            approval_status=ApprovalStatus.PENDING)

        QuestionaireTranComments.objects.using(self.schema()).create(comments=remarks, proposed_id=proposal_id,approver=self.emp_id,created_by=self.emp_id, approval_status=ApprovalStatus.PENDING,is_user=self.is_user)

        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.message = SuccessMessage.CREATE_MESSAGE
        return success_obj

