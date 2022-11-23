import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from rest_framework.decorators import authentication_classes, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from cmsservice.service.proposerservice import ProposerService
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from cmsservice.service.cmsapprovalservice import CmsApprovalService, VowCmsApprovalService


@csrf_exempt
@transaction.atomic
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def project_status_update(request, project_id):
    data = json.loads(request.body)
    scope = request.scope
    emp_id = scope['employee_id']
    approval_service = CmsApprovalService(scope)
    resp_obj = approval_service.project_status_update(request, data, project_id, emp_id)
    response = HttpResponse(resp_obj.get(), content_type='application/json')
    return response


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def project_approval_history(request, project_id):
    scope = request.scope
    approval_service = CmsApprovalService(scope)
    rel_type = request.GET.get('rel_type',None)
    resp_obj = approval_service.get_project_approver_history(request, project_id,rel_type)
    response = HttpResponse(resp_obj.get(), content_type='application/json')
    return response


@transaction.atomic
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def proposed_status_update(request, proposal_id):
    data = json.loads(request.body)
    scope = request.scope
    emp_id = scope['employee_id']
    approval_service = CmsApprovalService(scope)
    resp_obj = approval_service.proposed_status_update(request, data, proposal_id, emp_id)
    response = HttpResponse(resp_obj.get(), content_type='application/json')
    return response


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def proposed_approval_history(request, proposed_id):
    scope = request.scope
    approval_service = CmsApprovalService(scope)
    resp_obj = approval_service.get_proposed_approver_history(request, proposed_id)
    response = HttpResponse(resp_obj.get(), content_type='application/json')
    return response

@api_view(['GET'])
def vow_proposal_tranhistory(request, proposal_id):
    pr_service = VowCmsApprovalService(request)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    response_obj = pr_service.vow_proposal_tranhistory(request, proposal_id, vys_page)
    response = HttpResponse(response_obj.get(), content_type="application/json")
    return response


@transaction.atomic
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def assign_proposed(request, project_id):
    scope = request.scope
    emp_id = scope['employee_id']
    data = json.loads(request.body)
    approval_service = CmsApprovalService(scope)
    proposed_id = request.GET.get('proposed_id')
    if proposed_id is None:
        resp_obj = approval_service.assign_proposed(data, project_id, emp_id, scope)
    else:
        resp_obj = approval_service.assign_proposedexact(data, project_id, proposed_id, emp_id, scope)
    response = HttpResponse(resp_obj.get(), content_type='application/json')
    return response


# PROPOSAL SHORTLIST/ UNDO SHORTLIST
@transaction.atomic
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def proposal_shortlist(request):
    data = json.loads(request.body)
    scope = request.scope
    emp_id = scope['employee_id']
    approval_service = CmsApprovalService(scope)
    resp_obj = approval_service.proposal_shortlist(data, emp_id, request)
    response = HttpResponse(resp_obj.get(), content_type='application/json')
    return response


# PROPOSAL FINALIZE
@transaction.atomic
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def proposal_shortlistfinalize(request):
    data = json.loads(request.body)
    scope = request.scope
    emp_id = scope['employee_id']
    approval_service = CmsApprovalService(scope)
    resp_obj = approval_service.proposal_shortlistfinalize(data, emp_id)
    response = HttpResponse(resp_obj.get(), content_type='application/json')
    return response


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def shortlist_proposer_list(request, project_id):
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    scope = request.scope
    prop_serv = ProposerService(scope)
    response_obj = prop_serv.shortlist_proposer_list(vys_page, project_id, request)
    response = HttpResponse(response_obj.get(), content_type="application/json")
    return response


@transaction.atomic
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def proposal_parallel_approver(request,project_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        scope = request.scope
        employee_id = request.employee_id
        approval_service = CmsApprovalService(scope)
        resp_obj = approval_service.proposal_parallel_approver(project_id, employee_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


# @transaction.atomic
# @csrf_exempt
# @api_view(['POST'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def project_proposal_approval(request,project_id):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         scope = request.scope
#         employee_id = request.employee_id
#         approval_service = CmsApprovalService(scope)
#         resp_obj = approval_service.project_proposal_approval(request, data, project_id, employee_id)
#         response = HttpResponse(resp_obj.get(), content_type="application/json")
#         return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def move_to_finalapprover(request,project_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        scope = request.scope
        employee_id = request.employee_id
        approval_service = CmsApprovalService(scope)
        resp_obj = approval_service.move_to_proposal_approval(data, project_id, employee_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response