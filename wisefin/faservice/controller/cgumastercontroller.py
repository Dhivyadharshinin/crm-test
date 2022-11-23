import json
from django.http import HttpResponse
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt

from faservice.data.request.cgumasterrequest import CGUMasterRequest
from faservice.service.cgumasterservice import CGUMASTERService


from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from faservice.util.FaApiService import FaApiService
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
# master cgu name
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_cgumaster(request):
    scope=request.scope
    cgumst_service = CGUMASTERService(scope)
    cgumst_data = json.loads(request.body)
    cgumst_objs = CGUMasterRequest(cgumst_data)
    emp_service = FaApiService(scope)
    logger.info('FAL_ASSETCGU_MAKE_DATA:{}'.format(cgumst_data))
    user_id = request.user.id
    emp_id=request.employee_id
    resp_obj = cgumst_service.create_cgumst(cgumst_objs, emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


# drop down -- cgu name
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def search_cgu_name(request):
    scope = request.scope
    cgumst_service = CGUMASTERService(scope)
    query = request.GET.get('query')
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = cgumst_service.search_cgu_name(vys_page, query)
    return HttpResponse(resp_obj.get(), content_type='application/json')