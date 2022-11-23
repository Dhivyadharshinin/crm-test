import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from userservice.data.request.rolerequest import RoleEmployeeResquest,RoleModuleResquest
from userservice.service.roleemployeeservice import RoleEmployeeService
from userservice.service.employeeservice import EmployeeService
from userservice.service.roleservice import RoleService
import time
from utilityservice.permissions.filter.urlpermission import UrlPermission


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission, UrlPermission])
def roleemployee(request):
    if request.method == 'POST':
        scope = request.scope
        roleemployee_service = RoleEmployeeService(scope)
        roleemployee_data = json.loads(request.body)
        user_id = request.employee_id
        roleemployee_obj = RoleEmployeeResquest(roleemployee_data)
        resp_obj = roleemployee_service.create_roleemployee(roleemployee_obj, user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_roleemployee_list(request)


def fetch_roleemployee_list(request):
    scope = request.scope
    roleemployee_service = RoleEmployeeService(scope)
    user_id = request.employee_id
    resp_obj = roleemployee_service.fetch_roleemployee_list()
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

#  fetch and delete role
@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission,UrlPermission])
def fetch_role(request,employee_id):
    if request.method == 'GET':
        t1 = time.time()
        scope = request.scope
        roleemployee_service = RoleEmployeeService(scope)
        user_id = request.employee_id
        resp_obj = roleemployee_service.fetch_role(employee_id)
        scope = request.scope
        role_service = RoleService(scope)
        role_array=[]
        for role_id in resp_obj :
            role = role_service.fetch_role(role_id)
            role_array.append(role.get())
        response = HttpResponse(role_array, content_type="application/json")
        t2 = time.time()
        return response
    elif request.method == 'DELETE':
        return delete_employee(request,employee_id)


@csrf_exempt
def delete_role(request,employee_id):
    scope = request.scope
    roleemployee_service = RoleEmployeeService(scope)
    resp_obj = roleemployee_service.delete_role(employee_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


#  fetch and delete  employee
@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission,UrlPermission])
def fetch_employee(request,role_id):
    if request.method == 'GET':
        t1 = time.time()
        scope = request.scope
        roleemployee_service = RoleEmployeeService(scope)
        user_id = request.employee_id
        resp_obj = roleemployee_service.fetch_employee(role_id)

        employee_service = EmployeeService(scope)
        emp_array=[]
        for id in resp_obj :
            emp_id = id
            employee = employee_service.get_employee(emp_id,user_id)
            emp_array.append(employee.get())
        response = HttpResponse(emp_array, content_type="application/json")
        t2 = time.time()
        return response
    elif request.method == 'DELETE':
        return delete_employee(request,role_id)


@csrf_exempt
def delete_employee(request,role_id):
    scope = request.scope
    roleemployee_service = RoleEmployeeService(scope)
    resp_obj = roleemployee_service.delete_employee(role_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission,UrlPermission])
def permission(request):
    if request.method == 'POST':
        scope = request.scope
        roleemployee_service = RoleEmployeeService(scope)
        roleemployee_data = json.loads(request.body)
        roleemployee_obj = RoleModuleResquest(roleemployee_data)
        user_id = request.employee_id
        resp_obj = roleemployee_service.role_module_employee(roleemployee_obj,user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission, UrlPermission])
def employee_module(request,employee_id):
    if request.method == 'GET':
        scope = request.scope
        roleemployee_service = RoleEmployeeService(scope)
        user_id = request.employee_id
        resp_obj = roleemployee_service.fetch_employee_module(employee_id, user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission,UrlPermission])
def fetch_employee_modulerole(request,module_id,role_id):
    if request.method == 'GET':
        scope = request.scope
        roleemployee_service = RoleEmployeeService(scope)
        user_id = request.employee_id
        resp_obj = roleemployee_service.fetch_employee_modulerole(role_id,module_id, user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


# @csrf_exempt
# @api_view(['POST'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def start_migrations(request):
#     if request.method == 'POST':
#         scope = request.scope
#         roleemployee_service = RoleEmployeeService(scope)
#         user_id = request.user.id
#         resp_obj = roleemployee_service.start_migrations(user_id)
#         response = HttpResponse(resp_obj.get(), content_type="application/json")
#         return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def employee_submodule(request):
    if request.method == 'GET':
        scope = request.scope
        roleemployee_service = RoleEmployeeService(scope)
        user_id = request.employee_id
        userid_check = True
        resp_obj = roleemployee_service.fetch_employee_submodule(user_id,userid_check)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def employee_submodule_empid(request,employee_id):
    if request.method == 'GET':
        scope = request.scope
        roleemployee_service = RoleEmployeeService(scope)
        userid_check = False
        resp_obj = roleemployee_service.fetch_employee_submodule(employee_id,userid_check)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

# admin
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def permission_admin(request):
    if request.method == 'POST':
        scope = request.scope
        roleemployee_service = RoleEmployeeService(scope)
        roleemployee_data = json.loads(request.body)
        roleemployee_obj = RoleModuleResquest(roleemployee_data)
        user_id = request.employee_id
        resp_obj = roleemployee_service.role_module_employee(roleemployee_obj,user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def employee_submodule_admin(request,employee_id):
    if request.method == 'GET':
        scope = request.scope
        roleemployee_service = RoleEmployeeService(scope)
        userid_check = False
        resp_obj = roleemployee_service.fetch_employee_submodule(employee_id,userid_check)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def permission_all(request):
    if request.method == 'POST':
        scope = request.scope
        roleemployee_service = RoleEmployeeService(scope)
        roleemployee_data = json.loads(request.body)
        # roleemployee_obj = RoleModuleResquest(roleemployee_data)
        user_id = request.employee_id
        resp_obj = roleemployee_service.premission_all(roleemployee_data,user_id)
        response = HttpResponse("permission given", content_type="application/json")
        return response

# @csrf_exempt
# @api_view(['post'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def permission_remove(request):
#     roleemployee_service = RoleEmployeeService()
#     user_id = request.user.id
#     data = json.loads(request.body)
#     resp_obj = roleemployee_service.premission_remove(data)
#     response = HttpResponse("permission removed", content_type="application/json")
#     return response


# @csrf_exempt
# @api_view(['post'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def rems_permission(request):
#     roleemployee_service = RoleEmployeeService()
#     user_id = request.user.id
#     data = json.loads(request.body)
#     roleemployee_obj = RoleModuleResquest(data)
#     resp_obj = roleemployee_service.rems_premission(roleemployee_obj,user_id)
#     response = HttpResponse("permission given", content_type="application/json")
#     return response
