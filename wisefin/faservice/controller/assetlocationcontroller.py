from django.http import HttpResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from faservice.data.request.assetlocationrequest import AssetLocationRequest
from faservice.service.assetlocationservice import AssetLocationService
from faservice.util.FaApiService import FaApiService
from nwisefin.settings import logger
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
import json
from utilityservice.data.response.nwisefinpage import NWisefinPage


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_assetlocation(request):
    if request.method == 'POST':
        scope = request.scope
        emp_service=FaApiService(scope)
        assetlocation_json = json.loads(request._request.body.decode('utf-8'))
        logger.info('FAL_ASSETCAT_DATA:{}'.format(assetlocation_json))
        assetlocation_obj = AssetLocationRequest(assetlocation_json)
        user_id = request.user.id
        emp_id=request.employee_id
        assetlocation_serv = AssetLocationService(scope)

        resp_obj = assetlocation_serv.create_assetlocation(assetlocation_obj, emp_id,request)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_assetlocation_list(request)


def fetch_assetlocation_list(request):
    scope = request.scope
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    query = request.GET.get('query', None)
    assetlocation_serv = AssetLocationService(scope)

    resp_obj = assetlocation_serv.fetch_assetlocation_list(query, vys_page,request)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_assetlocation(request, assetlocation_id):
    scope = request.scope
    if request.method == 'GET':
        user_id = request.user.id
        assetlocation_serv = AssetLocationService(scope)

        resp_obj = assetlocation_serv.fetch_assetlocation(assetlocation_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_assetlocation(request, assetlocation_id)


def delete_assetlocation(request, assetlocation_id):
    scope = request.scope
    user_id = request.user.id
    emp_service = FaApiService(scope)
    emp_id=request.employee_id
    assetlocation_serv = AssetLocationService(scope)

    resp_obj = assetlocation_serv.delete_assetlocation(assetlocation_id,emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
