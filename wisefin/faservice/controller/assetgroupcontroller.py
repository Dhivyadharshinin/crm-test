from django.http import HttpResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from faservice.data.request.assetlocationrequest import AssetLocationRequest
from faservice.service.assetdetailsservice import AssetDetailsService
from faservice.service.assetgroupservice import AssetGroupService
from faservice.service.assetlocationservice import AssetLocationService
# from userservice.service.employeeservice import EmployeeService
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
import json
from utilityservice.data.response.nwisefinpage import NWisefinPage

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_assetgroup(request):
    if request.method == 'POST':
        pass
        # assetlocation_json = json.loads(request.body)
        # assetlocation_obj = AssetLocationRequest(assetlocation_json)
        # user_id = request.user.id
        # emp_id=request.employee_id
        # resp_obj = assetlocation_serv.create_assetlocation(assetlocation_obj, emp_id)
        # response = HttpResponse(resp_obj.get(), content_type="application/json")
        # return response
    elif request.method == 'GET':
        return fetch_assetgroup_list(request._request)

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_assetgroup_list(request):
    scope=request.scope
    user_id = request.user.id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    query = request.GET.get('query', None)
    assetgroup_serv = AssetGroupService(scope)
    resp_obj = assetgroup_serv.fetch_assetgroup_list(query, vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_assetgroup(request):
    user_id = request.user.id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    query = request.GET.get('query', None)
    assetgroup_serv = AssetGroupService(scope)
    resp_obj = assetgroup_serv.fetch_assetgroup(query)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_assetgroup_assetid(request):
    user_id = request.user.id
    scope = request.scope
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    query = request.GET.get('query', None)
    assetgroup_serv = AssetGroupService(scope)
    resp_obj = assetgroup_serv.fetch_assetgroup_asset(query)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response