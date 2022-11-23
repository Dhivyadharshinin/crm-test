import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from userservice.service.employeeservice import EmployeeService
from vendorservice.data.request.taxrequest import TaxRequest
from vendorservice.service.vendortaxservice import TaxService
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
#vendor_id
def suppliertax(request,branch_id):
    if request.method == 'POST':
        employee_id = request.employee_id
        scope = request.scope
        #user_id=1
        #bulk = request.GET.get('bulk', False)
        # tax_service = TaxMasterService()
        tax_obj = json.loads(request.body)
        tax_obj=TaxRequest(tax_obj)
        tax_service = TaxService(scope)
        resp_obj = tax_service.create_tax(branch_id, tax_obj, employee_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_tax_list(request,branch_id)


def fetch_tax_list(request, branch_id):
    employee_id = request.employee_id
    scope = request.scope
    director_service = TaxService(scope)
    resp_obj = director_service.fetch_tax_list(branch_id, employee_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_tax(request, branch_id, tax_id):
    if request.method == 'GET':
        employee_id = request.employee_id
        scope = request.scope
        tax_service = TaxService(scope)
        resp_obj = tax_service.fetch_tax(branch_id, employee_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_tax(request, branch_id, tax_id)


def delete_tax(request, branch_id, tax_id):
    employee_id = request.employee_id
    scope = request.scope
    tax_service = TaxService(scope)
    resp_obj = tax_service.delete_tax(branch_id, employee_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

