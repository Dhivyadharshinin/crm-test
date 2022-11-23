from cmsservice.models.cmsmodels import Project, ProjectApprovalTran, ProjectTranComments, \
    ProposedContractApprovalTran, ProposedContractTranComments, ProposedContract, AnswerMapping
from cmsservice.service.cmscommonservice import CommonService
from cmsservice.service.quesansservice import Quesansservice
from cmsservice.util.cmsutil import TranApproverType, Trantype, TranStatus, ApprovalStatus, \
    ActiveStatus, DocUtil, HistoryStatus,Mailtotypeutil,Mail_TranType,cms_file_key
from django.utils import timezone
from cmsservice.data.response.cmsapprovalresponse import ApprovalHistoryResponse, ApprovalTranHistoryResponse
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage
from utilityservice.service import cms_api_service
from utilityservice.service.cms_api_service import ApiService
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from django.db.models import Q
from cmsservice.models.cmsmodels import QuestionAnswers,QuestionClassification,QuestionProjectMapping,CMSProjectInvitation,CMSDocuments
from cmsservice.service.cms_email_service import EmailService
import pandas as pd
import json ,numpy as np

class CmsApprovalService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.CMS_SERVICE)

    #  APPROVAL QUEUE INSERT
    def project_approval_queue(self, data, project_id, emp_id,is_draft):
        parallel_approval = 0
        to_arr = data['to_arr']
        to_type = 2

        if to_type not in [TranApproverType.employee, TranApproverType.group]:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description("INVAILD TRAN TYPE")
            e = {"app_resp": False, "obj": error_obj}
            return e

        val_to_arr = sorted(set(to_arr), key=to_arr.index)
        if to_arr != val_to_arr:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description("INVAILD APPROVER")
            e = {"app_resp": False, "obj": error_obj}
            return e

        if to_type == TranApproverType.employee:
            if emp_id in to_arr:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description("Maker can't be Approver")
                e = {"app_resp": False, "obj": error_obj}
                return e

        # elif to_type == TranApproverType.group :
        #     emp_grp = ApiService(request.scope).get_group_info_by_id(emp_id)
        #     val_grp_arr=list(set(emp_grp) & set(to_arr))
        #     if len(val_grp_arr)>0:
        #         error_obj = NWisefinError()
        #         error_obj.set_code(ErrorMessage.INVALID_DATA)
        #         error_obj.set_description("Maker group can't be Approver")
        #         e = {"app_resp": False, "obj": error_obj}
        #         return e

        q_order = 1
        arr = []

        # created by me in tran
        c_obj = ProjectApprovalTran(project_id=project_id, tran_type=Trantype.creator,
                                    to_type=TranApproverType.employee, to=emp_id,
                                    order=0, tran_status=TranStatus.creator,
                                    created_by=emp_id, created_date=timezone.now())
        arr.append(c_obj)

        for i in to_arr:
            if is_draft!=None:
                tran_status=TranStatus.awaiting
            else:
                if parallel_approval != 0:
                    tran_status = TranStatus.pending
                else:
                    if q_order == 1:
                        tran_status = TranStatus.pending
                    else:
                        tran_status = TranStatus.awaiting

            obj = ProjectApprovalTran(project_id=project_id, tran_type=Trantype.approver,
                                      to_type=to_type, to=i, order=q_order,
                                      tran_status=tran_status, created_by=emp_id, created_date=timezone.now())
            arr.append(obj)
            q_order += 1

        ProjectApprovalTran.objects.using(self._current_app_schema()).bulk_create(arr)
        ProjectTranComments.objects.using(self._current_app_schema()).create(rel_id=project_id,
                                                                             rel_type=DocUtil.project, approver=emp_id,
                                                                             comments=None, created_by=emp_id,
                                                                             created_date=timezone.now(),
                                                                             approval_status=HistoryStatus.CREATED)
        e = {"app_resp": True, "obj": None}
        return e

    def collaborator_queue(self, data, project_id, emp_id):
        arr = []
        to_arr = data['to_arr']
        to_type = 2
        for data in to_arr:
            obj = ProjectApprovalTran(project_id=project_id, tran_type=Trantype.collaborator,
                                      to_type=to_type, to=data, order=0,
                                      tran_status=TranStatus.creator, created_by=emp_id, created_date=timezone.now())
            arr.append(obj)

        ProjectApprovalTran.objects.using(self._current_app_schema()).bulk_create(arr)
        e = {"app_resp": True, "obj": None}
        return e

    def q_approval_queue(self, data, project_id, emp_id, parallel_approval):
        to_arr = data['to_arr']

        q_order = 1
        arr = []

        tran_status = TranStatus.creator
        for i in to_arr:
            obj = ProjectApprovalTran(project_id=project_id, tran_type=Trantype.proposal_approver,
                                      to_type=TranApproverType.group, to=i, order=q_order,
                                      tran_status=tran_status, created_by=emp_id, created_date=timezone.now())
            arr.append(obj)
            q_order += 1

        ProjectApprovalTran.objects.using(self._current_app_schema()).bulk_create(arr)
        e = {"app_resp": True, "obj": None}
        return e

    #  TRAN LIST
    def get_project_approver_list(self, request, project_id):
        cond = Q(project_id=project_id) & Q(status=ActiveStatus.Active) & ~Q(tran_type=Trantype.creator)
        obj = ProjectApprovalTran.objects.using(self._current_app_schema()).filter(cond)
        approver_arr, collabator_arr, q_approver_arr = [], [], []
        approver_list = [i.to for i in obj if i.to_type == TranApproverType.employee]
        approver_data = ApiService(request.scope).get_multi_emp(request, approver_list)

        approver_grp_list = [i.to for i in obj if i.to_type == TranApproverType.group]
        approver_grp_data = ApiService(request.scope).get_multi_group_info_by_id(approver_grp_list)
        dictt = {}

        for i in obj:
            resp_obj = ApprovalTranHistoryResponse()
            resp_obj.set_id(i.id)
            resp_obj.set_approver(i.to, i.to_type, approver_data, approver_grp_data)
            resp_obj.set_to_type(i.to_type)
            resp_obj.set_status(i.tran_status)
            resp_obj.set_order(i.order)

            if i.tran_type == Trantype.approver:
                approver_arr.append(resp_obj)
            elif i.tran_type == Trantype.collaborator:
                collabator_arr.append(resp_obj)
            elif i.tran_type == Trantype.proposal_approver:
                q_approver_arr.append(resp_obj)
        dictt["approver"] = approver_arr
        dictt["collabator"] = collabator_arr
        dictt["q_approver"] = q_approver_arr
        return dictt

    # APPROVAL STATUS UPDATE
    def project_status_update(self, request, data, project_id, emp_id):
        approval_status = data['status']
        remarks = data['remarks']
        approver = None
        if approver in data:
            approver = data['approver']

        # approval status validation
        if approval_status in [TranStatus.approved, TranStatus.rejected, TranStatus.reviwed]:
            pass
        else:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description("INVAILD STATUS")
            return error_obj

        cond = Q(project_id=project_id) & Q(status=ActiveStatus.Active) & Q(tran_type=Trantype.approver)
        obj = ProjectApprovalTran.objects.using(self._current_app_schema()).filter(cond)

        if obj[0].project.created_by == emp_id:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description("Approver and Maker can't be same")
            return error_obj

        emp_grp = ApiService(request.scope).grouplist_by_empid(emp_id)

        approved_arr, approver_arr, arr, total_arr = [], [], [], []
        is_approver = False
        for i in obj:
            approver_arr.append(i.to)
            if i.to_type == TranApproverType.employee:
                if (emp_id == i.to) and (i.tran_status == TranStatus.pending):
                    current_order=i.order
                    d={"id":i.id,"transtatus":approval_status}
                    arr.append(d)
                    is_approver = True
            elif i.to_type == TranApproverType.group:
                if (i.to in emp_grp) and (i.tran_status == TranStatus.pending):
                    current_order = i.order
                    d = {"id": i.id, "transtatus": approval_status}
                    arr.append(d)
                    is_approver = True

        # current approver validation
        if is_approver == False:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description("INVAILD APPROVER")
            return error_obj

        #  forward and approve
        if approver != None and approval_status == TranStatus.approved:
            if approver == None or approver == "":
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description("Please Choose Approver")
                return error_obj
            if approver in approver_arr:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description("INVAILD APPROVER")
                return error_obj

            ProjectApprovalTran.objects.using(self._current_app_schema()).filter(project_id=project_id, order=current_order,
                                               tran_status=TranStatus.pending).update(tran_status=data["status"],
                                                                                      updated_date=timezone.now(),
                                                                                      updated_by=emp_id)
            ProjectApprovalTran.objects.using(self._current_app_schema()).create(project_id=project_id, order=int(current_order) + 1,
                                               tran_type=Trantype.approver, tran_status=TranStatus.pending, to=approver,
                                               to_type=2, status=ActiveStatus.Active, created_by=emp_id,
                                               created_date=timezone.now())


        elif approval_status == TranStatus.approved:
            for i in obj:
                if i.order == (current_order + 1):
                    d = {"id": i.id, "transtatus": TranStatus.pending}
                    arr.append(d)
                if i.tran_type == Trantype.approver:
                    if i.tran_status == TranStatus.approved:
                        approved_arr.append(i.tran_status)
                total_arr.append(i.id)
            if len(total_arr) == (int(len(approved_arr)) + 1):
                Project.objects.using(self._current_app_schema()).filter(id=project_id).update(
                    approval_status=TranStatus.approved, updated_date=timezone.now(), updated_by=emp_id)


            mail_data = self.projectinvitaioncmsinfo(project_id)
            service = EmailService(self._scope())
            a=service.createmailcms(mail_data,emp_id)

        elif approval_status == TranStatus.reviwed:
            # for j in obj:
            #     if j.order == 1:
            #         d = {"id": j.id, "transtatus": TranStatus.pending}
            #         arr.append(d)
            #     elif j.order > 1:
            #         d = {"id": j.id, "transtatus": TranStatus.awaiting}
            #         arr.append(d)
            Project.objects.using(self._current_app_schema()).filter(id=project_id).update(
                approval_status=TranStatus.reviwed, updated_date=timezone.now(), updated_by=emp_id)

        elif approval_status == TranStatus.rejected:
            Project.objects.using(self._current_app_schema()).filter(id=project_id).update(
                approval_status=ApprovalStatus.REJECTED)

        for j in arr:
            ProjectApprovalTran.objects.using(self._current_app_schema()).filter(id=j['id']).update(
                tran_status=j['transtatus'])

        #  project tran history
        ProjectTranComments.objects.using(self._current_app_schema()).create(rel_id=project_id,
                                                                            rel_type=DocUtil.project, approver=emp_id,
                                                                             comments=remarks, created_by=emp_id,
                                                                             created_date=timezone.now(),
                                                                             approval_status=approval_status)

        success_obj = NWisefinSuccess()
        success_obj.set_status("Success")
        success_obj.set_message("Created Successfully")
        return success_obj

    # APPROVAL PROJECT HISTORY
    def get_project_approver_history(self,request,project_id,rel_type):

        if rel_type!=None:
            rel_type=DocUtil.project_identification
        else:
            rel_type = DocUtil.project

        obj=ProjectTranComments.objects.using(self._current_app_schema()).filter(rel_id=project_id,status=ActiveStatus.Active,rel_type=rel_type)
        arr=NWisefinList()
        approver_list = [i.approver for i in obj ]
        approver_data = ApiService(request.scope).get_multi_emp(request, approver_list)
        for i in obj:
            resp_obj = ApprovalHistoryResponse()
            resp_obj.set_id(i.id)
            resp_obj.set_approver(i.approver, approver_data)
            resp_obj.set_comments(i.comments)
            resp_obj.set_approval_status(i.approval_status)
            resp_obj.set_created_date(i.created_date)
            arr.append(resp_obj)
        return arr

    # proposed APPROVAL STATUS UPDATE
    def proposed_status_update(self, request, data, proposed_id, emp_id):
        approval_status = data['status']
        remarks = data['remarks']
        # group_id = data['group_id']
        approver = None
        if approver in data:
            approver = data['approver']

        # approval status validation
        if approval_status in [TranStatus.approved, TranStatus.rejected, TranStatus.reviwed]:
            pass
        else:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description("INVAILD STATUS")
            return error_obj

        obj = ProposedContractApprovalTran.objects.using(self._current_app_schema()).filter(status=ActiveStatus.Active,proposed_id=proposed_id,tran_type=Trantype.approver)
        parallel_approver = obj[0].proposed.parallel_approval
        if obj[0].proposed.created_by == emp_id:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description("Approver and Maker can't be same")
            return error_obj
        emp_grp = ApiService(request.scope).grouplist_by_empid(emp_id)

        approved_arr, approver_arr, arr, total_arr = [], [], [], []
        is_approver = False
        for i in obj:
            approver_arr.append(i.to)
            if i.to_type == TranApproverType.employee:
                if (emp_id == i.to) and (i.tran_status == TranStatus.pending):
                    current_order = i.order
                    d = {"id": i.id, "transtatus": approval_status}
                    arr.append(d)
                    is_approver = True
            elif i.to_type == TranApproverType.group:
                if (i.to in emp_grp) and (i.tran_status == TranStatus.pending):
                    current_order = i.order
                    d = {"id": i.id, "transtatus": approval_status}
                    arr.append(d)
                    is_approver = True

        # current approver validation
        if is_approver == False:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description("INVAILD APPROVER")
            return error_obj
        # if parallel_approver == False:
        if approver != None and approval_status == TranStatus.approved:
            if approver == None or approver == "":
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description("Please Choose Approver")
                return error_obj
            if approver in approver_arr:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description("INVAILD APPROVER")
                return error_obj

            ProposedContractApprovalTran.objects.using(self._current_app_schema()).filter(proposed_id=proposed_id, order=current_order).update(
                tran_status=data["status"], updated_date=timezone.now(), updated_by=emp_id)
            ProposedContractApprovalTran.objects.using(self._current_app_schema()).create(proposed_id=proposed_id, order=int(current_order) + 1,
                                                        tran_type=Trantype.approver, tran_status=TranStatus.pending,
                                                        to=approver, to_type=2, status=ActiveStatus.Active,
                                                        created_by=emp_id, created_date=timezone.now())



        elif approval_status == TranStatus.approved:
            for i in obj:
                if i.order == (current_order + 1):
                    d = {"id": i.id, "transtatus": TranStatus.pending}
                    arr.append(d)
                if i.tran_type == Trantype.approver:
                    if i.tran_status == TranStatus.approved:
                        approved_arr.append(i.tran_status)
                total_arr.append(i.id)
            if len(total_arr) == (int(len(approved_arr)) + 1):
                ProposedContract.objects.using(self._current_app_schema()).filter(id=proposed_id).update(
                    approval_status=TranStatus.approved, updated_date=timezone.now(), updated_by=emp_id)
        elif approval_status == TranStatus.reviwed:
            # for j in obj:
            #     if j.order == 1:
            #         d = {"id": j.id, "transtatus": TranStatus.pending}
            #         arr.append(d)
            #     elif j.order > 1:
            #         d = {"id": j.id, "transtatus": TranStatus.awaiting}
            #         arr.append(d)
            ProposedContract.objects.using(self._current_app_schema()).filter(id=proposed_id).update(
                approval_status=TranStatus.reviwed, updated_date=timezone.now(), updated_by=emp_id)
        elif approval_status == TranStatus.rejected:
            ProposedContract.objects.using(self._current_app_schema()).filter(id=proposed_id).update(
                approval_status=ApprovalStatus.REJECTED)

        for j in arr:
            ProposedContractApprovalTran.objects.using(self._current_app_schema()).filter(id=j['id']).update(
                tran_status=j['transtatus'])
        # else:
        #     ProposedContractApprovalTran.objects.using(self._current_app_schema()).filter(to=group_id,proposed_id=proposed_id,to_type=TranApproverType.group).update(
        #         tran_status=approval_status)
        ProposedContractTranComments.objects.using(self._current_app_schema()).create(proposed_id=proposed_id,approver=emp_id, comments=remarks,created_by=emp_id,approval_status=approval_status)

        success_obj = NWisefinSuccess()
        success_obj.set_status("Success")
        success_obj.set_message("Created Successfully")
        return success_obj

    def projectinvitaioncmsinfo(self,project_id):
        data=CMSProjectInvitation.objects.using(self._current_app_schema()).filter(project_id=project_id)
        arr= []
        for i in data:
            data1 = {"rel_id": project_id, "rel_type" :DocUtil.project, "is_user" : 0,
                  "to_type" : Mailtotypeutil.vendor,"tran_type":Mail_TranType.INVITATION,"to_mail":i.id}
            arr.append(data1)
        return arr

    # APPROVAL proposed HISTORY
    def get_proposed_approver_history(self, request, proposed_id):
        obj = ProposedContractTranComments.objects.using(self._current_app_schema()).filter(proposed_id=proposed_id,
                                                                                   status=ActiveStatus.Active,)
        arr = NWisefinList()
        approver_list = [i.approver for i in obj]
        approver_data = ApiService(request.scope).get_multi_emp(request, approver_list)

        for i in obj:
            resp_obj = ApprovalHistoryResponse()
            resp_obj.set_id(i.id)
            resp_obj.set_approver(i.approver, approver_data)
            resp_obj.set_comments(i.comments)
            resp_obj.set_approval_status(i.approval_status)
            resp_obj.set_created_date(i.created_date)
            arr.append(resp_obj)
        return arr

    # proposed assign
    def assign_proposed(self, data, project_id, emp_id, scope):
        ass_emp_id = data['to_arr']
        to_type = data['to_type']

        if to_type not in [TranApproverType.employee, TranApproverType.group]:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description("INVAILD TRAN TYPE")
            return error_obj

        projectty = Project.objects.using(self._current_app_schema()).filter(id=project_id,
                                                                             approval_status=ApprovalStatus.APPROVED)
        if len(projectty) > 0:
            prpos_list = ProposedContract.objects.using(self._current_app_schema()).filter(project_id=project_id)
            for pro in prpos_list:
                proposed_id = pro.id
                common_service = CommonService(scope)
                tran_type = Trantype.approver
                parallel_approver = pro.parallel_approval
                resp = common_service.bulk_create_assign(ass_emp_id, proposed_id, tran_type, to_type, emp_id,
                                                         parallel_approver)
            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message('Successfully Assigned')
            return success_obj

        else:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_DATA)
            return error_obj

    def assign_proposedexact(self, data, project_id, proposed_id, emp_id, scope):
        ass_emp_id = data['ass_emp_id']
        to_type = data['to_type']

        if to_type not in [TranApproverType.employee, TranApproverType.group]:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description("INVAILD TRAN TYPE")
            return error_obj

        projectty = Project.objects.using(self._current_app_schema()).filter(id=project_id,
                                                                             approval_status=ApprovalStatus.DRAFT)
        if len(projectty) > 0:
            prpos_list = ProposedContract.objects.using(self._current_app_schema()).filter(project_id=project_id,
                                                                                           proposed_id=proposed_id)
            if len(prpos_list) > 0:
                common_service = CommonService(scope)
                tran_type = Trantype.approver
                parallel_approval = prpos_list[0].parallel_approval
                resp = common_service.bulk_create_assign(ass_emp_id, proposed_id, tran_type, to_type, emp_id,
                                                         parallel_approval)
                success_obj = NWisefinSuccess()
                success_obj.set_status(SuccessStatus.SUCCESS)
                success_obj.set_message('Successfully Assigned')
                return success_obj
            else:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_PROPOSED_ID)
                error_obj.set_description(ErrorDescription.INVALID_PROPOSED_ID)
                return error_obj
        else:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_PROJECT_ID)
            error_obj.set_description(ErrorDescription.INVALID_PROJECT_ID)
            return error_obj

    # TRAN LIST
    def get_proposal_approver_list(self, request, proposed_id):
        cond = Q(proposed_id=proposed_id) & Q(status=ActiveStatus.Active) & ~Q(order=0)
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

    #  Proposal create QUEUE INSERT
    def proposal_createtran(self, proposed_id, emp_id, project_id):
        to_arr = ProjectApprovalTran.objects.using(self._current_app_schema()).filter(project_id=project_id, status=1,
                                                                                      tran_type=Trantype.q_approver).values_list(
            'to')
        q_order = 1
        arr = []
        # created by me in tran
        c_obj = ProposedContractApprovalTran(proposed_id=proposed_id, tran_type=Trantype.creator,
                                             to_type=TranApproverType.employee, to=emp_id, order=0,
                                             tran_status=TranStatus.creator, created_by=emp_id,
                                             created_date=timezone.now())
        arr.append(c_obj)

        for i in to_arr:
            if q_order == 1:
                tran_status = TranStatus.pending
            else:
                tran_status = TranStatus.awaiting

            obj = ProposedContractApprovalTran(proposed_id=proposed_id, tran_type=Trantype.approver,
                                               to_type=TranApproverType.group, to=i, order=q_order,
                                               tran_status=tran_status, created_by=emp_id,
                                               created_date=timezone.now())
            arr.append(obj)
            q_order += 1

        ProposedContractApprovalTran.objects.using(self._current_app_schema()).bulk_create(arr)
        ProposedContractTranComments.objects.using(self._current_app_schema()).create(proposed_id=proposed_id,
                                                                                      approver=emp_id, remarks=None,
                                                                                      created_by=emp_id,
                                                                                      created_date=timezone.now(),
                                                                                      approval_status=TranStatus.creator)
        return c_obj

    # proposal shortlist
    def proposal_shortlist(self, data, emp_id, request):
        is_shortlist = request.GET.get('is_shortlist')
        proposal_id = data['proposal_id']
        remarks = data['remarks']
        condition_prop = Q(id=proposal_id) & Q(status=ActiveStatus.Active)
        projecttyl = ProposedContract.objects.using(self._current_app_schema()).filter(condition_prop)
        if len(projecttyl) == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_PROPOSED_ID)
            error_obj.set_description(ErrorDescription.INVALID_PROPOSED_ID)
            return error_obj
        if (is_shortlist is not None) & (is_shortlist is not '') & (int(is_shortlist) != 0):
            projectty = projecttyl[0]
            project_createdBy = projectty.project.created_by
            if project_createdBy != emp_id:
                error_obj = NWisefinError()
                error_obj.set_code("You don't have permission to perform this action")
                error_obj.set_description("Project Maker only allow to Shortlist Proposal")
                return error_obj
            prpos_list = ProposedContract.objects.using(self._current_app_schema()).filter(condition_prop).update(
                is_shortlisted=True, updated_date=timezone.now(), updated_by=emp_id)
            commentprpos_list = ProposedContractTranComments.objects.using(self._current_app_schema()).create(
                proposed_id=proposal_id,
                approver=emp_id,
                comments=remarks,
                created_by=emp_id,
                approval_status=ApprovalStatus.SHORTLISTED)
            success_obj = NWisefinSuccess()
            success_obj.set_status("Proposal Shortlisted")
            success_obj.set_message("Proposal Shortlisted Successfully")
            return success_obj
        else:
            prpos_list = ProposedContract.objects.using(self._current_app_schema()).filter(condition_prop).update(
                is_shortlisted=False, updated_date=timezone.now(), updated_by=emp_id)
            commentprpos_list = ProposedContractTranComments.objects.using(self._current_app_schema()).create(
                proposed_id=proposal_id,
                approver=emp_id,
                comments=remarks,
                created_by=emp_id,
                approval_status=ApprovalStatus.SHORTLISTED_UNDO)
            success_obj = NWisefinSuccess()
            success_obj.set_status("Proposal Shortlisted Undo")
            success_obj.set_message("Proposal Shortlisted Undo Successfully")
            return success_obj

    # proposal shortlistfinalize
    def proposal_shortlistfinalize(self, data, emp_id):
        proposal_id = data['proposal_id']
        remarks = data['remarks']
        condition_prop = Q(id=proposal_id) & Q(status=ActiveStatus.Active)
        projecttyl = ProposedContract.objects.using(self._current_app_schema()).filter(condition_prop)
        if len(projecttyl) == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_PROPOSED_ID)
            error_obj.set_description(ErrorDescription.INVALID_PROPOSED_ID)
            return error_obj
        prpos_list = ProposedContract.objects.using(self._current_app_schema()).filter(condition_prop).update(
            is_finalized=True, updated_date=timezone.now(), updated_by=emp_id)
        commentprpos_list = ProposedContractTranComments.objects.using(self._current_app_schema()).create(
            proposed_id=proposal_id,
            approver=emp_id,
            comments=remarks,
            created_by=emp_id,
            approval_status=ApprovalStatus.FINALIZED)
        success_obj = NWisefinSuccess()
        success_obj.set_status("Proposal Shortlist Finalized")
        success_obj.set_message("Proposal ShortlistFinalized Successfully")
        return success_obj

    def proposal_parallel_approver(self, product_id, employee_id):
        proj_ide_tab = ProposedContract.objects.using(self._current_app_schema()).filter(id=product_id, approval_status=ApprovalStatus.APPROVED)

        if len(proj_ide_tab) != 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description("INVAILD APPROVER")
            return error_obj

        proj_ide_tab1 = ProposedContract.objects.using(self._current_app_schema()).filter(id=product_id, created_by=employee_id)
        proj_ide_tab2 = ProposedContract.objects.using(self._current_app_schema()).filter(parallel_approval=False)
        if len(proj_ide_tab1) == 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description("INVAILD APPROVER")
            return error_obj
        if len(proj_ide_tab2) != 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description("INVAILD APPROVER")
            return error_obj

        proj_ide_t1 = ProposedContractApprovalTran.objects.using(self._current_app_schema()).filter(proposed_id=product_id,
                                                                  tran_status=TranStatus.awaiting).update(
            tran_status=TranStatus.pending)
        proj_ide_t2 = ProposedContract.objects.using(self._current_app_schema()).filter(id=product_id).update(parallel_approval=True)
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        return success_obj

    def project_proposal_approval(self,request, data, project_id, employee_id):
        approval_status = data['status']
        remarks = data['remarks']
        group_id = data['group_id']
        tab=ProjectApprovalTran.objects.filter(project_id=project_id,to=group_id,tran_type=Trantype.q_approver)
        api_ser=ApiService(self._scope())
        emp_grup=api_ser.grouplist_by_empid(employee_id)
        if tab[0].to not in emp_grup:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description("INVAILD APPROVER")
            return error_obj
        tab.update(tran_status=approval_status)
        ProjectTranComments.objects.create(approver=employee_id, comments=remarks, created_by=employee_id,
                                           rel_id=project_id, rel_type=DocUtil.project_identification,
                                           approval_status=TranStatus.reviwed)
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        return success_obj

    def move_to_proposal_approval(self,data, project_id, employee_id):
        arr=[]
        if 'arr' in data:
            arr=data['arr']
        comments = data['comments']

        cond= Q(project_id=project_id)&Q(status=ActiveStatus.Active)&Q(is_finalized=True)&Q(approval_status=ApprovalStatus.EVALUATION)
        if len(arr)>0:
            cond&=Q(id__in=arr)

        proposal_obj=ProposedContract.objects.filter(cond)
        proposal_id=[p.id  for p in proposal_obj ]
        if len(proposal_obj)==0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description("INVAILD ID")
            return error_obj

        project_obj =proposal_obj[0].project
        parallel_approval= project_obj.parallel_approval

        val_proposal_id=[i.id for i in proposal_obj]
        tran_cond = Q(tran_status=TranStatus.awaiting) & Q(tran_type=Trantype.approver)&Q(proposed_id__in=val_proposal_id)
        if parallel_approval ==False:
            tran_cond &=Q(order=1)

        ProposedContractApprovalTran.objects.filter(tran_cond).update(tran_status=TranStatus.pending)

        proposal_arr=[]
        for j in val_proposal_id:
            p_obj=ProposedContractTranComments(proposed_id=j,approver=employee_id,comments=comments,approval_status=HistoryStatus.MOVE_TO_APPROVAL,created_by=employee_id)
            proposal_arr.append(p_obj)

        ProposedContractTranComments.objects.bulk_create(proposal_arr)
        ProposedContract.objects.filter(id__in=proposal_id).update(approval_status=ApprovalStatus.PENDING)

        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj



    def new_evaluator(self,project_id):
        api_serv = cms_api_service.ApiService(self._scope())
        # project type
        questype = api_serv.get_proquesmap_id(project_id)
        q_type = api_serv.get_questype(questype)
        vsolv_list = NWisefinList()
        type_dict={}
        for type in q_type:
            data = api_serv.get_ques([type.id])
            qid_arr = [q.id for q in data]
            qid_name = [q.text for q in data]
            question_arr = list(set(qid_arr))
            question_name_arr = list(set(qid_name))
            cls=Quesansservice(self._scope())
            proposal_arr = cls.get_finalized_proposal(project_id)


            # question_arr = []
            # proposal_arr = []
            arr=[]
            dict={}
            dict["name"]="Questions"
            # dict["Questions"]=question_arr
            # vsolv_list.append(dict)
            dict["value"] = question_name_arr
            arr.append(dict)
            # dict={}
            answer_arr = []
            evaluator_arr=[]
            for proposal in proposal_arr:
                # answer_tab=QuestionAnswers.objects.using(self._current_app_schema()).filter(classify__classify_id=proposal,classify__classify_type=DocUtil.proposer)
                dict = {}
                for questions in question_arr:
                    answer_tab = QuestionAnswers.objects.using(self._current_app_schema()).filter(
                        classify__classify_id=proposal, classify__classify_type=DocUtil.proposer,question_id=questions)
                    if len(answer_tab)!=0:
                        for data in answer_tab:
                            answer_arr.append(data.answer)
                            evaluator = AnswerMapping.objects.using(self._current_app_schema()).filter(
                                answer_id=data.id)
                            if len(evaluator)!=0:
                                evaluator_arr.append(evaluator.latest().comments)
                            else:
                                evaluator_arr.append(None)
                    else:
                        answer_arr.append(None)
                        evaluator_arr.append(None)

                name=ProposedContract.objects.using(self._current_app_schema()).get(id=proposal).name
                dict["name"]=name
                dict["value"]=answer_arr
                arr.append(dict)
                dict={}
                answer_arr = []
                dict["name"]="Evaluator"
                dict["value"]=evaluator_arr
                evaluator_arr=[]
                arr.append(dict)
                dict={}

            type_dict["type"]=type.name
            type_dict["value"]=arr
            vsolv_list.append(type_dict)
            type_dict={}
        # dict["name"] = "Questions"


        return vsolv_list

    def get_question_answer(self,proposal_id,qid_arr):
        answer_obj = QuestionAnswers.objects.using(self._current_app_schema()).filter(
            classify__classify_id__in=proposal_id, classify__classify_type=DocUtil.proposer, question_id__in=qid_arr).values('classify__classify_id','id','question_id','answer','question_type')
        return  answer_obj

    def project_qtype(self,project_id):
        api_serv = cms_api_service.ApiService(self._scope())
        project_type = api_serv.get_proquesmap_id(project_id)
        q_type = api_serv.get_questype(project_type).values('id','name')
        q_type = list(q_type)
        data= json.dumps(q_type,indent=4)
        return data

    def evaluator1(self,project_id,request):
        api_serv = cms_api_service.ApiService(self._scope())
        # project type
        type_id =request.GET.get('type_id')
        if type_id !=None:
            q_type =[type_id]
        else:
            project_type = api_serv.get_proquesmap_id(project_id)
            q_type = api_serv.get_questype(project_type)

        question_data = api_serv.get_ques(q_type)
        # question dataframe
        question_df = pd.DataFrame(question_data.values('id','text','ref_id'))
        question_df=question_df.rename({"text":"question"},axis=1)

        qid_arr = [i.id for i in question_data]
        cls = Quesansservice(self._scope())
        proposal_info = cls.get_finalized_proposal_info(project_id)
        proposal_arr = [p['id'] for p in proposal_info]
        answer_data=self.get_question_answer(proposal_arr,qid_arr)
        ansid_arr=[i['id'] for i in answer_data ]

        # file
        q_file_df =pd.DataFrame(columns=['id','rel_id','rel_type'])
        docu_df= pd.DataFrame(columns=['a_id','file'])
        if len(ansid_arr) >0:
            q_file=CMSDocuments.objects.using(self._current_app_schema()).filter(rel_id__in=ansid_arr, rel_type=DocUtil.Questionnaire,status=ActiveStatus.Active).values('id','rel_id','rel_type')
            file_relid=list(set([j['rel_id'] for j in q_file]))
            if len(q_file) >0 :
                q_file_df=pd.DataFrame(q_file)
                q_file_df['file_key'] = cms_file_key()+ q_file_df['id'].astype(str)

                for row in file_relid:
                    arr1 = q_file_df.loc[q_file_df['rel_id'] == row].to_dict('records')
                    data1={"a_id":row,"file":arr1}
                    docu_df = docu_df.append(data1, ignore_index=True)

        # answer dataframe
        if len(answer_data) >0 :
            answer_df=pd.DataFrame(answer_data)
        else:
            answer_df=pd.DataFrame(columns=['classify__classify_id','id','question_id','answer','question_type'])


        # comments dataframe
        comments_df = pd.DataFrame(columns=['comments', 'red_flag', 'score', 'answer_id'])
        if len(ansid_arr) > 0:
            ans_comments = AnswerMapping.objects.using(self._current_app_schema()).filter(answer_id__in=ansid_arr, status=ActiveStatus.Active).values('comments','red_flag','score','answer_id')
            if len(ans_comments)>0:
                comments_df=pd.DataFrame(ans_comments)

        answer_df = pd.merge(answer_df,comments_df,how="left",left_on='id',right_on='answer_id')

        answer_df =pd.merge(answer_df,docu_df,how='left',left_on='id',right_on='a_id')

        arr=['question']
        for p in proposal_info:
            p_id=p['id']
            p_name=p['name']
            p_ans=answer_df[answer_df.classify__classify_id==p_id]
            arr.append(p_name)

            p_ans=p_ans[['answer','comments','question_id','red_flag','file']]
            # p_ans['file']=file_data
            p_ans = p_ans.replace({np.nan: None})

            p_ans[p_name]=p_ans.to_dict('records')

            p_ans=p_ans[[p_name,'question_id']]
            
            question_df = pd.merge(question_df, p_ans, how="left", left_on='id', right_on='question_id')
        question_df['ref_id']=question_df['ref_id'].fillna(0)
        question_df = question_df.replace({np.nan: None})

        sub_q_arr=[]
        for row in question_df.index:
            ref_id= question_df['ref_id'][row]
            q_id = question_df['id'][row]
            arr1=[]
            if ref_id==None:
                arr1=question_df.loc[question_df['ref_id']==q_id].to_dict('records')
            sub_q_arr.append(arr1)

        question_df['sub_question']=sub_q_arr
        # question_df['ref_id'].replace({None:0})
        # question_df=np.where((question_df['ref_id']==None))
        # question_df=question_df.loc[question_df['ref_id']==0]
        question_df = question_df[question_df.ref_id == 0]

        a=question_df.to_dict('records')
        data={"header":arr,"data":a}
        b=json.dumps(data)
        return b

    def evaluator(self, project_id, request):
        api_serv = cms_api_service.ApiService(self._scope())
        # project type
        type_id = request.GET.get('type_id')
        if type_id != None:
            q_type = [type_id]
        else:
            project_type = api_serv.get_proquesmap_id(project_id)
            q_type = api_serv.get_questype(project_type)

        question_data = api_serv.get_ques(q_type)
        # question dataframe
        question_df = pd.DataFrame(question_data.values('id', 'text', 'ref_id'))
        # question_df = question_df.rename({"text": "question"}, axis=1)
        # p_ans = p_ans.rename({'comments': 'text'}, axis=1)
        question_df['question'] = question_df[['text']].to_dict(orient='records')

        qid_arr = [i.id for i in question_data]
        cls = Quesansservice(self._scope())
        proposal_info = cls.get_finalized_proposal_info(project_id)
        proposal_arr = [p['id'] for p in proposal_info]
        answer_data = self.get_question_answer(proposal_arr, qid_arr)
        ansid_arr = [i['id'] for i in answer_data]

        # file
        q_file_df = pd.DataFrame(columns=['id', 'rel_id', 'rel_type'])
        docu_df = pd.DataFrame(columns=['a_id', 'file'])
        if len(ansid_arr) > 0:
            q_file = CMSDocuments.objects.using(self._current_app_schema()).filter(rel_id__in=ansid_arr,rel_type=DocUtil.Questionnaire,status=ActiveStatus.Active).values(
                'id', 'rel_id', 'rel_type')
            file_relid = list(set([j['rel_id'] for j in q_file]))
            if len(q_file) > 0:
                q_file_df = pd.DataFrame(q_file)
                q_file_df['file_key'] = cms_file_key() + q_file_df['id'].astype(str)

                for row in file_relid:
                    arr1 = q_file_df.loc[q_file_df['rel_id'] == row].to_dict('records')
                    data1 = {"a_id": row, "file": arr1}
                    docu_df = docu_df.append(data1, ignore_index=True)

        # answer dataframe
        if len(answer_data) > 0:
            answer_df = pd.DataFrame(answer_data)
        else:
            answer_df = pd.DataFrame(columns=['classify__classify_id', 'id', 'question_id', 'answer', 'question_type'])

        # comments dataframe
        comments_df = pd.DataFrame(columns=['comments', 'red_flag', 'score', 'answer_id'])
        if len(ansid_arr) > 0:
            ans_comments = AnswerMapping.objects.using(self._current_app_schema()).filter(answer_id__in=ansid_arr,
                                                                                          status=ActiveStatus.Active).values(
                'comments', 'red_flag', 'score', 'answer_id')
            if len(ans_comments) > 0:
                comments_df = pd.DataFrame(ans_comments)

        answer_df = pd.merge(answer_df, comments_df, how="left", left_on='id', right_on='answer_id')

        answer_df = pd.merge(answer_df, docu_df, how='left', left_on='id', right_on='a_id')

        arr ,arr_dup = ['question'],['question']
        evl='Evaluator'
        for p in proposal_info:
            p_id = p['id']
            p_name = p['name']
            p_ans = answer_df[answer_df.classify__classify_id == p_id]
            # arr.append(p_name)
            ans_evl =p_name+"_evl"

            arr += [p_name,evl]
            arr_dup +=[p_name,ans_evl]
            p_ans = p_ans.replace({np.nan: None})
            p_ans = p_ans[['answer', 'comments', 'question_id', 'red_flag', 'file']]
            p_ans = p_ans.rename({'answer':'text'},axis=1)
            # columns=[]
            p_ans[p_name] = p_ans[['red_flag', 'file','text']].to_dict(orient='records')
            p_ans = p_ans.rename({'comments':'text'},axis=1)
            p_ans[ans_evl] = p_ans[['text']].to_dict(orient='records')

            dict_ans_df=p_ans[[p_name,'question_id']]
            dict_cmt_df=p_ans[[ans_evl,'question_id']]

            # p_ans = p_ans.replace({np.nan: None})
            p_ans[p_name] = p_ans.to_dict('records')

            question_df = pd.merge(question_df, dict_ans_df, how="left", left_on='id', right_on='question_id')
            question_df = pd.merge(question_df, dict_cmt_df, how="left", left_on='id', right_on='question_id')

        # question_df['ref_id'] = question_df['ref_id'].fillna(0)
        question_df = question_df.replace({np.nan: None})

        sub_q_arr = []
        for row in question_df.index:
            ref_id = question_df['ref_id'][row]
            q_id = question_df['id'][row]
            arr1 = []
            if ref_id == None:
                arr1 = question_df.loc[question_df['ref_id'] == q_id].to_dict('records')
            sub_q_arr.append(arr1)

        question_df['sub_question'] = sub_q_arr
        # question_df['ref_id'].replace({None:0})
        # question_df=np.where((question_df['ref_id']==None))
        # question_df=question_df.loc[question_df['ref_id']==0]
        question_df = question_df[question_df.ref_id != None]
        columns=arr_dup+['sub_question']
        question_df=question_df[columns]
        a = question_df.to_dict('records')
        data = {"header": arr, "data": a,"dup_header":arr_dup}
        b = json.dumps(data)
        return b

    # version approval tran get
    def get_approvaltran_data(self, project_id, tran_type):
        proj_app = ProjectApprovalTran.objects.using(self._current_app_schema()).filter(
                                                        project_id=project_id,
                                                        tran_type=tran_type, status=ActiveStatus.Active)
        proj_appdata = []
        for i in proj_app:
            proj_appdata.append(i.__dict__)
        return proj_appdata

    def get_proposalapprovaltran_data(self, proposal_id, tran_type):
        prop_app = ProposedContractApprovalTran.objects.using(self._current_app_schema()).filter(
                                                        proposed_id=proposal_id,
                                                        tran_type=tran_type, status=ActiveStatus.Active)
        prop_appdata = []
        for i in prop_app:
            prop_appdata.append(i.__dict__)
        return prop_appdata

# Vow History:

from userservice.controller.vowusercontroller import VowUser


class VowCmsApprovalService:
    def __init__(self, request):
        vowuser_info = VowUser().get_user(request)

        self.emp_id = vowuser_info['user_id']
        self.entity_id = vowuser_info['entity_id']
        self.is_user = vowuser_info['is_user']
        self.schema = vowuser_info['schema']

    #  vow Proposal create QUEUE INSERT
    # def vow_proposal_createtran(self, proposed_id):
    #     c_obj = ProposedContractApprovalTran.objects.using(self.schema).create(
    #         proposed_id=proposed_id, tran_type=Trantype.creator,
    #         to_type=TranApproverType.employee, to=self.emp_id, order=0,
    #         tran_status=TranStatus.creator, created_by=self.emp_id,
    #         created_date=timezone.now(), is_user=self.is_user)
    #     return c_obj

    # APPROVAL proposed HISTORY
    def vow_proposal_tranhistory(self, request, proposed_id, vys_page):
        obj = ProposedContractTranComments.objects.using(self.schema).filter(proposed_id=proposed_id,
                                                                             status=ActiveStatus.Active
                                                                             ).order_by('created_date')[
              vys_page.get_offset():vys_page.get_query_limit()]
        arr = NWisefinList()
        approver_list = [i.approver for i in obj]
        approver_data = ApiService(request.scope).get_multi_emp(request, approver_list)

        for i in obj:
            resp_obj = ApprovalHistoryResponse()
            resp_obj.set_id(i.id)
            resp_obj.set_approver(i.approver, approver_data)
            resp_obj.set_comments(i.comments)
            resp_obj.set_approval_status(i.approval_status)
            arr.append(resp_obj)
            vpage = NWisefinPaginator(obj, vys_page.get_index(), 10)
            arr.set_pagination(vpage)
        return arr
