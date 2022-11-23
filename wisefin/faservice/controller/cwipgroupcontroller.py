from django.http import HttpResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from faservice.data.request.cwipgrouprequest import CwipGroupRequest
from faservice.service.cwipgroupservice import CwipGroupService
from faservice.util.FaApiService import FaApiService
from faservice.util.fautil import get_fadoctype_list
#from userservice.service.employeeservice import EmployeeService
from nwisefin.settings import logger
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
import json
from utilityservice.data.response.nwisefinpage import NWisefinPage

#emp_service = EmployeeService(scope)



@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_cwipgroup(request):
    if request.method == 'POST':
        scope=request.scope
        cwipgroup_json = json.loads(request.body)
        logger.info('FAL_ASSET_CWIP_GROUP_DATA:{}'.format(cwipgroup_json))
        cwipgroup_obj = CwipGroupRequest(cwipgroup_json)
        user_id = request.user.id
        fa_obj = FaApiService(scope)
        cwipgroup_serv = CwipGroupService(scope)
        emp_id = request.employee_id
        resp_obj = cwipgroup_serv.create_cwipgroup(cwipgroup_obj, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_cwipgroup_list(request)


def fetch_cwipgroup_list(request):
    user_id = request.user.id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    query = request.GET.get('query', str())
    scope = request.scope
    cwipgroup_serv = CwipGroupService(scope)
    resp_obj = cwipgroup_serv.fetch_cwipgroup_list(query, vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_doctype_list(request):
    resp_obj = get_fadoctype_list()
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


# @api_view(['GET', 'DELETE'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def fetch_assetlocation(request, assetlocation_id):
#     if request.method == 'GET':
#         user_id = request.user.id
#         resp_obj = assetlocation_serv.fetch_assetlocation(assetlocation_id)
#         response = HttpResponse(resp_obj.get(), content_type="application/json")
#         return response
#     elif request.method == 'DELETE':
#         return delete_assetlocation(request, assetlocation_id)
#
#
# def delete_assetlocation(request, assetlocation_id):
#     user_id = request.user.id
#     emp_id=request.employee_id
#     resp_obj = assetlocation_serv.delete_assetlocation(assetlocation_id,emp_id)
#     response = HttpResponse(resp_obj.get(), content_type="application/json")
#     return response
