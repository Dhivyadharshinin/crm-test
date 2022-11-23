import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from userservice.data.request.hierarchyrequest import HierarchyRequest
from userservice.service.hierarchyservice import HierarchyService
from utilityservice.data.response.nwisefinpage import NWisefinPage

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def employeehierarchy(request):
    if request.method == 'POST':
        scope=request.scope
        hierarchy_service = HierarchyService(scope)
        hierarchy_data = json.loads(request.body)
        user_id = request.user.id
        hierarchy_obj = HierarchyRequest(hierarchy_data)
        resp_obj = hierarchy_service.create_hierarchy(hierarchy_obj, user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_employeehierarchy_list(request)


def fetch_employeehierarchy_list(request):
    scope=request.scope
    hierarchy_service = HierarchyService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    user_id = request.employee_id
    data = request.GET.get('data')
    resp_obj = hierarchy_service.fetch_hierarchy_list(vys_page,data)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_employeehierarchy(request,employeehierarchy_id):
    if request.method == 'GET':
        scope=request.scope
        hierarchy_service = HierarchyService(scope)
        user_id = request.employee_id
        resp_obj = hierarchy_service.fetch_hierarchy(employeehierarchy_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_employeehierarchy(request,employeehierarchy_id)


@csrf_exempt
def delete_employeehierarchy(request,employeehierarchy_id):
    scope=request.scope
    hierarchy_service = HierarchyService(scope)
    resp_obj = hierarchy_service.delete_hierarchy(employeehierarchy_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
