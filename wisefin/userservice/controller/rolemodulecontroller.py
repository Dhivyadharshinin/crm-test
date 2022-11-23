import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from userservice.data.request.rolerequest import RoleModuleResquest
from userservice.service.rolemoduleservice import RoleModuleService
from userservice.service.moduleservice import ModuleService
from userservice.service.roleservice import RoleService
import time
from utilityservice.permissions.filter.urlpermission import UrlPermission


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission,UrlPermission])
def rolemodule(request):
    if request.method == 'POST':
        scope = request.scope
        rolemodule_service = RoleModuleService(scope)
        rolemodule_data = json.loads(request.body)
        user_id = request.employee_id
        rolemodule_obj = RoleModuleResquest(rolemodule_data)
        resp_obj = rolemodule_service.create_rolemodule(rolemodule_obj, user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_rolemodule_list(request)


def fetch_rolemodule_list(request):
    scope = request.scope
    rolemodule_service = RoleModuleService(scope)
    user_id = request.employee_id
    resp_obj = rolemodule_service.fetch_rolemodule_list()
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

#  fetch and delete role

@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission,UrlPermission])
def fetch_role(request,module_id):
    if request.method == 'GET':
        t1 = time.time()
        scope = request.scope
        rolemodule_service = RoleModuleService(scope)
        user_id = request.employee_id
        resp_obj = rolemodule_service.fetch_role(module_id)
        scope = request.scope
        role_service = RoleService(scope)
        role_array = []
        for role_id in resp_obj:
            role = role_service.fetch_role(role_id)
            role_array.append(role.get())

        response = HttpResponse(role_array, content_type="application/json")
        t2 = time.time()
        return response
    elif request.method == 'DELETE':
        return delete_role(request,module_id)


@csrf_exempt
def delete_role(request,module_id):
    scope = request.scope
    rolemodule_service = RoleModuleService(scope)
    resp_obj = rolemodule_service.delete_role(module_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

#  fetch and delete  module

@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission,UrlPermission])
def fetch_module(request,role_id):
    if request.method == 'GET':
        t1 = time.time()
        scope = request.scope
        rolemodule_service = RoleModuleService(scope)
        user_id = request.employee_id
        resp_obj = rolemodule_service.fetch_module(role_id)
        module_array = []
        for module_id in resp_obj:
            scope = request.scope
            module_service = ModuleService(scope)
            module = module_service.fetch_module(module_id)
            module_array.append(module.get())
        response = HttpResponse(module_array, content_type="application/json")
        t2 = time.time()
        return response
    elif request.method == 'DELETE':
        return delete_module(request,role_id)


@csrf_exempt
def delete_module(request,role_id):
    scope = request.scope
    rolemodule_service = RoleModuleService(scope)
    resp_obj = rolemodule_service.delete_module(role_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
