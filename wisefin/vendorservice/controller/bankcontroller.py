import json
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from userservice.service.employeeservice import EmployeeService
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from vendorservice.service.bankservice import BankService
from vendorservice.data.request.bankrequest import BankRequest


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def bank(request):
    if request.method == 'POST':
        scope = request.scope
        bank_service = BankService(scope)
        bank_data = json.loads(request.body)
        user_id = request.employee_id
        bank_obj = BankRequest(bank_data)
        resp_obj = bank_service.create_bank(bank_obj, user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_bank_list(request)


def fetch_bank_list(request):
    scope = request.scope
    bank_service = BankService(scope)
    user_id = request.employee_id
    resp_obj = bank_service.fetch_bank_list(user_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_bank(request,bank_id):
    if request.method == 'GET':
        scope = request.scope
        bank_service = BankService(scope)
        user_id = request.employee_id
        resp_obj = bank_service.fetch_bank(bank_id,user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_bank(request,bank_id)


@csrf_exempt
def delete_bank(request,bank_id):
    scope = request.scope
    bank_service = BankService(scope)
    resp_obj = bank_service.delete_bank(bank_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
