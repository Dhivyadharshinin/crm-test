import json
from django.db import transaction
from django.http import HttpResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from faservice.service.categorychangeservice import AssetCategoryChange
from faservice.util.FaApiService import FaApiService
from nwisefin.settings import logger
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from utilityservice.data.response.nwisefinpage import NWisefinPage
from faservice.data.request.assetidrequest import AssetidRequest
from faservice.service.assetidservice import AssetidService
from faservice.util.fautil_valid import source_valdaition
from faservice.util.fautil import get_sourcetype_list
from utilityservice.data.response.nwisefinerror import NWisefinError as Error
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription,ErrorMessage



@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_categorychange(request):
    scope=request.scope
    if request.method == 'POST':
        asset_json = json.loads(request.body)
        asset_serv = AssetCategoryChange(scope)
        logger.info('FAL_ASSET_CAT_CHANGE_DATA:{}'.format(asset_json))
        user_id = request.user.id
        emp_service = FaApiService(scope)
        emp_id=request.employee_id
        resp_obj = asset_serv.make_categorychange(asset_json, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view([ 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_categorychange(request):
    scope=request.scope
    if request.method == 'POST':
        assetvalue_filter_json = json.loads(request.body)
        user_id = request.user.id
        emp_service = FaApiService(scope)
        assettransfer_serv = AssetCategoryChange(scope)
        emp_id=request.employee_id
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        resp_obj = assettransfer_serv.get_categorychange_list(vys_page,assetvalue_filter_json,emp_id,request)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@api_view([ 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_categorychange(request):
    if request.method == 'POST':
        scope = request.scope
        assetvalue_filter_json = json.loads(request.body)
        user_id = request.user.id
        emp_service = FaApiService(scope)
        assettransfer_serv = AssetCategoryChange(scope)
        emp_id=request.employee_id
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        resp_obj = assettransfer_serv.fetch_categorychange_list(vys_page,assetvalue_filter_json,emp_id,request)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@api_view([ 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_catchangechecker(request):
    scope=request.scope
    if request.method == 'POST':
        assetvalue_filter_json = json.loads(request.body)
        user_id = request.user.id
        emp_service = FaApiService(scope)
        assettransfer_serv = AssetCategoryChange(scope)
        emp_id=request.employee_id
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        resp_obj = assettransfer_serv.fetch_catchangechecker_list(vys_page,assetvalue_filter_json,emp_id,request)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@api_view([ 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def catchange_approve(request):
    scope=request.scope
    if request.method == 'POST':
        assetcat_json = json.loads(request.body)
        logger.info('FAL_ASSETCAT_APPROVE_DATA:{}'.format(assetcat_json))
        user_id = request.user.id
        emp_service = FaApiService(scope)
        assettransfer_serv = AssetCategoryChange(scope)
        emp_id=request.employee_id

        catchange_approver_val = assettransfer_serv.catchange_approver_validation(assetcat_json, emp_id)
        if catchange_approver_val is True:
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST)
            error_obj.set_description(ErrorDescription.INVALID_VALUECHANGEAPPROVER)
            response = HttpResponse(error_obj.get(), content_type="application/json")
            return response


        resp_obj = assettransfer_serv.catchangechecker_approve(assetcat_json,emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
