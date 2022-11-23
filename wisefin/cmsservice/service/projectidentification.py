import datetime
from django.db.models import Q
from django.db.models.aggregates import Max
from django.utils import timezone
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.cms_api_service import ApiService
from utilityservice.service.threadlocal import NWisefinThread
from cmsservice.data.response.cmsapprovalresponse import ApprovalTranHistoryResponse
from cmsservice.data.response.projectidentification_response import ProjectIdentification_Response
from cmsservice.service.cmsapprovalservice import CmsApprovalService
from cmsservice.service.cmscommonservice import CommonService
from cmsservice.service.codegenhistoryservice import Codegenservice
from cmsservice.service.projecttypeservice import ProjectTypeService
from cmsservice.util.cmsutil import CodePrefix, TranApproverType, TranStatus, Trantype, ActiveStatus, DocUtil, \
    SearchUtil, ApprovalStatus, HistoryStatus
from cmsservice.models.cmsmodels import ProjectidentificationApprovalTran, ProjectTranComments, \
    ProjectIdentification
from cmsservice.data.request.projectidentification_request import ProjectIndentification_Request


class Project_Identification_Service(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.CMS_SERVICE)

    def project_identification(self, request, project_data, employee_id):
        fun = ProjectIndentification_Request(project_data)
        if fun.get_id() != None:
            table = ProjectIdentification.objects.using(self._current_app_schema()).filter(id=fun.get_id()).update(
                title=fun.get_title(), type=fun.get_type(), onbehalf_group=fun.get_onbehalf_group(),
                updated_by=employee_id, updated_date=datetime.datetime.now())

            table = ProjectIdentification.objects.using(self._current_app_schema()).get(id=fun.get_id())
        else:
            table_type = CodePrefix.ProjectIdentification
            codegen_service = Codegenservice(self._scope())
            code_gen = codegen_service.codegen(table_type, employee_id)
            table = ProjectIdentification.objects.using(self._current_app_schema()).create(
                title=fun.get_title(), type=fun.get_type(), onbehalf_group=fun.get_onbehalf_group(),
                approval_status=ApprovalStatus.PENDING,
                created_by=employee_id, created_date=datetime.datetime.now(), code=code_gen)

        pr_data = ProjectIdentification_Response()
        pr_data.set_id(table.id)
        pr_data.set_code(table.code)
        pr_data.set_title(table.title)
        return table

    def project_identification_fetch(self, request, vys_page):
        fetch = ProjectIdentification.objects.using(self._current_app_schema()).filter(status=1).all()[
                vys_page.get_offset():vys_page.get_query_limit()]
        pr_list_data = NWisefinList()
        for data in fetch:
            resp = ProjectIdentification_Response()
            resp.set_id(data.id)
            resp.set_code(data.code)
            resp.set_title(data.title)
            resp.set_type(data.type)
            resp.set_onbehalf_group(data.onbehalf_group)
            resp.set_approval_status(data.approval_status)
            resp.set_parallel_approval(data.parallel_approval)
            resp.set_status(data.status)
            resp.set_is_user(data.is_user)
            resp.set_created_by(data.created_by)
            resp.set_created_date(data.created_date)
            resp.set_updated_date(data.updated_date)
            pr_list_data.append(resp)
        vpage = NWisefinPaginator(fetch, vys_page.get_index(), 10)
        pr_list_data.set_pagination(vpage)
        return pr_list_data

    def project_identication_get(self, id, employee_id, request):
        type = DocUtil.project_identification
        data = ProjectIdentification.objects.using(self._current_app_schema()).get(id=id, status=1)
        projecttype_service = ProjectTypeService(self._scope())
        common_service = CommonService(self._scope())
        apiserv = ApiService(self._scope())
        approval_serv = CmsApprovalService(self._scope())
        resp = ProjectIdentification_Response()
        resp.set_id(data.id)
        resp.set_code(data.code)
        resp.set_title(data.title)
        resp.set_type(projecttype_service.fetch_projecttype(data.type))
        resp.set_approval_status(data.approval_status)
        resp.set_parallel_approval(data.parallel_approval)
        resp.set_status(data.status)
        resp.set_onbehalf_group(apiserv.get_group_info_by_id(data.onbehalf_group))
        attach_pr = common_service.attachement_project(data.id, type)
        covernote_pr = common_service.covernote_project(data.id, type)
        grup_list = apiserv.grouplist_by_empid(employee_id)

        if data.created_by == employee_id:
            resp.is_created_by = True
        else:
            resp.is_created_by = False
        resp.covernote = covernote_pr
        resp.filedata = attach_pr
        approver = self.project_identification_approver_list(request, data.id)
        pending_approver = CommonService(self._scope()).get_pending_grp(grup_list, approver)
        resp.pending_approver = pending_approver
        resp.approver = approver
        return resp

    def project_identication_tran_get(self, id):
        data = ProjectidentificationApprovalTran.objects.using(self._current_app_schema()).get(id=id, status=1)
        pr_list_data = NWisefinList()
        resp = ProjectIdentification_Response()
        resp.set_project_identification(data.project_identification)
        resp.set_id(data.id)
        resp.set_tran_type(data.tran_type)
        resp.set_to(data.to)
        resp.set_to_type(data.to_type)
        resp.set_tran_status(data.tran_status)
        resp.set_order(data.order)
        resp.set_status(data.status)
        resp.set_created_by(data.created_by)
        resp.set_created_date(data.created_date)
        resp.set_updated_date(data.updated_date)
        resp.set_updated_by(data.updated_by)
        resp.set_is_user(data.is_user)
        pr_list_data.append(resp)
        return pr_list_data

    def pro_tran_approval(self, data, project_id, emp_id):
        to_arr = data['to_arr']

        val_to_arr = sorted(set(to_arr), key=to_arr.index)
        if to_arr != val_to_arr:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description("INVAILD APPROVER")
            e = {"app_resp": False, "obj": error_obj}
            return e

        # if to_type == TranApproverType.employee:
        #     if emp_id in to_arr:
        #         error_obj = NWisefinError()
        #         error_obj.set_code(ErrorMessage.INVALID_DATA)
        #         error_obj.set_description("Maker can't be Approver")
        #         e = {"app_resp": False, "obj": error_obj}
        #         return e
        # proj_tab=ProjectidentificationApprovalTran.objects.filter(project_identification_id=project_id,status=ActiveStatus.Active)
        q_order = 1
        arr = []
        # if len(proj_tab)!=0:
        # created by me in tran
        c_obj = ProjectidentificationApprovalTran(project_identification_id=project_id, tran_type=Trantype.creator,to_type=TranApproverType.employee, to=emp_id, order=0,tran_status=TranStatus.creator, created_by=emp_id, created_date=timezone.now())
        arr.append(c_obj)

        for i in to_arr:
            if q_order == 1:
                tran_status = TranStatus.pending
            else:
                tran_status = TranStatus.awaiting

            obj = ProjectidentificationApprovalTran(project_identification_id=project_id, tran_type=Trantype.approver, to_type=TranApproverType.group, to=i,order=q_order, tran_status=tran_status, created_by=emp_id,created_date=timezone.now())
            arr.append(obj)
            q_order += 1

        ProjectidentificationApprovalTran.objects.bulk_create(arr)
        ProjectTranComments.objects.using(self._current_app_schema()).create(rel_id=project_id,
                                                                             rel_type=DocUtil.project_identification, approver=emp_id,
                                                                             comments=None, created_by=emp_id,
                                                                             created_date=timezone.now(),
                                                                             approval_status=HistoryStatus.CREATED)

        e = {"app_resp": True, "obj": None}
        return e

    def project_identification_approval(self, request, data, project_identification_id, emp_id):
        approval_status = data['status']
        remarks = data['remarks']
        approver = None
        if 'approver' in data:
            approver = data['approver']

        # approval status validation
        if approval_status in [TranStatus.approved, TranStatus.rejected, TranStatus.reviwed]:
            pass
        else:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description("INVAILD STATUS")
            return error_obj

        emp_grp = ApiService(request.scope).grouplist_by_empid(emp_id)
        obj = ProjectidentificationApprovalTran.objects.using(self._current_app_schema()).filter(
            status=ActiveStatus.Active, project_identification_id=project_identification_id,
            tran_type__in=[Trantype.approver])

        approver_arr, approved_arr, total_arr, arr = [], [], [], []
        is_approver = False
        current_tran_status = None
        for i in obj:
            approver_arr.append(i.to)
            if i.to_type == TranApproverType.employee:
                if (emp_id == i.to) and (i.tran_status == TranStatus.pending):
                    current_order = i.order
                    current_tran_status = i.tran_status
                    d = {"id": i.id, "transtatus": approval_status}
                    arr.append(d)
                    is_approver = True
            elif i.to_type == TranApproverType.group:
                if (i.to in emp_grp) and (i.tran_status == TranStatus.pending):
                    current_order = i.order
                    current_tran_status = i.tran_status
                    d = {"id": i.id, "transtatus": approval_status}
                    arr.append(d)
                    is_approver = True
        if current_tran_status != TranStatus.pending:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description("INVAILD APPROVER")
            return error_obj
        # current approver validation
        if is_approver == False:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description("INVAILD APPROVER")
            return error_obj
        # if parallel_approver ==False:
        if approver != None and approval_status == TranStatus.approved:
            if approver == None or approver == "":
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description("Please Choose Approver")
                return error_obj
            if (approver in approver_arr) or emp_id == approver:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description("INVAILD APPROVER")
                return error_obj

            ProjectidentificationApprovalTran.objects.using(self._current_app_schema()).create(
                project_identification_id=project_identification_id, order=(current_order + 1),
                tran_type=Trantype.approver, tran_status=TranStatus.pending, to=approver,
                to_type=TranApproverType.group, created_by=emp_id)

            ProjectidentificationApprovalTran.objects.using(self._current_app_schema()).filter(
                project_identification_id=project_identification_id, order=current_order,
                tran_status=TranStatus.pending).update(tran_status=approval_status, updated_date=timezone.now(),
                                                       updated_by=emp_id)


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
                ProjectIdentification.objects.using(self._current_app_schema()).filter(
                    id=project_identification_id).update(
                    approval_status=TranStatus.approved, updated_date=timezone.now(), updated_by=emp_id)

        elif approval_status == TranStatus.reviwed:
            # for j in obj:
            #     if j.order == 1:
            #         d = {"id": j.id, "transtatus": TranStatus.pending}
            #         arr.append(d)
            #     elif j.order > 1:
            #         d = {"id": j.id, "transtatus": TranStatus.awaiting}
            #         arr.append(d)
            ProjectIdentification.objects.using(self._current_app_schema()).filter(id=project_identification_id).update(
                approval_status=TranStatus.reviwed, updated_date=timezone.now(), updated_by=emp_id)

        elif approval_status == TranStatus.rejected:
            ProjectIdentification.objects.using(self._current_app_schema()).filter(id=project_identification_id).update(
                approval_status=TranStatus.rejected, updated_date=timezone.now(), updated_by=emp_id)

        for j in arr:
            ProjectidentificationApprovalTran.objects.using(self._current_app_schema()).filter(id=j['id']).update(
                tran_status=j['transtatus'], updated_date=timezone.now(), updated_by=emp_id)

        ProjectTranComments.objects.using(self._current_app_schema()).create(approver=emp_id, comments=remarks,
                                                                             created_by=emp_id,
                                                                             rel_id=project_identification_id,
                                                                             rel_type=DocUtil.project_identification,
                                                                             approval_status=approval_status)

        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message("Successfully Approved")
        return success_obj

    def project_identification_list(self, scope, vys_page, emp_id, request):
        condition = Q(project_identification__status=ActiveStatus.Active)
        approval_status = request.GET.get('approval_status')
        is_project = request.GET.get('is_project', True)
        # NON - CREATION PROJECT VALIDATION
        if is_project == '0':
            project_created = [False]
        else:
            project_created = [True, False]
        title = request.GET.get('title')
        apiserv = ApiService(scope)
        emp_group = apiserv.grouplist_by_empid(emp_id)
        # approval_status
        if (approval_status is not None) & (approval_status != ''):
            approval_status = int(approval_status)
            if approval_status == SearchUtil.PendingApproval:
                condition &= ((Q(tran_status=TranStatus.pending) & Q(to=emp_id) & Q(
                    to_type=TranApproverType.employee)) | (Q(tran_status=TranStatus.pending) & Q(to__in=emp_group) & Q(
                    to_type=TranApproverType.group))) & ~Q(project_identification__created_by=emp_id)
            elif approval_status == SearchUtil.CreatedByMe:
                condition &= Q(tran_status=TranStatus.creator) & Q(to=emp_id)
            elif approval_status == SearchUtil.ApprovedByMe:
                condition &= Q(tran_status=TranStatus.approved) & Q(updated_by=emp_id)
            elif approval_status == SearchUtil.RejectedByMe:
                condition &= Q(tran_status=TranStatus.rejected) & Q(updated_by=emp_id)
            elif approval_status == SearchUtil.FullApproved:
                condition &= Q(tran_status=TranStatus.approved) & Q(
                    project_identification__approval_status=ApprovalStatus.APPROVED) & Q(order=1)
                condition &= Q(project_identification__is_project__in=project_created)
            elif approval_status == SearchUtil.ReturnByMe:
                condition &= Q(tran_status=TranStatus.reviwed) & Q(updated_by=emp_id)
            elif approval_status == SearchUtil.PendingReview:
                condition &= Q(tran_status=TranStatus.reviwed) & Q(project_identification__created_by=emp_id)
            # elif approval_status == SearchUtil.CreatedByGroup:
            #     condition &= Q(tran_status=TranStatus.creator) & Q(to__in=emp_group)& Q(order=0)
            else:
                condition &= Q(status=-1)
        else:
            condition &= (Q(tran_status=TranStatus.pending) & Q(to=emp_id) & Q(to_type=TranApproverType.employee)) | (
                    Q(tran_status=TranStatus.pending) & Q(to__in=emp_group) & Q(
                to_type=TranApproverType.group)) & ~Q(project_identification__created_by=emp_id)

        # code, title, projecttype, date
        if (title is not None) & (title != ''):
            condition &= Q(project_identification__title__icontains=title) | Q(
                project_identification__code__icontains=title)

        print("project - condition ", condition)
        # prjlist = ProjectidentificationApprovalTran.objects.using(
        #     self._current_app_schema()).filter(condition).order_by('-created_date')[
        #           vys_page.get_offset():vys_page.get_query_limit()]
        #
        prjlist1 = ProjectidentificationApprovalTran.objects.filter(condition).values("project_identification__id").annotate(id=Max('id')).order_by(
            '-project_identification_id')[vys_page.get_offset():vys_page.get_query_limit()]
        arr = []
        for i in prjlist1:
            arr.append(i["id"])
        prjlist = ProjectidentificationApprovalTran.objects.filter(id__in=arr).order_by('-created_date')

        type_arr = [i.project_identification.type for i in prjlist]
        project_identificationtype_service = ProjectTypeService(scope)
        type_data = project_identificationtype_service.get_projecttype_info(type_arr)

        pr_list_data = NWisefinList()
        for prhdr in prjlist:
            pr_data = ProjectIdentification_Response()
            pr_data.set_id(prhdr.project_identification_id)
            pr_data.set_project_identification(prhdr.id)
            pr_data.set_projecttype(prhdr.project_identification.type, type_data)
            pr_data.set_code(prhdr.project_identification.code)
            pr_data.set_title(prhdr.project_identification.title)
            pr_data.set_approval_status(prhdr.project_identification.approval_status)
            pr_data.set_is_user(prhdr.project_identification.is_user)
            pr_data.set_onbehalf_group(prhdr.project_identification.onbehalf_group)
            pr_list_data.append(pr_data)
        vpage = NWisefinPaginator(prjlist, vys_page.get_index(), 10)
        pr_list_data.set_pagination(vpage)
        return pr_list_data

    def projectidentification_parallel_app(self, product_id, employee_id):
        proj_ide_tab = ProjectIdentification.objects.using(self._current_app_schema()).filter(id=product_id,
                                                                                              approval_status=ApprovalStatus.APPROVED)
        if len(proj_ide_tab) != 0:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description("INVAILD APPROVER")
            return error_obj

        proj_ide_tab1 = ProjectIdentification.objects.using(self._current_app_schema()).filter(id=product_id,
                                                                                               created_by=employee_id)
        proj_ide_tab2 = ProjectIdentification.objects.using(self._current_app_schema()).filter(parallel_approval=False)
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

        proj_ide_t1 = ProjectidentificationApprovalTran.objects.using(self._current_app_schema()).filter(
            project_identification_id=product_id, tran_status=TranStatus.awaiting).update(
            tran_status=TranStatus.pending)
        proj_ide_t2 = ProjectIdentification.objects.using(self._current_app_schema()).filter(id=product_id).update(
            parallel_approval=True)

        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)

        success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        return success_obj

    def project_identification_approver_list(self, request, project_id):
        cond = Q(project_identification_id=project_id) & Q(status=ActiveStatus.Active) & ~Q(order=0)
        obj = ProjectidentificationApprovalTran.objects.using(self._current_app_schema()).filter(cond)
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

    def project_ide_resubmit(self, identification_id, employee_id):
        proj_ide = ProjectIdentification.objects.using(self._current_app_schema()).get(id=identification_id)
        if proj_ide.approval_status != ApprovalStatus.REVIEW:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description("CAN'T RESUBMIT")
            return error_obj
        if proj_ide.created_by != employee_id:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description("CAN'T RESUBMIT")
            return error_obj
        ProjectIdentification.objects.using(self._current_app_schema()).filter(id=identification_id).update(
            approval_status=ApprovalStatus.PENDING)

        if proj_ide.parallel_approval !=True:
            condition=Q(project_identification_id=identification_id)
            condition&=~Q(order=0)
            condition&=~Q(order=1)
            ProjectidentificationApprovalTran.objects.using(self._current_app_schema()).filter(
                project_identification_id=identification_id, order=1).update(
                tran_status=TranStatus.pending, updated_by=employee_id, updated_date=timezone.now())
            ProjectidentificationApprovalTran.objects.using(self._current_app_schema()).filter(
                condition).update(
                tran_status=TranStatus.awaiting, updated_by=employee_id, updated_date=timezone.now())
        else:
            condition = Q(project_identification_id=identification_id)
            condition &= ~Q(order=0)
            ProjectidentificationApprovalTran.objects.using(self._current_app_schema()).filter(
                condition).update(
                tran_status=TranStatus.pending, updated_by=employee_id, updated_date=timezone.now())

        ProjectTranComments.objects.using(self._current_app_schema()).create(rel_id=identification_id,
                                                                             rel_type=DocUtil.project_identification, approver=employee_id,
                                                                             comments=None, created_by=employee_id,
                                                                             created_date=timezone.now(),
                                                                             approval_status=HistoryStatus.RESUBMITTED)

        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.UPDATE_MESSAGE)
        return success_obj

    def projectidentificationclosure(self,project_id,arr):
        projectidentification = ProjectIdentification.objects.filter(id__in=arr,
                                                    is_project=False,
                                                    project_id=None,
                                                    approval_status=HistoryStatus.APPROVED)
        if len(arr) != len(projectidentification):
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description("INVALID DATA")
            return error_obj
        data = ProjectIdentification.objects.using(self._current_app_schema()).filter(id__in=arr).update(is_project=True,project_id=project_id)
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        return success_obj