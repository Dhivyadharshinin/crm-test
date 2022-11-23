from django.core import signing
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from rest_framework import status
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from userservice.data.request.employeeaccountrequest import EmployeeAccountDetailsRequest
from userservice.service.employeeaccountdetailsservice import EmployeeAccountDetailsService
from userservice.service.employeeservice import EmployeeService
from utilityservice.service.api_service import ApiService
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from rest_framework.permissions import IsAuthenticated
import json
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpage import NWisefinPage
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_employee_account(request):
    if request.method == 'POST':
        scope=request.scope
        employee_service =EmployeeAccountDetailsService(scope)
        emp_data = json.loads(request.body)
        # user_id = request.user.id
        user_id=request.employee_id
        emp_obj = EmployeeAccountDetailsRequest(emp_data)
        resp_obj = employee_service.create_employee_account_details(emp_obj, user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    if request.method=='GET':
        return fetch_employee_account_summary(request)


def fetch_employee_account_summary(request):
    scope = request.scope
    empl_service = EmployeeAccountDetailsService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    emp_id=request.employee_id
    # user_id = request.user.id
    resp_obj = empl_service.fetch_employee_account_summary(request,vys_page,emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


# @csrf_exempt
@api_view(['GET','POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def employee_get(request):
       if request.method == 'GET':
        scope=request.scope
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        employee_service = EmployeeAccountDetailsService(scope)
        resp_obj = employee_service.employee_get(request,vys_page)
        return HttpResponse(resp_obj.get(), content_type='application/json')
@csrf_exempt
@api_view(['GET'])
def employee_paymode_get(request):
    if request.method == 'GET':
        scope=request.scope
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        api_serv = ApiService(scope)
        resp_obj = api_serv.get_paymodeList(request,vys_page)
        # employee_service = EmployeeAccountDetailsService(scope)
        # resp_obj = employee_service.employee_paymode_get(request,vys_page)
        return HttpResponse(resp_obj.get(), content_type='application/json')
@csrf_exempt
@api_view(['GET'])

def employee_bank(request):
    if request.method == 'GET':
        scope=request.scope
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        api_serv = ApiService(scope)
        data =request.GET.get('data')
        resp_obj = api_serv.get_bankList(data,vys_page)
        return HttpResponse(resp_obj.get(), content_type='application/json')
@csrf_exempt
@api_view(['GET'])
def employee_bankbranch(request,bank_id):
    if request.method == 'GET':
        scope=request.scope
        page = request.GET.get('page', 1)
        page = int(page)
        emp_id = request.employee_id
        vys_page = NWisefinPage(page, 10)
        api_serv = ApiService(scope)
        query = request.GET.get('data')
        resp_obj = api_serv.get_bankbranch_search(query,bank_id,vys_page)
        return HttpResponse(resp_obj.get(), content_type='application/json')


@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def employeeaccount_active_inactivate(request):
    if request.method == 'POST':
        scope=request.scope

        taxrate_service = EmployeeAccountDetailsService(scope)
        # user_id = request.user.id
        emp_data = json.loads(request.body)
        emp_obj = EmployeeAccountDetailsRequest(emp_data)
        emp_service = EmployeeService(scope)
        # empid = emp_service.get_empid_from_userid(user_id)
        emp_id=request.employee_id
        resp_obj = taxrate_service.employeeaccount_active_inactivate(request,emp_obj,emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response