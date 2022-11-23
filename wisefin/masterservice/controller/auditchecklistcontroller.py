import json

from masterservice.service.auditchecklistservice import AuditChecklistService
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_apauditchecklist_mapping(request):
    if request.method == 'POST':
        from utilityservice.service import api_service
        data = json.loads(request.body)
        scope = request.scope
        audit_chklist=AuditChecklistService(scope)
        emp_id = request.employee_id
        response_obj = audit_chklist.create_audit_check_list(data, emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response