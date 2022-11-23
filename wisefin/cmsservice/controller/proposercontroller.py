import json
from django.db import transaction
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from cmsservice.data.request.proposerrequest import ProposerRequest
from cmsservice.service.cmsapprovalservice import CmsApprovalService
from cmsservice.service.cmsapprovalservice import VowCmsApprovalService
from cmsservice.service.historyservice import Historyservice, VowHistoryService
from cmsservice.service.proposerservice import ProposerService, VowProposerService
from cmsservice.service.cmscommonservice import CommonService, VowCommonService
from cmsservice.util.cmsutil import get_fileextension_val, DocUtil, CovernoteUtil
from docservice.service.documentservice import DocumentsService, VowDocumentsService
from docservice.util.docutil import DocModule
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission


# CRUD
@transaction.atomic
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_proposer(request, project_id):
    scope = request.scope
    proposer_service = ProposerService(scope)
    common_service = CommonService(scope)
    cms_appr_service = CmsApprovalService(scope)
    if request.method == 'POST':
        proposer_data = json.loads(request.data.dict().get('data'))

        # check if proposal against proposer_code
        if "id" not in proposer_data:
            proposer_code = proposer_data.get("proposer_code")
            proposer_exists = proposer_service.check_proposer(project_id, proposer_code)
            if proposer_exists:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.DUPLICATE_ENTRY)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                response = HttpResponse(error_obj.get(), content_type="application/json")
                return response

        proposer_obj = ProposerRequest(proposer_data)
        scope = request.scope
        emp_id = request.employee_id

        # proposal create
        response_obj = proposer_service.create_proposer(proposer_obj, emp_id, scope)
        proposal_id = response_obj.id

        appresponse_obj = cms_appr_service.proposal_createtran(proposal_id, emp_id, project_id)

        # remove file while update
        if ("id" in proposer_data) & ("file_remove" in proposer_data):
            project_id = proposer_data.get("id")
            file_remove = proposer_data.get("file_remove")
            file_remove_len = len(file_remove)
            if file_remove_len > 0:
                removeattach_resp = common_service.remove_prjattachement(project_id, file_remove, emp_id)

        # covernote & doc-upload
        attach_type = DocUtil.proposer
        content_type = CovernoteUtil.proposer

        doc_service = DocumentsService(scope)
        docmodule_obj = DocModule()
        params = dict()
        params['module'] = docmodule_obj.CMS
        params['ref_id'] = proposal_id
        params['ref_type'] = docmodule_obj.CMS
        doc_type = proposer_data.get("type")
        proposed_content = proposer_data.get('content')

        # covernote
        covernote_create_resp = common_service.covernote_create(proposal_id, content_type, proposed_content, emp_id)

        # attachment remove while update
        file_remove = len(proposer_data.get("file_remove"))
        if file_remove > 0:
            removeattach_resp = common_service.remove_prjattachement(proposal_id, file_remove, emp_id)

        # doc attachment
        file_len = len(request.FILES.getlist('file'))
        if file_len > 0:
            file_key_check = request.FILES.getlist('file')
            if file_key_check is not None:
                for i in request.FILES.getlist('file'):
                    file_name = i.name
                    extension = file_name.split('.')[-1]
                    filetype_check = get_fileextension_val(extension)
                    if filetype_check is False:
                        error_obj = NWisefinError()
                        error_obj.set_code(ErrorMessage.INVALID_FILETYPE)
                        error_obj.set_description(ErrorDescription.INVALID_FILETYPE)
                        response = HttpResponse(error_obj.get(), content_type="application/json")
                        return HttpResponse(response, content_type='application/json')
                resp_obj = doc_service.upload(request, params)
                document_json = json.loads(resp_obj.get())['data']
                response_obj1 = common_service.updateprojectattachement(document_json, proposal_id, attach_type,
                                                                        doc_type, emp_id)
        history_id = proposal_id
        project_id = response_obj.project_id

        entry = Historyservice(scope)
        prjt = entry.proposalhstry(response_obj, history_id, project_id)
        prjtid = prjt.id
        activefile = common_service.updatedfile(proposal_id, attach_type)
        if len(activefile) > 0:
            doch = entry.cmsdochstry(activefile, prjtid)
        dochcvnt = entry.cmscvrhstry(covernote_create_resp, prjtid)
        success_obj = NWisefinSuccess()
        success_obj.set_status("Success")
        success_obj.set_message("Created Successfully")
        response = HttpResponse(success_obj.get(), content_type='application/json')
        return response

    elif request.method == 'GET':
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        emp_id = request.employee_id
        response_obj = proposer_service.fetch_proposer_list(vys_page, project_id, request, emp_id)
        response = HttpResponse(response_obj.get(), content_type="application/json")
        return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_proposer(request, proposal_id):
    scope = request.scope
    proposer_service = ProposerService(scope)
    resp_obj = proposer_service.fetch_proposer(proposal_id, request)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


#  vow api
@transaction.atomic
@csrf_exempt
@api_view(['POST'])
def vow_create_proposer(request, project_id):
    proposer_service = VowProposerService(request)
    common_service = VowCommonService(request)

    if request.method == 'POST':
        proposer_data = json.loads(request.data.dict().get('data'))
        is_update = False
        if "id" in proposer_data:
            is_update=True

        # duplicate validation
        if is_update == False:
            proposer_code = proposer_data.get("proposer_code")
            proposer_exists = proposer_service.vow_check_proposer(proposer_code, project_id)
            print("proposal_exists", proposer_code)
            if proposer_exists:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.DUPLICATE_ENTRY)
                error_obj.set_description(ErrorDescription.INVALID_DATA)
                response = HttpResponse(error_obj.get(), content_type="application/json")
                return response

        # remove file while update
        if (is_update==True) & ("file_remove" in proposer_data):
            project_id = proposer_data.get("id")
            file_remove = proposer_data.get("file_remove")
            file_remove_len = len(file_remove)
            if file_remove_len > 0:
                common_service.vow_remove_prjattachement(project_id, file_remove)

        # proposal insert
        proposer_obj = ProposerRequest(proposer_data)
        response_obj = proposer_service.create_proposer(proposer_obj, project_id, request)
        proposal_id = response_obj.id

        #  QUESTIONNAIRE APPORVER ENTRY
        if is_update ==False:
            proposer_service.proposal_tran_create(project_id, proposal_id)

        # content upload
        attach_type = DocUtil.proposer
        content_type = CovernoteUtil.proposer
        doc_service = VowDocumentsService(request)
        docmodule_obj = DocModule()
        params = dict()
        params['module'] = docmodule_obj.CMS
        params['ref_id'] = proposal_id
        params['ref_type'] = docmodule_obj.CMS
        proposed_content = proposer_data.get('content')

        # covernote
        covernote_create_resp = common_service.vow_covernote_create(proposal_id, content_type, proposed_content)

        file_len = len(request.FILES.getlist('file'))
        if file_len > 0:
            for i in request.FILES.getlist('file'):
                file_name = i.name
                extension = file_name.split('.')[-1]
                filetype_check = get_fileextension_val(extension)
                if filetype_check is False:
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.INVALID_FILETYPE)
                    error_obj.set_description(ErrorDescription.INVALID_FILETYPE)
                    response = HttpResponse(error_obj.get(), content_type="application/json")
                    return HttpResponse(response, content_type='application/json')
            resp_obj = doc_service.upload(request, params)
            document_json = json.loads(resp_obj.get())['data']
            type = -1
            common_service.updateprojectattachement(document_json, proposal_id, attach_type, type)

        #  EXCECUTION NOTE
        if 'execution_note' in proposer_data:
            execution_content = proposer_data.get('execution_note')
            content_type = CovernoteUtil.proposal_execution
            covernote_create_resp = common_service.vow_covernote_create(proposal_id, content_type, execution_content)
        if 'financial_note' in proposer_data:
            finanical_content = proposer_data.get('financial_note')
            content_type = CovernoteUtil.proposal_financial
            covernote_create_resp = common_service.vow_covernote_create(proposal_id, content_type, finanical_content)


        # history_id = proposal_id
        # project_id = response_obj.project_id
        # entry = VowHistoryService(request)
        # prjt = entry.proposalhstry(response_obj, history_id, project_id)
        # prjtid = prjt.id
        # activefile = common_service.vow_updatedfile(proposal_id, attach_type)
        # if len(activefile) > 0:
        #     doch = entry.cmsdochstry(activefile, prjtid)
        # dochcvnt = entry.vow_cmscvrhstry(covernote_create_resp, prjtid)

        success_obj = NWisefinSuccess()
        success_obj.set_status("Success")
        success_obj.set_message("Created Successfully")
        response = HttpResponse(success_obj.get(), content_type='application/json')
        return response

    elif request.method == 'GET':
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        response_obj = proposer_service.fetch_proposer_list(vys_page, project_id)
        response = HttpResponse(response_obj.get(), content_type="application/json")
        return response


@csrf_exempt
@api_view(['GET'])
def vow_fetch_proposer(request, project_id):
    proposer_service = VowProposerService(request)
    proposer_code = request.GET.get('proposer_code')
    resp_obj = proposer_service.fetch_proposer(project_id, proposer_code, request)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@transaction.atomic
@csrf_exempt
@api_view(['POST'])
def vow_cms_notepad(request, proposal_id):
    common_serv = VowCommonService(request)
    content_type = CovernoteUtil.proposer
    obj_data = json.loads(request.body)
    resp_obj = common_serv.vow_create_notepad(proposal_id, obj_data, content_type)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@transaction.atomic
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def cms_notepad(request, proposal_id):
    scope = request.scope
    emp_id = request.employee_id
    common_serv = CommonService(scope)
    content_type = CovernoteUtil.proposer
    obj_data = json.loads(request.body)
    resp_obj = common_serv.create_notepad(proposal_id, obj_data, content_type, emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def proposal_viewsummary(request, proposal_id):
    scope = request.scope
    project_service = Historyservice(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    response_obj = project_service.proposal_viewsummary(request, vys_page, proposal_id)
    response = HttpResponse(response_obj.get(), content_type="application/json")
    return response


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def proposal_version(request, proposal_id):
    scope = request.scope
    project_service = Historyservice(scope)
    response_obj = project_service.proposal_version(proposal_id)
    response = HttpResponse(response_obj.get(), content_type="application/json")
    return response


@api_view(['GET'])
def vow_proposal_version(request, proposal_id):
    project_service = VowHistoryService(request)
    response_obj = project_service.vow_proposal_version(proposal_id)
    response = HttpResponse(response_obj.get(), content_type="application/json")
    return response


@api_view(['GET'])
def vow_proposal_viewsummary(request, proposal_id):
    project_service = VowHistoryService(request)
    response_obj = project_service.vow_proposal_viewsummary(request, proposal_id)
    response = HttpResponse(response_obj.get(), content_type="application/json")
    return response


@transaction.atomic
@api_view(['GET'])
def proposal_submit(request, project_id):
    project_service = VowProposerService(request)
    response_obj = project_service.proposal_submit(project_id, request)
    response = HttpResponse(response_obj.get(), content_type="application/json")
    return response


# @csrf_exempt
# @api_view(['POST'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def questionary_group_list(request, proposal_id):
#     scope = request.scope
#     proposer_service = ProposerService(scope)
#     employee_id = request.employee_id
#     response_obj = proposer_service.questionary_group_list(proposal_id, employee_id)
#     response = HttpResponse(response_obj.get(), content_type="application/json")
#     return response


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def questionary_group_approve(request, proposal_id):
    scope = request.scope
    proposer_service = ProposerService(scope)
    employee_id = request.employee_id
    data = json.loads(request.body)
    response_obj = proposer_service.questionary_group_approval(proposal_id, data, employee_id)
    response = HttpResponse(response_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def vow_questionary_resubmit(request,proposal_id):
    # scope = request.scope
    proposer_service = VowProposerService(request)
    employee_id = request.employee_id
    data = json.loads(request.body)
    response_obj = proposer_service.vow_questionary_resubmit(proposal_id, data)
    response = HttpResponse(response_obj.get(), content_type="application/json")
    return response

@transaction.atomic
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def proposal_return(request,proposal_id):
    if request.method == 'POST':
        scope = request.scope
        proposer_service = ProposerService(scope)
        employee_id = request.employee_id
        obj_data = json.loads(request.body)
        response_obj = proposer_service.proposal_return(proposal_id,employee_id,obj_data)
        response = HttpResponse(response_obj.get(), content_type="application/json")
        return response


@transaction.atomic
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def proposal_report(request):
    prop_service = ProposerService(request.scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    emp_id = request.employee_id
    proposer_code = request.GET.get('proposer_code')
    response_obj = prop_service.proposal_report(request, vys_page, proposer_code, emp_id)
    response = HttpResponse(response_obj.get(), content_type="application/json")
    return response


@transaction.atomic
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def approved_proposal(request):
    prop_service = ProposerService(request.scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    response_obj = prop_service.approved_proposal(request, vys_page)
    response = HttpResponse(response_obj.get(), content_type="application/json")
    return response