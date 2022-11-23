import json
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from userservice.service.employeeservice import EmployeeService
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from vendorservice.service.vendorauditservice import VendorAuditService
from vendorservice.data.request.vendorauditrequest import VendorAuditRequest


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def vendoraudit(request):
    if request.method == 'POST':
        scope = request.scope
        vendoraudit_service = VendorAuditService(scope)
        vendoraudit_data = json.loads(request.body)
        employee_id = request.employee_id
        vendoraudit_obj = VendorAuditRequest(vendoraudit_data)
        resp_obj = vendoraudit_service.create_vendoraudit(vendoraudit_obj)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_vendoraudit_list(request)


def fetch_vendoraudit_list(request):
    scope = request.scope
    vendoraudit_service = VendorAuditService(scope)
    employee_id = request.employee_id
    resp_obj = vendoraudit_service.fetch_vendoraudit_list(employee_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_vendoraudit(request,vendoraudit_id):
    if request.method == 'GET':
        scope = request.scope
        vendoraudit_service = VendorAuditService(scope)
        employee_id = request.employee_id
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        resp_obj = vendoraudit_service.fetch_vendoraudit(vendoraudit_id,employee_id,vys_page)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_vendoraudit(request,vendoraudit_id)


@csrf_exempt
def delete_vendoraudit(request,vendoraudit_id):
    scope = request.scope
    vendoraudit_service = VendorAuditService(scope)
    employee_id = request.employee_id
    resp_obj = vendoraudit_service.delete_vendoraudit(vendoraudit_id,employee_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
