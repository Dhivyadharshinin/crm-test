from django.http import HttpResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt

from faservice.data.request.depreciationsettingrequest import DepreciationSettingRequest
from faservice.service.depreciationsettingservice import DepreciationSettingService
#from inwardservice.data.request.escalationtyperequest import EscalatonTypeRequest
#from inwardservice.service.escalationtypeservice import EscalationTypeService
#from userservice.service.employeeservice import EmployeeService
from userservice.service.employeeservice import EmployeeService
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
def create_depreciationsetting(request):
    if request.method == 'POST':
        scope = request.scope
        depsetting_serv = DepreciationSettingService(scope)
        depsetting_json = json.loads(request.body)
        logger.info('FAL_ASSET_DEPRICIATIONSETTINGS_DATA:{}'.format(depsetting_json))
        depsetting_obj = DepreciationSettingRequest(depsetting_json)
        user_id = request.user.id
        emp_service = FaApiService(scope)
        emp_id = request.employee_id
        resp_obj = depsetting_serv.create_depsetting( depsetting_obj, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_depsetting_list(request)


def fetch_depsetting_list(request):
    user_id = request.user.id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    query = request.GET.get('query', None)
    scope = request.scope
    depsetting_serv = DepreciationSettingService(scope)
    resp_obj = depsetting_serv.fetch_depsetting_list(query, vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_depsetting(request, depsetting_id):
    if request.method == 'GET':
        user_id = request.user.id
        scope = request.scope
        depsetting_serv = DepreciationSettingService(scope)
        resp_obj = depsetting_serv.fetch_depsetting(depsetting_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_depsetting(request, depsetting_id)


def delete_depsetting(request, depsetting_id):
    user_id = request.user.id
    scope = request.scope
    emp_service = FaApiService(scope)
    emp_id = request.employee_id
    depsetting_serv = DepreciationSettingService(scope)
    resp_obj = depsetting_serv.delete_depsetting(depsetting_id,emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
