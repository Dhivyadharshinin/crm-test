import json
from ast import literal_eval
from django.db.models import Q

from cmsservice.data.response.cmsapprovalresponse import ApprovalTranHistoryResponse
from cmsservice.data.response.projectresponse import ProjectResponse, VersionHistoryResponse
from cmsservice.data.response.proposerreponse import ProposerResponse
from cmsservice.models import ProjectHistory, ProposedContractHistory, CMSDocumentsHistory, CMSCovernoteHistory, \
    Project, CMSVersionHistory
from cmsservice.service.cmsapprovalservice import CmsApprovalService
from cmsservice.service.cmscommonservice import CommonService, VowCommonService
from cmsservice.service.projectinvitationservice import ProjectInvitationService
from cmsservice.service.projecttypeservice import ProjectTypeService
from cmsservice.util.cmsutil import ActiveStatus, DocUtil, get_viewtype, CovernoteUtil, conversion, VersionDataType, \
    TranApproverType, Trantype
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.cms_api_service import ApiService
from utilityservice.service.threadlocal import NWisefinThread
from django.utils import timezone


class Historyservice(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.CMS_SERVICE)

    def projecthstry(self, prhdr, history_id):
        projecthsty = ProjectHistory.objects.using(self._current_app_schema()).filter(history_id=history_id).order_by(
            '-created_date')
        if len(projecthsty) > 0:
            projecthsty = projecthsty[0]
            version = int(projecthsty.version) + 1
        else:
            version = 1
        project = ProjectHistory.objects.using(self._current_app_schema()).create(
            history_id=history_id,
            code=prhdr.code,
            title=prhdr.title,
            type=prhdr.type,
            submission_start_date=prhdr.submission_start_date,
            submission_end_date=prhdr.submission_end_date,
            project_start_date=prhdr.project_start_date,
            project_end_date=prhdr.project_end_date,
            budget=prhdr.budget,
            onbehalf_group=prhdr.onbehalf_group,
            parent_id=prhdr.parent_id,
            view_type=prhdr.view_type,
            description=prhdr.description,
            version=version,
            commodity_id=prhdr.commodity_id,
            subcommodity=prhdr.subcommodity,
            estimate_currentspent=prhdr.estimate_currentspent,
            estimate_save=prhdr.estimate_save,
            rel_cat=prhdr.rel_cat,
            criticality=prhdr.criticality,
            vendor_type=prhdr.vendor_type,
            created_by=prhdr.created_by,
            created_date=timezone.now())
        return project

    def proposalhstry(self, prop_obj, history_id, project_id):
        projecthsty = ProposedContractHistory.objects.using(self._current_app_schema()).filter(
            history_id=history_id).order_by('-created_date')
        if len(projecthsty) > 0:
            projecthsty = projecthsty[0]
            version = int(projecthsty.version) + 1
        else:
            version = 1
        proposal = ProposedContractHistory.objects.using(self._current_app_schema()).create(
            history_id=history_id,
            project_id=project_id,
            code=prop_obj.code,
            name=prop_obj.name,
            submitted_date=prop_obj.submitted_date,
            budget=prop_obj.budget,
            proposer_code=prop_obj.proposer_code,
            is_vendor=prop_obj.is_vendor,
            version=version,
            created_by=prop_obj.created_by,
            created_date=timezone.now())
        return proposal

    def cmsdochstry(self, cmsdoc_obj, prjtid):
        for d_j in cmsdoc_obj:
            cmsdoc = CMSDocumentsHistory.objects.using(self._current_app_schema()).create(
                rel_id=prjtid,
                rel_type=d_j.rel_type,
                file_id=d_j.file_id,
                gen_file_name=d_j.gen_file_name,
                file_name=d_j.file_name,
                type=-1,
                created_by=d_j.created_by,
                created_date=timezone.now())

    def cmscvrhstry(self, cmsdoc_obj, prjtid):
        cmsdoc = CMSCovernoteHistory.objects.using(self._current_app_schema()).create(
            rel_id=prjtid,
            rel_type=cmsdoc_obj.rel_type,
            note=cmsdoc_obj.note,
            created_by=cmsdoc_obj.created_by,
            created_date=timezone.now())
        return cmsdoc

    # project version
    def project_viewsummary(self, request, project_id, scope, emp_id):
        history_id = request.GET.get('history_id')
        if (history_id is not None) & (history_id != ''):
            condition = Q(status=ActiveStatus.Active) & Q(history_id=project_id) & Q(id=history_id)
        else:
            condition = Q(status=ActiveStatus.Active) & Q(history_id=project_id)

        print("project - condition ", condition)
        prj = ProjectHistory.objects.using(self._current_app_schema()).get(condition)
        type = DocUtil.project
        pr_data = ProjectResponse()
        projecttype_service = ProjectTypeService(scope)
        common_service = CommonService(scope)
        apiserv = ApiService(scope)

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

        pr_data.version = prj.version

        covernote_pr = common_service.covernotehistory_project(project_id, CovernoteUtil.project)
        pr_data.covernote = covernote_pr

        strategy_note = common_service.covernotehistory_project(project_id, CovernoteUtil.project_strategy)
        pr_data.strategy_note = strategy_note

        attach_pr = common_service.attachementhistory_project(project_id, type)
        pr_data.filedata = attach_pr

        ref_type = DocUtil.project
        #
        prj_invite_type = VersionDataType.ProjectInvitation
        prj_inv = self.version_get(project_id, ref_type, prj.version, prj_invite_type)
        print("prj_inv", prj_inv)
        invi_arr = []
        for invi in prj_inv:
            invi_arr.append(invi.data)
        pr_data.invitation = invi_arr

        #
        prj_coll_type = VersionDataType.ProjectCollaborator
        prj_coll = self.get_project_history_list(request, project_id, ref_type, prj.version, prj_coll_type)
        pr_data.collabator = prj_coll["collabator"]

        #
        prj_app_type = VersionDataType.ProjectApprover
        prj_app = self.get_project_history_list(request, project_id, ref_type, prj.version, prj_app_type)
        approver = prj_app["approver"]
        pr_data.approver = approver

        emp_grp = ApiService(request.scope).grouplist_by_empid(emp_id)
        pending_approve = CommonService(scope).get_pending_grp(emp_grp, prj_app["approver"])
        pr_data.pending_approver = pending_approve

        #
        prpo_app_type = VersionDataType.ProposalApprover
        prpo_app = self.get_project_history_list(request, project_id, ref_type, prj.version, prpo_app_type)
        pr_data.q_approver = prpo_app["q_approver"]

        prjt = Project.objects.using(self._current_app_schema()).get(id=project_id)
        pr_data.set_approval_status(prjt.approval_status)
        pr_data.set_is_closed(prjt.is_closed)
        return pr_data

    def proposal_viewsummary(self, request, vys_page, proposal_id):
        history_id = request.GET.get('history_id')
        type = DocUtil.proposer
        scope = request.scope
        if (history_id is not None) & (history_id != ''):
            condition = Q(status=ActiveStatus.Active) & Q(history_id=proposal_id) & Q(id=history_id)
        else:
            condition = Q(status=ActiveStatus.Active) & Q(history_id=proposal_id)
        print("project - condition ", condition)

        prlist = ProposedContractHistory.objects.using(self._current_app_schema()).filter(condition).order_by(
            '-created_date')[vys_page.get_offset():vys_page.get_query_limit()]
        list_length = len(prlist)
        print(list_length)
        pr_list_data = NWisefinList()
        common_service = CommonService(scope)
        for prhdr in prlist:
            pr_data = ProposerResponse()
            pr_data.set_id(prhdr.id)
            pr_data.set_code(prhdr.code)
            pr_data.set_name(prhdr.name)
            pr_data.set_submitted_date(prhdr.submitted_date)
            pr_data.set_budget(prhdr.budget)
            pr_data.set_proposer_code(prhdr.proposer_code)
            pr_data.version_date = str(prhdr.created_date)
            pr_data.version = prhdr.version
            pr_data.set_is_shortlisted(prhdr.is_shortlisted)
            pr_data.set_is_finalized(prhdr.is_finalized)
            covernote_pr = common_service.covernotehistory_project(prhdr.id, type)
            attach_pr = common_service.attachementhistory_project(prhdr.id, type)
            pr_data.covernote = covernote_pr
            pr_data.filedata = attach_pr

            pr_list_data.append(pr_data)
        vpage = NWisefinPaginator(prlist, vys_page.get_index(), 10)
        pr_list_data.set_pagination(vpage)
        return pr_list_data

    def proposal_version(self, proposal_id):
        condition = Q(status=ActiveStatus.Active) & Q(history_id=proposal_id)
        prlist = ProposedContractHistory.objects.using(self._current_app_schema()).filter(condition)
        list_length = len(prlist)
        print(list_length)
        pr_list_data = NWisefinList()
        for prhdr in prlist:
            pr_data = ProposerResponse()
            pr_data.set_id(prhdr.id)
            pr_data.version_date = str(prhdr.created_date)
            pr_data.version = "Version " + str(prhdr.version)
            pr_list_data.append(pr_data)
        return pr_list_data

    def project_version(self, project_id):
        condition = Q(status=ActiveStatus.Active) & Q(history_id=project_id)
        prlist = ProjectHistory.objects.using(self._current_app_schema()).filter(condition)
        list_length = len(prlist)
        print(list_length)
        pr_list_data = NWisefinList()
        for prhdr in prlist:
            pr_data = ProposerResponse()
            pr_data.set_id(prhdr.id)
            pr_data.version_date = str(prhdr.created_date)
            pr_data.version = "Version " + str(prhdr.version)
            pr_list_data.append(pr_data)
        return pr_list_data

    # common version history insert
    def version_history(self, ref_id, ref_type, data, data_type, emp_id):
        print("version data i/p: ", data)
        vhsrty = CMSVersionHistory.objects.using(self._current_app_schema()).filter(
                                                ref_id=ref_id,
                                                ref_type=ref_type,
                                                data_type=data_type,
                                                status=ActiveStatus.Active).order_by('-created_date')
        if len(vhsrty) > 0:
            versionhsrty = vhsrty[0]
            version = int(versionhsrty.version) + 1
        else:
            version = 1
        for versionhstry in data:
            if "_state" in versionhstry:
                print("delete")
                del versionhstry['_state']
            if "created_date" in versionhstry:
                versionhstry['created_date'] = conversion(versionhstry['created_date'])
            if "updated_date" in versionhstry:
                versionhstry['updated_date'] = conversion(versionhstry['updated_date'])
            print("after convsn version data i/p: ", versionhstry)
            versioncr = CMSVersionHistory.objects.using(self._current_app_schema()).create(
                version=version,
                ref_id=ref_id,
                ref_type=ref_type,
                data=versionhstry,
                data_type=data_type,
                created_by=emp_id,
                created_date=timezone.now())
        success_obj = NWisefinSuccess()
        success_obj.set_status("Success")
        success_obj.set_message("Success")
        return success_obj

    # common version history get
    def version_get(self, ref_id, ref_type, version, data_type):
        condition = Q(status=ActiveStatus.Active) & Q(ref_id=ref_id) & Q(ref_type=ref_type) & Q(data_type=data_type) & Q(version=version)
        print("project - condition ", condition)
        vhsrty_dt = CMSVersionHistory.objects.using(self._current_app_schema()).filter(condition)
        v_list = []
        for vhsrty in vhsrty_dt:
            vhstry_data = VersionHistoryResponse()
            # vhstry_data.set_id(vhsrty.id)
            # vhstry_data.set_ref_id(vhsrty.ref_id)
            # vhstry_data.set_ref_type(vhsrty.ref_type)
            # vhstry_data.set_version(vhsrty.version)
            all_data = vhsrty.data
            data = all_data.replace("'", "\"")
            print("replaced", data)
            group_data = literal_eval(data)
            vhstry_data.set_data(group_data)
            vhstry_data.set_data_type(vhsrty.data_type)
            v_list.append(vhstry_data)
        return v_list

    # version history insert for approvaltran
    def get_project_history_list(self, request, project_id, ref_type, version, data_type):
        prj_data = self.version_get(project_id, ref_type, version, data_type)

        approver_arr, collabator_arr, q_approver_arr = [], [], []
        approver_list = [i.data['to'] for i in prj_data if i.data['to_type'] == TranApproverType.employee]
        approver_data = ApiService(request.scope).get_multi_emp(request, approver_list)

        approver_grp_list = [i.data['to'] for i in prj_data if i.data['to_type'] == TranApproverType.group]
        approver_grp_data = ApiService(request.scope).get_multi_group_info_by_id(approver_grp_list)
        dictt = {}

        for i in prj_data:
            resp_obj = ApprovalTranHistoryResponse()
            resp_obj.set_id(i.id)
            resp_obj.set_approver(i.data['to'], i.data['to_type'], approver_grp_list, approver_grp_data)
            resp_obj.set_to_type(i.data['to_type'])
            resp_obj.set_tran_status(i.data['tran_status'])
            resp_obj.set_status(i.data['tran_status'])
            resp_obj.set_order(i.data['order'])

            if i.data['tran_type'] == Trantype.approver:
                approver_arr.append(resp_obj)
            elif i.data['tran_type'] == Trantype.collaborator:
                collabator_arr.append(resp_obj)
            elif i.data['tran_type'] == Trantype.proposal_approver:
                q_approver_arr.append(resp_obj)
        dictt["approver"] = approver_arr
        dictt["collabator"] = collabator_arr
        dictt["q_approver"] = q_approver_arr
        return dictt

    # project version history all entry
    def projectversion_insert(self, request, project_id, emp_id):
        ref_type = DocUtil.project
        cma_appserv = CmsApprovalService(request.scope)

        # version ProjectApprover
        prjapp_datatype = VersionDataType.ProjectApprover
        atran_type = Trantype.approver
        pjapp_data = cma_appserv.get_approvaltran_data(project_id, atran_type)
        v_pj_app = self.version_history(project_id, ref_type, pjapp_data, prjapp_datatype, emp_id)
        logger.info("v_pj_app" + str(v_pj_app))

        # version ProposalApprover
        prp_datatype = VersionDataType.ProposalApprover
        ptran_type = Trantype.proposal_approver
        ppapp_data = cma_appserv.get_approvaltran_data(project_id, ptran_type)
        v_pr_app = self.version_history(project_id, ref_type, ppapp_data, prp_datatype, emp_id)
        logger.info("v_pr_app" + str(v_pr_app))

        # version ProjectCollaborator
        pcoll_datatype = VersionDataType.ProjectCollaborator
        invi_serv = ProjectInvitationService(request.scope)
        ctran_type = Trantype.collaborator
        coll_data = cma_appserv.get_approvaltran_data(project_id, ctran_type)
        v_coll_app = self.version_history(project_id, ref_type, coll_data, pcoll_datatype, emp_id)
        logger.info("v_coll_app" + str(v_coll_app))

        # version  ProjectInvitation
        versiondata_type = VersionDataType.ProjectInvitation
        iv_data = invi_serv.invitation_projectget(project_id)
        versionhistory = self.version_history(project_id, ref_type, iv_data, versiondata_type, emp_id)
        print(versionhistory)
        logger.info("versionhistory" + str(versionhistory))

        # attach
        content_type = CovernoteUtil.project
        common_service = CommonService(request.scope)
        activefile = common_service.updatedfile(project_id, content_type)
        if len(activefile) > 0:
            doch = self.cmsdochstry(activefile, project_id)

        # covernote
        content_type = CovernoteUtil.project
        content_strategy_type = CovernoteUtil.project_strategy
        covernote = common_service.updated_covernote(project_id, content_type)
        strategy_covernote = common_service.updated_covernote(project_id, content_strategy_type)
        for cn in covernote:
            cvnt = self.cmscvrhstry(cn, project_id)
            logger.info("version - cvnt" + str(cvnt))
        for stcn in strategy_covernote:
            strategy_cvnt = self.cmscvrhstry(stcn, project_id)
            logger.info("version - strategy_cvnt" + str(strategy_cvnt))

        success_obj = NWisefinSuccess()
        success_obj.set_status("Success")
        success_obj.set_message("Created Successfully")
        return success_obj


# Vow History:
from userservice.controller.vowusercontroller import VowUser


class VowHistoryService:
    def __init__(self, request):
        vowuser_info = VowUser().get_user(request)

        self.emp_id = vowuser_info['user_id']
        self.entity_id = vowuser_info['entity_id']
        self.is_user = vowuser_info['is_user']
        self.schema = vowuser_info['schema']

    # def __init__(self, request):
    #     app_name = ApplicationNamespace.CMS_SERVICE
    #     vowuser_info = VowUser().get_user1(request, app_name)
    #     self.emp_id = vowuser_info['user_id']
    #     self.is_user = vowuser_info['is_user']
    #     self.schema = vowuser_info['schema']

    def projecthstry(self, prhdr, history_id):
        projecthsty = ProjectHistory.objects.using(self.schema).filter(history_id=history_id).order_by(
            '-created_date')
        if len(projecthsty) > 0:
            projecthsty = projecthsty[0]
            version = int(projecthsty.version) + 1
        else:
            version = 1
        project = ProjectHistory.objects.using(self.schema).create(
            history_id=history_id,
            code=prhdr.code,
            title=prhdr.title,
            type=prhdr.type,
            submission_start_date=prhdr.submission_start_date,
            submission_end_date=prhdr.submission_end_date,
            project_start_date=prhdr.project_start_date,
            project_end_date=prhdr.project_end_date,
            budget=prhdr.budget,
            cat_id=prhdr.cat_id,
            subcat_id=prhdr.subcat_id,
            onbehalf_group=prhdr.onbehalf_group,
            parent_id=prhdr.parent_id,
            view_type=prhdr.view_type,
            version=version,
            is_user=self.is_user,
            created_by=self.emp_id,
            created_date=timezone.now())

    def proposalhstry(self, prop_obj, history_id, project_id):
        projecthsty = ProposedContractHistory.objects.using(self.schema).filter(
            history_id=history_id).order_by('-created_date')
        if len(projecthsty) > 0:
            projecthsty = projecthsty[0]
            version = int(projecthsty.version) + 1
        else:
            version = 1
        proposal = ProposedContractHistory.objects.using(self.schema).create(
            history_id=history_id,
            project_id=project_id,
            code=prop_obj.code,
            name=prop_obj.name,
            submitted_date=prop_obj.submitted_date,
            budget=prop_obj.budget,
            proposer_code=prop_obj.proposer_code,
            is_vendor=prop_obj.is_vendor,
            version=version,
            is_user=self.is_user,
            created_by=self.emp_id)
        return proposal

    def cmsdochstry(self, cmsdoc_obj, prjtid):
        for d_j in cmsdoc_obj:
            cmsdoc = CMSDocumentsHistory.objects.using(self.schema).create(
                rel_id=prjtid,
                rel_type=d_j.rel_type,
                file_id=d_j.file_id,
                gen_file_name=d_j.gen_file_name,
                file_name=d_j.file_name,
                type=-1,
                created_by=d_j.created_by)

    def vow_cmscvrhstry(self, cmsdoc_obj, prjtid):
        cmsdoc = CMSCovernoteHistory.objects.using(self.schema).create(
            rel_id=prjtid,
            rel_type=cmsdoc_obj.rel_type,
            note=cmsdoc_obj.note,
            created_by=cmsdoc_obj.created_by,
            created_date=timezone.now())
        return cmsdoc

    def vow_proposal_version(self, proposal_id):
        condition = Q(status=ActiveStatus.Active) & Q(history_id=proposal_id)
        prlist = ProposedContractHistory.objects.using(self.schema).filter(condition)
        list_length = len(prlist)
        print(list_length)
        pr_list_data = NWisefinList()
        for prhdr in prlist:
            pr_data = ProposerResponse()
            pr_data.set_id(prhdr.id)
            pr_data.version_date = str(prhdr.created_date)
            pr_data.version = "Version " + str(prhdr.version)
            pr_list_data.append(pr_data)
        return pr_list_data

    def vow_proposal_viewsummary(self, request, proposal_id):
        history_id = request.GET.get('history_id')
        type = DocUtil.proposer
        if (history_id is not None) & (history_id != ''):
            condition = Q(status=ActiveStatus.Active) & Q(history_id=proposal_id) & Q(id=history_id)
        else:
            condition = Q(status=ActiveStatus.Active) & Q(history_id=proposal_id)
        print("project - condition ", condition)

        prlist = ProposedContractHistory.objects.using(self.schema).filter(condition).order_by(
            '-created_date')
        list_length = len(prlist)
        print(list_length)
        common_service = VowCommonService(request)
        prhdr = prlist[0]
        pr_data = ProposerResponse()
        pr_data.set_id(prhdr.id)
        pr_data.set_code(prhdr.code)
        pr_data.set_name(prhdr.name)
        pr_data.set_submitted_date(prhdr.submitted_date)
        pr_data.set_budget(prhdr.budget)
        pr_data.set_proposer_code(prhdr.proposer_code)
        pr_data.version_date = str(prhdr.created_date)
        pr_data.version = prhdr.version
        covernote_pr = common_service.vow_covernotehistory_project(prhdr.id, type)
        attach_pr = common_service.vow_attachementhistory_project(prhdr.id, type)
        pr_data.covernote = covernote_pr
        pr_data.filedata = attach_pr
        return pr_data

    # proposal version history all entry
    def proposalversion_insert(self, request, proposal_id):
        ref_type = DocUtil.proposer
        emp_id = self.emp_id
        cma_appserv = CmsApprovalService(request.scope)

        # version ProposalApprover
        prp_datatype = VersionDataType.ProposalApprover
        ptran_type = Trantype.proposal_approver
        ppapp_data = cma_appserv.get_proposalapprovaltran_data(proposal_id, ptran_type)
        v_pr_app = self.vow_version_history(proposal_id, ref_type, ppapp_data, prp_datatype, emp_id)
        logger.info("v_pr_app" + str(v_pr_app))

        # attach
        content_type = CovernoteUtil.proposer
        common_service = VowCommonService(request.scope)
        activefile = common_service.vow_updatedfile(proposal_id, content_type)
        print("activefile", activefile)
        if len(activefile) > 0:
            doch = self.cmsdochstry(activefile, proposal_id)

        # covernote proposer
        pcontent_type = CovernoteUtil.proposer
        pcovernote = common_service.vow_updated_covernote(proposal_id, pcontent_type)
        for cn in pcovernote:
            cvnt = self.vow_cmscvrhstry(cn, proposal_id)
            logger.info("version - cvnt" + str(cvnt))

        # covernote proposal_execution
        econtent_type = CovernoteUtil.proposal_execution
        ecovernote = common_service.vow_updated_covernote(proposal_id, econtent_type)
        for cn in ecovernote:
            cvnt = self.vow_cmscvrhstry(cn, proposal_id)
            logger.info("version - cvnt" + str(cvnt))

        # covernote proposal_financial
        fcontent_type = CovernoteUtil.proposal_financial
        fcovernote = common_service.vow_updated_covernote(proposal_id, fcontent_type)
        for cn in fcovernote:
            cvnt = self.vow_cmscvrhstry(cn, proposal_id)
            logger.info("version - cvnt" + str(cvnt))

        success_obj = NWisefinSuccess()
        success_obj.set_status("Success")
        success_obj.set_message("Created Successfully")
        return success_obj

    # common version history insert
    def vow_version_history(self, ref_id, ref_type, data, data_type, emp_id):
        print("version data i/p: ", data)
        vhsrty = CMSVersionHistory.objects.using(self.schema).filter(
            ref_id=ref_id,
            ref_type=ref_type,
            data_type=data_type,
            status=ActiveStatus.Active).order_by('-created_date')
        if len(vhsrty) > 0:
            versionhsrty = vhsrty[0]
            version = int(versionhsrty.version) + 1
        else:
            version = 1
        for versionhstry in data:
            if "_state" in versionhstry:
                print("delete")
                del versionhstry['_state']
            if "created_date" in versionhstry:
                versionhstry['created_date'] = conversion(versionhstry['created_date'])
            if "updated_date" in versionhstry:
                versionhstry['updated_date'] = conversion(versionhstry['updated_date'])
            print("after convsn version data i/p: ", versionhstry)
            versioncr = CMSVersionHistory.objects.using(self.schema).create(
                version=version,
                ref_id=ref_id,
                ref_type=ref_type,
                data=versionhstry,
                data_type=data_type,
                created_by=emp_id,
                created_date=timezone.now())
        success_obj = NWisefinSuccess()
        success_obj.set_status("Success")
        success_obj.set_message("Success")
        return success_obj

    # common version history get
    def vow_version_get(self, ref_id, ref_type, version, data_type):
        condition = Q(status=ActiveStatus.Active) & Q(ref_id=ref_id) & Q(ref_type=ref_type) & Q(
            data_type=data_type) & Q(version=version)
        print("project - condition ", condition)
        vhsrty_dt = CMSVersionHistory.objects.using(self.schema).filter(condition)
        v_list = []
        for vhsrty in vhsrty_dt:
            vhstry_data = VersionHistoryResponse()
            all_data = vhsrty.data
            data = all_data.replace("'", "\"")
            print("replaced", data)
            group_data = literal_eval(data)
            vhstry_data.set_data(group_data)
            vhstry_data.set_data_type(vhsrty.data_type)
            v_list.append(vhstry_data)
        return v_list

