import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from userservice.data.request.modulerequest import ModuleResquest
from userservice.service.moduleservice import ModuleService
from userservice.service.roleemployeeservice import RoleEmployeeService
from utilityservice.permissions.filter.urlpermission import UrlPermission
import time


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission,UrlPermission])
def module(request):
    if request.method == 'POST':
        scope = request.scope
        module_service = ModuleService(scope)
        module_data = json.loads(request.body)
        user_id = request.employee_id
        module_obj = ModuleResquest(module_data)
        resp_obj = module_service.create_module(module_obj, user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_module_list(request)


def fetch_module_list(request):
    scope = request.scope
    module_service = ModuleService(scope)
    user_id = request.employee_id
    resp_obj = module_service.fetch_module_list()
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission,UrlPermission])
def fetch_module(request,module_id):
    if request.method == 'GET':
        t1 = time.time()
        scope = request.scope
        module_service = ModuleService(scope)
        user_id = request.employee_id
        resp_obj = module_service.fetch_module(module_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        t2 = time.time()
        return response
    elif request.method == 'DELETE':
        return delete_module(request,module_id)


@csrf_exempt
def delete_module(request,module_id):
    scope = request.scope
    module_service = ModuleService(scope)
    resp_obj = module_service.delete_module(module_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission,UrlPermission])
def fetch_submodule(request,module_id):
    if request.method == 'GET':
        scope = request.scope
        module_service = ModuleService(scope)
        # user_id = request.employee_id
        resp_obj = module_service.fetch_submodule(module_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

# admin
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def module_admin(request):
    if request.method == 'POST':
        scope = request.scope
        module_service = ModuleService(scope)
        module_data = json.loads(request.body)
        user_id = request.employee_id
        module_obj = ModuleResquest(module_data)
        resp_obj = module_service.create_module(module_obj, user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_module_list(request)


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_module_admin(request,module_id):
    if request.method == 'GET':
        t1 = time.time()
        scope = request.scope
        module_service = ModuleService(scope)
        user_id = request.employee_id
        resp_obj = module_service.fetch_module(module_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        t2 = time.time()
        return response
    elif request.method == 'DELETE':
        return delete_module(request,module_id)

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def employee_modulerole(request):
    scope = request.scope
    roleemployee_service = RoleEmployeeService(scope)
    module_data = json.loads(request.body)
    employee_id=module_data['employee_id']
    module=module_data['module']
    resp_obj = roleemployee_service.fetch_employee_role(employee_id, module)
    json_object = json.dumps(resp_obj, indent=4)
    response = HttpResponse(json_object, content_type="application/json")
    return response
