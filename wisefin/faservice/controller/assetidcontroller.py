import json
from django.http import HttpResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt

from faservice.util.FaApiService import FaApiService
from nwisefin.settings import logger
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from utilityservice.data.response.nwisefinpage import NWisefinPage


#from userservice.service.employeeservice import EmployeeService
from faservice.data.request.assetidrequest import AssetidRequest
from faservice.service.assetidservice import AssetidService

from faservice.util.fautil_valid import source_valdaition
from faservice.util.fautil import get_sourcetype_list
from utilityservice.data.response.nwisefinerror import NWisefinError as Error
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription,ErrorMessage
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_assetid(request):
    scope=request.scope
    if request.method == 'POST':
        assetid_json = json.loads(request.body)
        logger.info('FAL_ASSETID_DATA:{}'.format(assetid_json))
        assetid_obj = AssetidRequest(assetid_json)
        # source validation
        source_valid = source_valdaition(assetid_obj.source)
        if source_valid is False:
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_DATA)
            response = HttpResponse(error_obj.get(), content_type="application/json")
            return response

        user_id = request.user.id
        emp_service = FaApiService(scope)
        emp_id=request.employee_id
        assetid_serv = AssetidService(scope)

        resp_obj = assetid_serv.create_assetid( assetid_obj, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_assetid_list(request)


def fetch_assetid_list(request):
    scope=request.scope
    # user_id = request.user.id
    # emp_id=request.employee_id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    assetid_serv = AssetidService(scope)

    resp_obj = assetid_serv.fetch_assetid_list(vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_assetid(request, assetcat_id):
    if request.method == 'GET':
        scope = request.scope
        # user_id = request.user.id
        # emp_id=request.employee_id
        assetid_serv = AssetidService(scope)

        resp_obj = assetid_serv.fetch_assetid(assetcat_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_assetid(request, assetcat_id)


def delete_assetid(request, assetcat_id):
    user_id = request.user.id
    scope = request.scope
    emp_service = FaApiService(scope)
    emp_id=request.employee_id
    assetid_serv = AssetidService(scope)

    resp_obj = assetid_serv.delete_assetid(assetcat_id,emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


def get_source_type(request):
    obj =get_sourcetype_list()
    response = HttpResponse(obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET', 'DELETE'])
def assetid_update(request,assetid_id):
    scope = request.scope
    # user_id = request.user.id
    data = json.loads(request.body)
    logger.info('FAL_ASSET_ID_UPDATE_DATA:{}'.format(data))
    # emp_id = emp_service.get_employee_from_userid(user_id)
    assetid_serv = AssetidService(scope)

    resp_obj  = assetid_serv.update_assetid(assetid_id,data)
    response = HttpResponse('updated', content_type="application/json")
    return response

