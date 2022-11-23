import json
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from userservice.service.employeeservice import EmployeeService
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from vendorservice.service.bankbranchservice import BankBranchService
from vendorservice.data.request.bankbranchrequest import BankBranchRequest


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def bankbranch(request):
    if request.method == 'POST':
        scope = request.scope
        bankbranch_service = BankBranchService(scope)
        bankbranch_data = json.loads(request.body)
        user_id = request.employee_id
        bankbranch_obj = BankBranchRequest(bankbranch_data)
        resp_obj = bankbranch_service.create_bankbranch(bankbranch_obj, user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_bankbranch_list(request)


def fetch_bankbranch_list(request):
    scope = request.scope
    bankbranch_service = BankBranchService(scope)
    user_id = request.employee_id
    resp_obj = bankbranch_service.fetch_bankbranch_list(user_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_bankbranch(request,bankbranch_id):
    if request.method == 'GET':
        scope = request.scope
        bankbranch_service = BankBranchService(scope)
        user_id = request.employee_id
        resp_obj = bankbranch_service.fetch_bankbranch(bankbranch_id,user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_bankbranch(request,bankbranch_id)


@csrf_exempt
def delete_bankbranch(request,bankbranch_id):
    scope = request.scope
    bankbranch_service = BankBranchService(scope)
    resp_obj = bankbranch_service.delete_bankbranch(bankbranch_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
