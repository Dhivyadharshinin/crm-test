import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from masterservice.service.apexpenseservice import APexpenseService
from masterservice.data.request.apexpenserequest import APexpenseRequest
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from utilityservice.data.response.nwisefinpage import NWisefinPage
from userservice.service.employeeservice import EmployeeService
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_expense(request):
    if request.method == 'POST':
        expe_obj = json.loads(request.body)
        expense_obj = APexpenseRequest(expe_obj)
        user_id = request.employee_id
        scope = request.scope
        emp_service = EmployeeService(scope)
        empid = emp_service.get_empid_from_userid(user_id)
        expenseservice = APexpenseService(scope)
        resp_obj = expenseservice.create_expense(expense_obj, empid)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
       return fetch_expense_list(request)
def fetch_expense_list(request):
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        scope = request.scope
        expenseservice = APexpenseService(scope)
        resp_obj = expenseservice.fetch_expense_list(vys_page)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_expense(request,expense_id):
    if request.method == 'GET':
        scope = request.scope
        expenseservice = APexpenseService(scope)
        resp_obj = expenseservice.fetch_expense(expense_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_expense(request,expense_id)
def delete_expense(request, expense_id):
    user_id = request.employee_id
    scope = request.scope
    expenseservice = APexpenseService(scope)
    resp_obj = expenseservice.delete_expense(expense_id,user_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def search_expense(request):
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    query = request.GET.get('query')
    scope = request.scope
    expenseservice = APexpenseService(scope)
    resp_obj = expenseservice.search_expense(query, vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response



@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def expense_code_update(request):
    if request.method == 'POST':
        expe_obj = json.loads(request.body)
        for i in expe_obj['expense_list']:
            scope = request.scope
            expenseservice = APexpenseService(scope)
            resp_obj = expenseservice.apexpence_code_update(i)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response