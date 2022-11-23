import traceback
from django.db.models import Q, Max
from django.utils import timezone
from cmsservice.data.response.projectresponse import ProjectResponse
from cmsservice.data.response.projecttyperesponse import ProjectTypeResponse
from cmsservice.models import Project, ProjectApprovalTran, ProjectType, ProposedContract, ProjectIdentification, \
    ProjectHistory, ProposedContractApprovalTran, ProjectTranComments
from cmsservice.service.cmsapprovalservice import CmsApprovalService
from cmsservice.service.cmscommonservice import VowCommonService, CommonService
from cmsservice.service.codegenhistoryservice import Codegenservice
from cmsservice.service.projectinvitationservice import ProjectInvitationService
from cmsservice.service.projecttypeservice import ProjectTypeService
from cmsservice.util.cmsutil import ActiveStatus, ApprovalStatus, TranStatus, CodePrefix, SearchUtil, \
    is_Closed, DocUtil, TranApproverType, get_viewtype, Trantype, HistoryStatus, CovernoteUtil
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from utilityservice.service.cms_api_service import ApiService, CmsCommonService
# vow class
from userservice.controller.vowusercontroller import VowUser


class ProjectService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.CMS_SERVICE)

    def create_project(self, pr_obj, emp_id, scope):
        if not pr_obj.get_id() is None:
            prhdr = Project.objects.using(self._current_app_schema()).filter(id=pr_obj.get_id()).update(
                title=pr_obj.get_title(),
                type=pr_obj.get_type(),
                submission_end_date=pr_obj.get_submission_end_date(),
                submission_start_date=pr_obj.get_submission_start_date(),
                project_start_date=pr_obj.get_project_start_date(),
                project_end_date=pr_obj.get_project_end_date(),
                budget=pr_obj.get_budget(),
                estimate_currentspent=pr_obj.get_estimate_currentspent(),
                estimate_save=pr_obj.get_estimate_save(),
                commodity_id=pr_obj.get_commodity_id(),
                subcommodity=pr_obj.get_subcommodity(),
                onbehalf_group=pr_obj.get_onbehalf_group(),
                view_type=pr_obj.get_view_type(),
                description=pr_obj.get_description(),
                rel_cat=pr_obj.get_rel_cat(),
                criticality=pr_obj.get_criticality(),
                vendor_type=pr_obj.get_vendor_type(),
                updated_by=emp_id,
                updated_date=timezone.now())
            prhdr = Project.objects.using(self._current_app_schema()).get(id=pr_obj.get_id())
        else:
            approval_status=ApprovalStatus.PENDING
            if pr_obj.get_is_draft() !=None:
                approval_status=ApprovalStatus.DRAFT
            if pr_obj.get_project_identification() != None:
                ProjectIdentification.objects.using(self._current_app_schema()).filter(
                    id=pr_obj.get_project_identification()
                ).update(is_project=True,
                         updated_by=emp_id,
                         updated_date=timezone.now())

            table_type = CodePrefix.Project
            codegen_service = Codegenservice(scope)
            code = codegen_service.codegen(table_type, emp_id)
            prhdr = Project.objects.using(self._current_app_schema()).create(
                type=pr_obj.get_type(),
                title=pr_obj.get_title(),
                submission_start_date=pr_obj.get_submission_start_date(),
                submission_end_date=pr_obj.get_submission_end_date(),
                project_start_date=pr_obj.get_project_start_date(),
                project_end_date=pr_obj.get_project_end_date(),
                budget=pr_obj.get_budget(),
                estimate_currentspent=pr_obj.get_estimate_currentspent(),
                estimate_save=pr_obj.get_estimate_save(),
                commodity_id=pr_obj.get_commodity_id(),
                subcommodity=pr_obj.get_subcommodity(),
                parent_id=pr_obj.get_parent(),
                approval_status=approval_status,
                onbehalf_group=pr_obj.get_onbehalf_group(),
                view_type=pr_obj.get_view_type(),
                description=pr_obj.get_description(),
                rel_cat=pr_obj.get_rel_cat(),
                criticality=pr_obj.get_criticality(),
                vendor_type=pr_obj.get_vendor_type(),
                code=code,
                created_by=emp_id,
                project_identification_id=pr_obj.get_project_identification())

        print("ProjectId while create/update: ", prhdr.id)

        return prhdr

    def project_identification_validation(self, prj_obj):
        idi = ProjectIdentification.objects.using(self._current_app_schema()).filter(
            id=prj_obj.get_project_identification(),
            is_project=False)
        if len(idi) == 0:
            return False

    def fetch_project(self, request, pr_id, emp_id):
        prj = Project.objects.using(self._current_app_schema()).get(id=pr_id)

        projecttype_service = ProjectTypeService(request.scope)
        approval_serv = CmsApprovalService(request.scope)
        common_service = CommonService(request.scope)
        invite_service = ProjectInvitationService(request.scope)
        apiserv = ApiService(request.scope)

        pr_data = ProjectResponse()
        pr_data.set_id(prj.id)
        pr_data.set_code(prj.code)
        pr_data.set_title(prj.title)
        pr_data.set_budget(prj.budget)
        pr_data.set_type(projecttype_service.fetch_projecttype(prj.type))
        pr_data.set_code(prj.code)
        pr_data.set_title(prj.title)
        pr_data.set_description(prj.description)
        pr_data.set_project_start_date(prj.project_start_date)
        pr_data.set_submission_start_date(prj.submission_start_date)
        pr_data.set_project_end_date(prj.project_end_date)
        pr_data.set_submission_end_date(prj.submission_end_date)
        pr_data.set_parent(prj.parent)
        pr_data.set_approval_status(prj.approval_status)
        pr_data.set_is_closed(prj.is_closed)
        pr_data.set_is_user(prj.is_user)
        pr_data.set_commodity_id(apiserv.get_commodity_id(prj.commodity_id))
        pr_data.set_subcommodity(prj.subcommodity)
        pr_data.set_estimate_currentspent(prj.estimate_currentspent)
        pr_data.set_estimate_save(prj.estimate_save)
        pr_data.set_onbehalf_group(apiserv.get_group_info_by_id(prj.onbehalf_group))
        pr_data.set_view_type(get_viewtype(prj.view_type))
        pr_data.set_rel_cat(apiserv.get_rel_cat(prj.rel_cat))
        pr_data.set_criticality(apiserv.get_criticality(prj.criticality))
        pr_data.set_vendor_type(apiserv.get_vendor_type(prj.vendor_type))
        pr_data.entity_id = prj.entity_id
        if prj.created_by == emp_id:
            pr_data.is_created_by = True
        else:
            pr_data.is_created_by = False

        type = DocUtil.project
        covernote_pr = common_service.covernote_project(prj.id, type)
        strategy_note = common_service.covernote_project(prj.id, CovernoteUtil.project_strategy)
        attach_pr = common_service.attachement_project(prj.id, type)
        invite_pr = invite_service.invitation_project(prj.id)
        pr_data.covernote = covernote_pr
        pr_data.strategy_note = strategy_note
        pr_data.filedata = attach_pr
        pr_data.invitation = invite_pr

        approver_list = approval_serv.get_project_approver_list(request, prj.id)
        approver = approver_list["approver"]
        emp_grp = apiserv.grouplist_by_empid(emp_id)
        pending_approve = CommonService(request.scope).get_pending_grp(emp_grp, approver)

        pr_data.approver = approver
        pr_data.collabator = approver_list["collabator"]
        pr_data.q_approver = approver_list["q_approver"]
        pr_data.pending_approver = pending_approve

        # latest version
        prjlist = ProjectHistory.objects.using(self._current_app_schema()).filter(
            history_id=prj.id).order_by(
            '-created_date').values(
            'id', 'version')
        if len(prjlist)!=0:
            prjlist1 = prjlist[0]
            pr_data.version = prjlist1['version']
        else:
            pr_data.version = 1
        return pr_data

    def delete_project(self, project_id, emp_id):
        project = Project.objects.using(self._current_app_schema()).filter(id=project_id).update(
            status=ActiveStatus.Delete,
            updated_by=emp_id,
            updated_date=timezone.now())
        if project[0] == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_PROJECT_ID)
            error_obj.set_description(ErrorDescription.INVALID_PROJECT_ID)
            return error_obj
        else:
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.DELETE_MESSAGE)
            return success_obj

    # updateprojectclose
    def updateprojectclose(self, project_id, emp_id):
        try:
            project = Project.objects.using(self._current_app_schema()).filter(id=project_id).update(
                is_closed=1,
                updated_by=emp_id,
                updated_date=timezone.now())
            print("pro", project)
            if project == 0:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_PROJECT_ID)
                error_obj.set_description(ErrorDescription.INVALID_PROJECT_ID)
                return error_obj
            else:
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.message = "Successfully Closed"
                return success_obj
        except Exception as e:
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(e))
            return error_obj

    def fetch_project_list(self, scope, vys_page, emp_id, request):
        condition = Q(project__status=ActiveStatus.Active)
        approval_status = request.GET.get('approval_status')
        ref_type = request.GET.get('ref_type', str(DocUtil.project))
        is_closed = request.GET.get('is_closed')
        title = request.GET.get('title')
        code = request.GET.get('code')
        projecttype = request.GET.get('projecttype')
        submission_start_date = request.GET.get('submission_start_date')
        submission_end_date = request.GET.get('submission_end_date')
        commodity_id = request.GET.get('commodity_id')
        # is_closed
        if (is_closed is not None) & (is_closed != ''):
            if int(is_closed) == 1:
                isClosed = True
            else:
                isClosed = False
            condition &= Q(project__is_closed=isClosed)
        else:
            isClosed = False
            condition &= Q(project__is_closed=isClosed)
        apiserv = ApiService(scope)
        emp_group = apiserv.grouplist_by_empid(emp_id)
        # approval_status for project
        if (approval_status is not None) & (approval_status != '') & (ref_type == str(DocUtil.project)):
            approval_status = int(approval_status)
            if approval_status == SearchUtil.PendingApproval:
                condition &= ((Q(tran_status=TranStatus.pending) & Q(to=emp_id) & Q(
                    to_type=TranApproverType.employee)) | (Q(tran_status=TranStatus.pending) & Q(to__in=emp_group) & Q(
                    to_type=TranApproverType.group))) & ~Q(project__created_by=emp_id)
            elif approval_status == SearchUtil.CreatedByMe:
                condition &= Q(tran_status=TranStatus.creator) & Q(project__created_by=emp_id)
            elif approval_status==SearchUtil.Draft:
                condition &= Q(project__approval_status=ApprovalStatus.DRAFT) & Q(project__created_by=emp_id)
            elif approval_status == SearchUtil.ApprovedByMe:
                condition &= Q(tran_status=TranStatus.approved) & Q(updated_by=emp_id)
            elif approval_status == SearchUtil.RejectedByMe:
                condition &= Q(tran_status=TranStatus.rejected) & Q(updated_by=emp_id)
            elif approval_status == SearchUtil.FullApproved:
                condition &= Q(tran_status=TranStatus.approved) & Q(
                    project__approval_status=ApprovalStatus.APPROVED) & Q(order=1)
            elif approval_status == SearchUtil.collaborator:
                condition &= Q(order=0) & Q(tran_type=Trantype.collaborator) & Q(to__in=emp_group)
            else:
                condition &= Q(project__status=-1)

        #  approval status for proposal
        elif (approval_status is not None) & (approval_status != '') & (ref_type == str(DocUtil.proposer)):
            approval_status = int(approval_status)
            condition1 = condition
            if approval_status == SearchUtil.PendingApproval:
                condition1 &= ((Q(tran_status=TranStatus.pending) & Q(to=emp_id) & Q(
                    to_type=TranApproverType.employee)) | (Q(tran_status=TranStatus.pending) & Q(to__in=emp_group) & Q(
                    to_type=TranApproverType.group))) & ~Q(proposed__proposer__created_by=emp_id)
            elif approval_status == SearchUtil.CreatedByMe:
                condition1 &= Q(tran_status=TranStatus.creator) & Q(to=emp_id)
            elif approval_status == SearchUtil.ApprovedByMe:
                condition1 &= Q(tran_status=TranStatus.approved) & Q(updated_by=emp_id)
            elif approval_status == SearchUtil.RejectedByMe:
                condition1 &= Q(tran_status=TranStatus.rejected) & Q(updated_by=emp_id)
            elif approval_status == SearchUtil.FullApproved:
                condition1 &= Q(tran_status=TranStatus.approved) & Q(
                    project__approval_status=ApprovalStatus.APPROVED) & Q(order=1)
            elif approval_status == SearchUtil.collaborator:
                condition1 &= Q(order=0) & Q(tran_type=Trantype.collaborator) & Q(to__in=emp_group)
            else:
                condition1 &= Q(project__status=-1)

            prj_idl_list = ProposedContractApprovalTran.objects.using(self._current_app_schema()).filter(
                condition1).values_list('proposed__project_id').order_by(
                '-created_date')[vys_page.get_offset():vys_page.get_query_limit()]

            condition &= Q(project_id__in=prj_idl_list)

        else:
            condition &= (Q(tran_status=TranStatus.pending) & Q(to=emp_id) & Q(to_type=TranApproverType.employee)) | (
                        Q(tran_status=TranStatus.pending) & Q(to__in=emp_group) & Q(
                    to_type=TranApproverType.group)) & ~Q(project__created_by=emp_id)

        # code, title, projecttype, date
        if (title is not None) & (title != ''):
            condition &= Q(project__title__icontains=title)
        if (code is not None) & (code != ''):
            condition &= Q(project__code__icontains=code)
        if (projecttype is not None) & (projecttype != ''):
            condition &= Q(project__type=projecttype)
        if (commodity_id is not None) & (commodity_id != ''):
            condition &= Q(project__commodity_id=commodity_id)
        if (submission_start_date is not None) & (submission_start_date != ''):
            condition &= Q(submission_start_date__range=(submission_start_date, submission_end_date))
        print("project - condition ", condition)
        # prjlist = ProjectApprovalTran.objects.using(self._current_app_schema()).filter(condition).order_by(
        #     '-created_date')[vys_page.get_offset():vys_page.get_query_limit()]

        # tran_arr = ProjectApprovalTran.objects.filter(condition).values_list('project', flat=True).order_by(
        #     '-project__id').distinct()[vys_page.get_offset():vys_page.get_query_limit()]
        # tran_arr = list(tran_arr)
        #
        # condition = Q(id__in=tran_arr)
        # prjlist = ProjectApprovalTran.objects.filter(condition).order_by('-created_date')
        prjlist1=ProjectApprovalTran.objects.filter(condition).values("project__id").annotate(id=Max('id')).order_by('-project_id')[vys_page.get_offset():vys_page.get_query_limit()]
        arr=[]
        for i in prjlist1:
            arr.append(i["id"])
        prjlist=ProjectApprovalTran.objects.filter(id__in=arr).order_by('-created_date')


        # print(prjlist.query)
        list_length = len(prjlist)
        print(list_length)
        type_arr = [i.project.type for i in prjlist]
        project_identificationtype_service = ProjectTypeService(scope)
        type_data = project_identificationtype_service.get_projecttype_info(type_arr)
        pr_list_data = NWisefinList()
        projecttype_service = ProjectTypeService(scope)
        for prhdr in prjlist:
            pr_data = ProjectResponse()
            pr_data.set_id(prhdr.project_id)
            pr_data.set_projecttype(prhdr.project.type, type_data)
            pr_data.set_code(prhdr.project.code)
            pr_data.set_title(prhdr.project.title)
            pr_data.set_submission_start_date(prhdr.project.submission_start_date)
            pr_data.set_submission_end_date(prhdr.project.submission_end_date)
            pr_data.set_project_start_date(prhdr.project.project_start_date)
            pr_data.set_project_end_date(prhdr.project.project_end_date)
            pr_data.set_budget(prhdr.project.budget)
            pr_data.set_parent(prhdr.project.parent)
            pr_data.set_approval_status(prhdr.project.approval_status)
            pr_data.set_is_user(prhdr.project.is_user)
            pr_data.set_commodity_id(apiserv.get_commodity_id(prhdr.project.commodity_id))
            pr_data.set_subcommodity(prhdr.project.subcommodity)
            # pr_data.set_cat_id(prhdr.project.cat_id)
            # pr_data.set_subcat_id(prhdr.project.subcat_id)
            pr_data.set_onbehalf_group(prhdr.project.onbehalf_group)
            pr_data.set_description(prhdr.project.description)

            if prhdr.project.is_closed == is_Closed.OPEN:
                pr_data.set_is_closed(is_Closed.OPEN_Type)
            elif prhdr.project.is_closed == is_Closed.CLOSED:
                pr_data.set_is_closed(is_Closed.CLOSED_Type)

            pr_list_data.append(pr_data)
        vpage = NWisefinPaginator(prjlist, vys_page.get_index(), 10)
        pr_list_data.set_pagination(vpage)
        return pr_list_data

    def get_project(self, id):
        condition = Q(approval_status=1) & Q(status=ActiveStatus.Active) & Q(id=id)
        prjlist = Project.objects.using(self._current_app_schema()).filter(condition)
        prjlist = prjlist[0]
        return prjlist.submission_start_date

    def project_parallel_app(self, product_id, employee_id):
        proj_ide_tab = Project.objects.using(self._current_app_schema()).filter(id=product_id, approval_status=ApprovalStatus.APPROVED
                                              )
        if len(proj_ide_tab) != 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description("INVAILD APPROVER")
            return error_obj

        proj_ide_tab1 = Project.objects.using(self._current_app_schema()).filter(id=product_id, created_by=employee_id)
        proj_ide_tab2 = Project.objects.using(self._current_app_schema()).filter(id=product_id, parallel_approval=False)
        if len(proj_ide_tab1) == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description("INVAILD APPROVER")
            return error_obj
        if len(proj_ide_tab2) == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description("INVAILD APPROVER")
            return error_obj

        proj_ide_t1 = ProjectApprovalTran.objects.using(self._current_app_schema()).filter(project_id=product_id, tran_status=TranStatus.awaiting
                                                         ).update(
            tran_status=TranStatus.pending,
            updated_by=employee_id,
            updated_date=timezone.now()
        )
        proj_ide_t2 = Project.objects.using(self._current_app_schema()).filter(id=product_id).update(parallel_approval=True,
                                                                   updated_by=employee_id,
                                                                   updated_date=timezone.now()
                                                                   )

        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)

        success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        return success_obj

    # def checkproject_status(self, project_id):
    #     condition = Q(is_closed=False) & Q(status=ActiveStatus.Active) & Q(id=project_id)
    #     prjlist = Project.objects.using(self._current_app_schema()).filter(condition)
    #     prjlist = prjlist[0]
    #     # dt = get_approvalstatus(prjlist.approval_status)
    #     if (prjlist.approval_status == ApprovalStatus.DRAFT) | (prjlist.approval_status == ApprovalStatus.REVIEW):
    #         resp = True
    #     else:
    #         resp = False
    #     data = {"project_status": prjlist.approval_status, "status": resp}
    #     return data

    def project_resubmit(self, project_id, employee_id):
        proj_ide = Project.objects.using(self._current_app_schema()).filter(id=project_id)
        if proj_ide[0].approval_status != ApprovalStatus.REVIEW:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description("CAN'T RESUBMIT")
            return error_obj
        if proj_ide[0].created_by != employee_id:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description("CAN'T RESUBMIT")
            return error_obj
        proj_ide.update(approval_status=ApprovalStatus.PENDING)
        ProjectApprovalTran.objects.using(self._current_app_schema()).filter(project_id=project_id, tran_status=TranStatus.reviwed).update(
            tran_status=TranStatus.pending, updated_by=employee_id, updated_date=timezone.now())
        if proj_ide[0].parallel_approval !=True:
            condition=Q(project_id=project_id)
            condition&=~Q(order=0)
            condition&=~Q(order=1)
            ProjectApprovalTran.objects.using(self._current_app_schema()).filter(
                project_identification_id=project_id, order=1).update(
                tran_status=TranStatus.pending, updated_by=employee_id, updated_date=timezone.now())
            ProjectApprovalTran.objects.using(self._current_app_schema()).filter(
                condition).update(
                tran_status=TranStatus.awaiting, updated_by=employee_id, updated_date=timezone.now())
        else:
            condition = Q(project_id=project_id)
            condition &= ~Q(order=0)
            ProjectApprovalTran.objects.using(self._current_app_schema()).filter(
                condition).update(
                tran_status=TranStatus.pending, updated_by=employee_id, updated_date=timezone.now())
        ProjectTranComments.objects.using(self._current_app_schema()).create(rel_id=project_id,
                                                                             rel_type=DocUtil.project,
                                                                             approver=employee_id,
                                                                             comments=None, created_by=employee_id,
                                                                             created_date=timezone.now(),
                                                                             approval_status=HistoryStatus.RESUBMITTED)
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        return success_obj


class VowProjectService:
    def __init__(self, request):
        vowuser_info = VowUser().get_user(request)

        self.emp_id = vowuser_info['user_id']
        self.is_user = vowuser_info['is_user']
        self.schema = vowuser_info['schema']

    def summary_vowproject(self, vys_page, request):
        print("requ", request)
        proposer_code = request.GET.get('proposer_code')
        if (proposer_code is None) | (proposer_code is ''):
            condition = Q(status=ActiveStatus.Active) & \
                        Q(approval_status=ApprovalStatus.APPROVED) \
                        & Q(is_closed=0)
                        # (Q(submission_start_date__gte=timezone.now()) & Q(submission_end_date__lte=timezone.now()))
        else:
            pro = ProposedContract.objects.using(self.schema).filter(status=ActiveStatus.Active,
                                                                     proposer_code=proposer_code
                                                                     ).values_list('project_id', flat=True)
            condition = Q(status=ActiveStatus.Active) & \
                        Q(approval_status=ApprovalStatus.APPROVED) \
                        & Q(is_closed=0) & Q(id__in=pro)
        title = request.GET.get('title')
        if title is not None:
            condition &= Q(title__icontains=title) | Q(code__icontains=title)

        print("project - condition ", condition)
        prjlist = Project.objects.using(self.schema).filter(condition).order_by('-created_date')[
                  vys_page.get_offset():vys_page.get_query_limit()]
        pr_list_data = NWisefinList()
        prj_arr = []
        for prhdr in prjlist:
            prj_arr.append(prhdr.id)
        print("prj_arr", prj_arr)
        prop_prj_id = self.check_prj(prj_arr, proposer_code)
        print("prop_prj_id", prop_prj_id)
        for prhdr in prjlist:
            print("prjj", prhdr.id)
            if (proposer_code is None) | (proposer_code is ''):
                is_applied = False
            elif prhdr.id in prop_prj_id:
                is_applied = True
            else:
                is_applied = False
            pr_data = ProjectResponse()
            pr_data.set_id(prhdr.id)
            pr_data.set_code(prhdr.code)
            pr_data.set_title(prhdr.title)
            pr_data.set_description(prhdr.description)
            pr_data.set_submission_start_date(prhdr.submission_start_date)
            pr_data.set_submission_end_date(prhdr.submission_end_date)
            pr_data.set_is_user(prhdr.is_user)
            pr_data.entity_id = prhdr.entity_id
            pr_data.is_applied = is_applied
            pr_list_data.append(pr_data)
        vpage = NWisefinPaginator(prjlist, vys_page.get_index(), 10)
        pr_list_data.set_pagination(vpage)
        return pr_list_data

    def check_prj(self, project_arr, proposer_code):
        pro = ProposedContract.objects.using(self.schema
                                    ).filter(status=ActiveStatus.Active,
                                            project_id__in=project_arr,
                                            proposer_code=proposer_code).values_list('project_id', flat=True)
        return pro


    def fetch_projecttype(self, projectty_id):
        try:
            projectty = ProjectType.objects.using(self.schema).get(id=projectty_id)
            projectty_data = ProjectTypeResponse()
            projectty_data.set_id(projectty.id)
            projectty_data.set_name(projectty.name)
            projectty_data.set_code(projectty.code)
            return projectty_data
        except:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_PROJECTTYPE_ID)
            error_obj.set_description(ErrorDescription.INVALID_PROJECTTYPE_ID)
            return error_obj

    def fetch_vowproject(self, project_id, request):
        proposer_code = request.GET.get('proposer_code')
        if (proposer_code is not None) & (proposer_code is not ''):
            pro = ProposedContract.objects.using(self.schema).filter(
                status=ActiveStatus.Active,
                project_id=project_id,
                proposer_code=proposer_code)
            if len(pro) > 0:
                is_applied = True
            else:
                is_applied = False
        else:
            is_applied = False
        type = DocUtil.project
        prj = Project.objects.using(self.schema).get(id=project_id)
        common_service = VowCommonService(request)
        apiserv = CmsCommonService(request)
        pr_data = ProjectResponse()
        pr_data.set_id(prj.id)
        pr_data.set_type(prj.type)
        pr_data.set_code(prj.code)
        pr_data.set_title(prj.title)
        pr_data.set_type(self.fetch_projecttype(prj.type))
        pr_data.set_code(prj.code)
        pr_data.set_title(prj.title)
        pr_data.set_project_start_date(prj.project_start_date)
        pr_data.set_submission_start_date(prj.submission_start_date)
        pr_data.set_project_end_date(prj.project_end_date)
        pr_data.set_submission_end_date(prj.submission_end_date)
        pr_data.set_parent(prj.parent)
        pr_data.set_is_user(prj.is_user)
        pr_data.set_description(prj.description)
        pr_data.set_commodity_id(apiserv.vow_get_commodity_id(prj.commodity_id))
        pr_data.set_subcommodity(prj.subcommodity)
        pr_data.entity_id = prj.entity_id
        covernote_pr = common_service.vow_covernote_project(prj.id, type)
        attach_pr = common_service.vow_attachement_project(prj.id, type)
        pr_data.covernote = covernote_pr
        pr_data.filedata = attach_pr
        pr_data.is_applied = is_applied

        prjlist = ProjectHistory.objects.using(self.schema).filter(
            history_id=prj.id).order_by(
            '-created_date').values(
            'id', 'version')
        if len(prjlist)!=0:
            prjlist1 = prjlist[0]
            pr_data.version = prjlist1['version']
        else:
            pr_data.version = 1
        return pr_data
