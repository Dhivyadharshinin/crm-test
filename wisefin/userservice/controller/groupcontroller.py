import json
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.cms_api_service import ApiService
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from userservice.data.request.employeegrouprequest import EmpGroupRequest,GroupPermissionResquest
from userservice.service.groupservice import GroupService
from userservice.data.userutil import get_group_list

@transaction.atomic
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_employee_group(request):
    if request.method == 'POST':
        employee_group_data = json.loads(request.body)
        employee_group_req = EmpGroupRequest(employee_group_data)
        scope = request.scope
        employee_group_service = GroupService(scope)
        api_serv = ApiService(scope)
        emp = api_serv.get_emp_id(request)
        emp_id = emp['id']
        response_obj = employee_group_service.create_employee_group(employee_group_req, emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response
    elif request.method == 'GET':
        return fetch_employee_group_list(request)

def fetch_employee_group_list(request):
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    scope = request.scope
    employee_group_service = GroupService(scope)
    response_obj = employee_group_service.fetch_employee_group_list(vys_page, request)
    response = HttpResponse(response_obj.get(), content_type="application/json")
    return response

@transaction.atomic
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def mapping_employee_group(request):
    if request.method == 'POST':
        group_data = json.loads(request.body)
        scope = request.scope
        employee_group_service = GroupService(scope)
        api_serv = ApiService(scope)
        emp = api_serv.get_emp_id(request)
        emp_id = emp['id']
        is_remove = request.GET.get('is_remove')

        response_obj = employee_group_service.mapping_employee_group(group_data, emp_id,is_remove)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_employee_by_groupid(request,group_id):
    if request.method == 'GET':
        scope = request.scope
        employee_group_service = GroupService(scope)
        response_obj = employee_group_service.get_employee_by_group_id(group_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_group_by_empid(request,employee_id):
    if request.method == 'GET':
        scope = request.scope
        employee_group_service = GroupService(scope)
        response_obj = employee_group_service.get_group_by_employee_id(employee_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_group_role(request):
    if request.method == 'GET':
        response_obj = get_group_list()
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def employee_group_fetch(request):
    if request.method == 'GET':
        response_obj = get_group_list()
        scope=request.scope
        employee_group_service = GroupService(scope)
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        type = request.GET.get('type',0)
        name = request.GET.get('name')
        employee_id=request.employee_id
        response_obj = employee_group_service.employee_group_fetch(type,vys_page,name,request)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response



@transaction.atomic
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def group_employee(request):
    scope = request.scope
    employee_group_service = GroupService(scope)
    api_serv = ApiService(scope)
    emp = api_serv.get_emp_id(request)
    emp_id = emp['id']
    response_obj = employee_group_service.group_employee(emp_id, request)
    response = HttpResponse(response_obj.get(), content_type='application/json')
    return response


@transaction.atomic
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def group_employeeall(request):
    scope = request.scope
    employee_group_service = GroupService(scope)
    api_serv = ApiService(scope)
    emp = api_serv.get_emp_id(request)
    emp_id = emp['id']
    response_obj = employee_group_service.group_employeeall(emp_id)
    response = HttpResponse(response_obj.get(), content_type='application/json')
    return response