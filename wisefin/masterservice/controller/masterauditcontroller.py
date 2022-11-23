import json
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from masterservice.service.masterauditservice import MasterAuditService
from masterservice.data.request.masterauditrequest import MasterAuditRequest




@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def masteraudit(request):
    if request.method == 'POST':
        scope=request.scope
        audit_service = MasterAuditService(scope)
        audit_data = json.loads(request.body)
        user_id = request.employee_id
        audit_obj = MasterAuditRequest(audit_data)
        resp_obj = audit_service.create_audit(audit_obj)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_audit_list(request)


def fetch_audit_list(request):
    scope = request.scope
    audit_service = MasterAuditService(scope)
    user_id = request.employee_id
    resp_obj = audit_service.fetch_audit_list(user_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_masteraudit(request,audit_id):
    if request.method == 'GET':
        scope=request.scope
        audit_service = MasterAuditService(scope)
        user_id = request.employee_id
        resp_obj = audit_service.fetch_masteraudit(audit_id,user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_audit(request,audit_id)


@csrf_exempt
def delete_audit(request,audit_id):
    scope = request.scope
    audit_service = MasterAuditService(scope)
    user_id = request.employee_id
    resp_obj = audit_service.delete_audit(audit_id,user_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response