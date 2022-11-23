import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from masterservice.data.request.bankdetailsrequest import BankDetailsRequest
from masterservice.service.bankdetailsservice import BankDetailsService
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from utilityservice.data.response.nwisefinpage import NWisefinPage
from userservice.service.employeeservice import EmployeeService


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def bank_details(request):
    if request.method == 'POST':
        scope = request.scope
        bankdtls_service = BankDetailsService(scope)
        bank_data = json.loads(request.body)
        user_id = request.employee_id
        bank_obj = BankDetailsRequest(bank_data)
        # emp_service = EmployeeService(scope)
        # emp_id = emp_service.get_empid_from_userid(user_id)
        resp_obj = bankdtls_service.create_bankdetails(bank_obj, user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_bankdetails_list(request)


def fetch_bankdetails_list(request):
    scope = request.scope
    bankdtl_service = BankDetailsService(scope)
    user_id = request.employee_id
    # emp_service = EmployeeService(scope)
    # emp_id = emp_service.get_empid_from_userid(user_id)
    page = request.GET.get('page', 1)
    account_no = request.GET.get('account_no', None)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = bankdtl_service.fetch_bankdetails_list(vys_page,account_no,user_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_bankdetails(request,bankdetails_id):
    if request.method == 'GET':
        scope = request.scope
        bankdtls_service = BankDetailsService(scope)
        user_id = request.employee_id
        emp_service = EmployeeService(scope)
        emp_id = emp_service.get_empid_from_userid(user_id)
        resp_obj = bankdtls_service.fetch_bankdetails(bankdetails_id,emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_bankdetails(request,bankdetails_id)


def delete_bankdetails(request,bankdetails_id):
    scope=request.scope
    bankdtls_service = BankDetailsService(scope)
    user_id = request.employee_id
    emp_service = EmployeeService(scope)
    emp_id = emp_service.get_empid_from_userid(user_id)
    resp_obj = bankdtls_service.delete_bankdetails(bankdetails_id,emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response