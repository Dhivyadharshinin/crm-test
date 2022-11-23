import json

from django.db import transaction
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from cmsservice.data.request.projectrequest import ProjectRequest
from cmsservice.service.cmsapprovalservice import CmsApprovalService
from cmsservice.service.cmscommonservice import CommonService
from cmsservice.service.historyservice import Historyservice
from cmsservice.service.projectinvitationservice import ProjectInvitationService
from cmsservice.service.projectservice import ProjectService, VowProjectService
from cmsservice.service.proposerservice import ProposerService
from cmsservice.util.cmsutil import get_fileextension_val, DocUtil, dd_SearchUtil, conversion, project_viewtype, \
    CovernoteUtil, VersionDataType
from docservice.service.documentservice import DocumentsService
from docservice.util.docutil import DocModule
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess,SuccessStatus
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission


# CRUD
@transaction.atomic()
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_project(request):
    if request.method == 'POST':
        project_data = json.loads(request.data.dict().get('data'))
        scope = request.scope
        emp_id = scope['employee_id']
        project_obj = ProjectRequest(project_data)
        project_service = ProjectService(scope)
        proj_app_service = CmsApprovalService(scope)
        common_service = CommonService(scope)
        history_serv = Historyservice(scope)
        attach_type = DocUtil.project

        # remove file while update
        if ("id" in project_data) & ("file_remove" in project_data):
            project_id = project_data.get("id")
            file_remove = project_data.get("file_remove")
            file_remove_len = len(file_remove)
            if file_remove_len > 0:
                removeattach_resp = common_service.remove_prjattachement(project_id, file_remove, emp_id)
                print("removeattach_resp", removeattach_resp)

        # validation
        if 'id' not in project_data:
            val = project_service.project_identification_validation(project_obj)
            if val == False:
                transaction.set_rollback(True)
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_PROJECT_ID)
                error_obj.set_description(ErrorDescription.INVALID_PROJECT_ID)
                response = HttpResponse(error_obj.get(), content_type="application/json")
                return response

        # project create
        response_obj = project_service.create_project(project_obj, emp_id, scope)
        project_id = response_obj.id

        # choose approval
        is_draft=project_obj.get_is_draft()
        approval = project_data.get("approval")
        collaborator = project_data.get("collaborator")
        q_approval = project_data.get("proposal_approver")
        parallel_approval = project_data["parallel_approval"]
        if "id" not in project_data:
            # proj - app
            app_resp_obj = proj_app_service.project_approval_queue(approval, project_id, emp_id, is_draft)

            # proj - coll
            collab_queue = proj_app_service.collaborator_queue(collaborator, project_id, emp_id)

            # proposal - app
            q_approval_queue = proj_app_service.q_approval_queue(q_approval, project_id, emp_id, parallel_approval)

            if not app_resp_obj['app_resp']:
                print("app_resp_obj['app_resp'] : ", app_resp_obj['app_resp'])
                transaction.set_rollback(True)
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                response = HttpResponse(app_resp_obj.get(), content_type="application/json")
                return response
            if not collab_queue['app_resp']:
                print("app_resp_obj['app_resp'] : ", app_resp_obj['app_resp'])
                transaction.set_rollback(True)
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                response = HttpResponse(app_resp_obj.get(), content_type="application/json")
                return response
            if not q_approval_queue['app_resp']:
                print("app_resp_obj['app_resp'] : ", app_resp_obj['app_resp'])
                transaction.set_rollback(True)
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                response = HttpResponse(app_resp_obj.get(), content_type="application/json")
                return response

        # covernote & upload
        content_type = CovernoteUtil.project
        doc_service = DocumentsService(scope)
        docmodule_obj = DocModule()
        params = dict()
        params['module'] = docmodule_obj.CMS
        params['ref_id'] = project_id
        params['ref_type'] = docmodule_obj.CMS

        doc_type = project_data.get("type")
        project_content = project_data.get('content')

        # covernote
        covernote_create_resp = common_service.covernote_create(project_id, content_type, project_content, emp_id)

        # strategy_note
        if 'strategy_note' in project_data:
            strategy_note = project_data.get('strategy_note')
            content_strategy_type = CovernoteUtil.project_strategy
            covernote_strategy_resp = common_service.covernote_create(project_id, content_strategy_type, strategy_note, emp_id)

        file_len = len(request.FILES.getlist('file'))
        if file_len > 0:
            for i in request.FILES.getlist('file'):
                file_name = i.name
                extension = file_name.split('.')[-1]
                filetype_check = get_fileextension_val(extension)
                if filetype_check is False:
                    transaction.set_rollback(True)
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVALID_FILETYPE)
                    error_obj.set_description(ErrorDescription.INVALID_FILETYPE)
                    response = HttpResponse(error_obj.get(), content_type="application/json")
                    return HttpResponse(response, content_type='application/json')
            # upload project document
            resp_obj = doc_service.upload(request, params)
            document_json = json.loads(resp_obj.get())['data']
            response_obj1 = common_service.updateprojectattachement(document_json, project_id, attach_type, doc_type,
                                                                    emp_id)
        # invitation
        project_invitation = project_data.get('invitation')
        if "id" not in project_data:
            if len(project_invitation) > 0:
                invi_serv = ProjectInvitationService(scope)
                invi_resp = invi_serv.projectinvitation(project_id, project_invitation, emp_id)
                print("invi_resp", invi_resp)
            else:
                transaction.set_rollback(True)
                error_obj = NWisefinError()
                error_obj.set_code("Kindly share Invitation Details")
                error_obj.set_description("Kindly share Invitation Details")
                response = HttpResponse(error_obj.get(), content_type='application/json')
                return response

        if "id" not in project_data:
            project_version = history_serv.projectversion_insert(request, project_id, emp_id)

        success_obj = NWisefinSuccess()
        success_obj.set_status("Success")
        success_obj.set_message("Created Successfully")
        success_obj.project_id = project_id
        response = HttpResponse(success_obj.get(), content_type='application/json')
        return response
    elif request.method == 'GET':
        return fetch_project_list(request)


def fetch_project_list(request):
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    scope = request.scope
    project_service = ProjectService(scope)
    emp_id = scope['employee_id']
    response_obj = project_service.fetch_project_list(scope, vys_page, emp_id, request)
    response = HttpResponse(response_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_project(request, project_id):
    if request.method == 'GET':
        scope = request.scope
        emp_id = scope['employee_id']
        project_service = ProjectService(scope)
        resp_obj = project_service.fetch_project(request, project_id, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_project(request, project_id)


def delete_project(request, project_id):
    scope = request.scope
    project_service = ProjectService(scope)
    emp_id = scope['employee_id']
    resp_obj = project_service.delete_project(project_id, emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


# projectclose
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def updateprojectclose(request, project_id):
    scope = request.scope
    project_service = ProjectService(scope)
    emp_id = scope['employee_id']
    resp_obj = project_service.updateprojectclose(project_id, emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


# summary_approvedproject for vow
@api_view(['GET'])
def vow_project(request):
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    vow_project_service = VowProjectService(request)
    resp_obj = vow_project_service.summary_vowproject(vys_page, request)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@api_view(['GET'])
def vow_fetchproject(request, project_id):
    vow_project_service = VowProjectService(request)
    resp_obj = vow_project_service.fetch_vowproject(project_id, request)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_approvalstatus(request, id):
    resp_obj = dd_SearchUtil(id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def conv_dt(request, id):
    scope = request.scope
    project_service = ProjectService(scope)
    resp_obj = project_service.get_project(id)
    p_date = resp_obj
    resp_obj = conversion(p_date)
    print("date convs", resp_obj)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_viewtype(request):
    resp_obj = project_viewtype()
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def project_viewsummary(request, project_id):
    scope = request.scope
    project_service = Historyservice(scope)
    emp_id = scope['employee_id']
    response_obj = project_service.project_viewsummary(request, project_id, scope, emp_id)
    response = HttpResponse(response_obj.get(), content_type="application/json")
    return response


@transaction.atomic()
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def project_parallel_app(request, project_id):
    scope = request.scope
    emp_id = scope['employee_id']
    approval_service = ProjectService(scope)
    resp_obj = approval_service.project_parallel_app(project_id, emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def project_version(request, project_id):
    scope = request.scope
    project_service = Historyservice(scope)
    response_obj = project_service.project_version(project_id)
    response = HttpResponse(response_obj.get(), content_type="application/json")
    return response


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def approval_status_search(request):
    type = [DocUtil.project, DocUtil.proposer]
    vyslist = NWisefinList()
    for i in type:
        resp_obj = dd_SearchUtil(i)
        if i == DocUtil.project:
            project = {"name": DocUtil.project_val, "value": json.loads(resp_obj.get())["data"]}
        elif i == DocUtil.proposer:
            project = {"name": DocUtil.proposer_val, "value": json.loads(resp_obj.get())["data"]}
        vyslist.append(project)
    response = HttpResponse(vyslist.get(), content_type="application/json")
    return response


@transaction.atomic
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def project_resubmit(request, project_id):
    if request.method == "POST":
        scope = request.scope
        employee_id = request.employee_id
        project_service = ProjectService(scope)
        history_serv = Historyservice(scope)
        resp_obj = project_service.project_resubmit(project_id, employee_id)
        project_version = history_serv.projectversion_insert(request, project_id, employee_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@transaction.atomic
@api_view(['POST', 'GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def project_finalizecovernote(request, project_id):
    if request.method == "POST":
        project_data = json.loads(request.body)
        content = project_data['content']
        scope = request.scope
        emp_id = scope['employee_id']
        # covernote
        content_type = CovernoteUtil.proposal_finalize
        common_service = CommonService(scope)
        proposer_service = ProposerService(scope)
        proposalcheck_resp = proposer_service.check_finalizeproposal(project_id)
        if proposalcheck_resp == False:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_PROJECT_ID)
            error_obj.set_description("This Project is Not Finalized Any Proposal, Kindly Check")
            response = HttpResponse(error_obj.get(), content_type="application/json")
            return response
        covernote_create_resp = common_service.covernote_create(project_id, content_type, content, emp_id)
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        response = HttpResponse(success_obj.get(), content_type='application/json')
        return response

    elif request.method == "GET":
        scope = request.scope
        # covernote
        content_type = CovernoteUtil.proposal_finalize
        common_service = CommonService(scope)
        resp_obj = common_service.covernote_project(project_id, content_type)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@transaction.atomic()
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def new_evaluator(request,project_id):
    scope = request.scope
    emp_id = scope['employee_id']
    proj_app_service = CmsApprovalService(scope)
    service=proj_app_service.evaluator(project_id,request)
    response = HttpResponse(service, content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def project_qtype(request,project_id):
    proj_app_service = CmsApprovalService(request.scope)
    service = proj_app_service.project_qtype(project_id)
    response = HttpResponse(service, content_type="application/json")
    return response