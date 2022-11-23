from django.http import HttpResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt

from faservice.data.request.assetcatrequest import AssetCatRequest
from faservice.service.assetcatservice import AssetCatService
#from inwardservice.data.request.escalationtyperequest import EscalatonTypeRequest
#from inwardservice.service.escalationtypeservice import EscalationTypeService
#from userservice.service.employeeservice import EmployeeService
from nwisefin.settings import logger
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
import json
from utilityservice.data.response.nwisefinpage import NWisefinPage
from faservice.util.FaApiService import FaApiService

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_assetcat(request):
    if request.method == 'POST':
        scope=request.scope
        assetcat_serv = AssetCatService(scope)
        assetcat_json = json.loads(request.body)
        logger.info('FAL_ASSETCAT_DATA:{}'.format(assetcat_json))
        escaltiontype_obj = AssetCatRequest(assetcat_json)
        user_id = request.user.id
        emp_service = FaApiService(scope)
        emp_id = emp_service.get_empid_from_userid(user_id,request)
        logger.info('FAL_ASSETCAT_DATA:{}'.format(str(assetcat_json)))
        resp_obj = assetcat_serv.create_assetcat( escaltiontype_obj, emp_id,request)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_assetcat_list(request)
def fetch_assetcat_list(request):
    scope = request.scope
    assetcat_serv = AssetCatService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    subcatname = request.GET.get('subcatname', None)
    deptype = request.GET.get('deptype', None)
    # print('subcatname -->',subcatname,'deptype -->',deptype)
    # print('subcatname -->',type(subcatname),'deptype -->',type(deptype))
    resp_obj = assetcat_serv.fetch_assetcat_list(subcatname,deptype, vys_page,request)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_assetcat(request, assetcat_id):
    scope = request.scope

    assetcat_serv = AssetCatService(scope)
    if request.method == 'GET':
        resp_obj = assetcat_serv.fetch_assetcat(assetcat_id,request)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_assetcat(request, assetcat_id)
def delete_assetcat(request, assetcat_id,):
    scope = request.scope
    assetcat_serv = AssetCatService(scope)
    user_id = request.user.id
    emp_service = FaApiService(scope)
    emp_id=request.employee_id
    resp_obj = assetcat_serv.delete_assetcat(assetcat_id,emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
