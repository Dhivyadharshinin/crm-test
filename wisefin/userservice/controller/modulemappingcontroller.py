import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from userservice.data.request.modulerequest import ModuleResquest
from userservice.service.modulemappingservice import ModuleMappingService
from utilityservice.permissions.filter.urlpermission import UrlPermission


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission, UrlPermission])
def modulemapping(request, moduleuser_id):
    if request.method == 'POST':
        scope = request.scope
        modulemapping_service = ModuleMappingService(scope)
        module_data = json.loads(request.body)
        method = module_data.get('method')
        if method == "add" :
            resp_obj = modulemapping_service.addmodule(moduleuser_id,module_data)
        elif method == "remove" :
            resp_obj = modulemapping_service.removemodule(moduleuser_id,module_data)

        response = HttpResponse(resp_obj, content_type="application/json")
        return response

    elif request.method == 'GET':
        scope = request.scope
        modulemapping_service = ModuleMappingService(scope)
        resp_obj = modulemapping_service.listmodule(moduleuser_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission, UrlPermission])
def module_order(request):
    if request.method == 'POST':
        scope = request.scope
        modulemapping_service = ModuleMappingService(scope)
        module_data = json.loads(request.body)
        resp_obj = modulemapping_service.module_order(module_data)
        response = HttpResponse(resp_obj, content_type="application/json")
        return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def module_order_assinging(request):
    if request.method == 'POST':
        scope = request.scope
        emp_id = request.employee_id
        module_data = json.loads(request.body)
        module_mapping_serv = ModuleMappingService(scope)
        res_obj = module_mapping_serv.module_order_assinging(emp_id, module_data)
        response = HttpResponse(res_obj.get(), content_type="application/json")
        return response


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def assign_module(request):
    if request.method == 'POST':
        scope = request.scope
        emp_id = request.employee_id
        module_data = json.loads(request.body)
        module_mapping_ser = ModuleMappingService(scope)
        res_obj = module_mapping_ser.assign_module(emp_id, module_data)
        response = HttpResponse(res_obj.get(), content_type="application/json")
        return response



