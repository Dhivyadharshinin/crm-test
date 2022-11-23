import json
from django.db import transaction
from django.http import HttpResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from faservice.service.assetvaluechangeservice import AssetValueChange
from faservice.util.FaApiService import FaApiService
from nwisefin.settings import logger
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from utilityservice.data.response.nwisefinpage import NWisefinPage
from userservice.service.employeeservice import EmployeeService
from faservice.data.request.assetidrequest import AssetidRequest
from faservice.service.assetidservice import AssetidService

from faservice.util.fautil_valid import source_valdaition
from faservice.util.fautil import get_sourcetype_list
from utilityservice.data.response.nwisefinerror import NWisefinError as Error
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription,ErrorMessage





@api_view([ 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_assetvaluechange_list(request):
    scope=request.scope
    if request.method == 'POST':
        assetvalue_filter_json = json.loads(request.body)
        user_id = request.user.id
        emp_service = FaApiService(scope)
        assetvalue_serv = AssetValueChange(scope)
        emp_id=request.employee_id
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        resp_obj = assetvalue_serv.fetch_assetvaluechange_list(vys_page,assetvalue_filter_json,emp_id,request)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_valuechange_assetdetails(request):
    scope=request.scope

    if request.method == 'POST':
        asset_json = json.loads(request.body)
        logger.info('FAL_ASSETVAL_DATA:{}'.format(asset_json))
        asset_serv = AssetValueChange(scope)

        assetvalue_currentdate_val = asset_serv.valuechange_currentdate_validation(asset_json)
        # print('assetvalue_currentdate_val',assetvalue_currentdate_val)
        if assetvalue_currentdate_val is True:
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_CAPDATE)
            response = HttpResponse(error_obj.get(), content_type="application/json")
            return response


        assetvalue_val=asset_serv.valuechange_validation(asset_json)
        if assetvalue_val is True:
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_VALUE)
            response = HttpResponse(error_obj.get(), content_type="application/json")
            return response

        assetvalue_changedate_val=asset_serv.valuechange_capdate_validation(asset_json)
        if assetvalue_changedate_val is True:
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_VALUECHANGEDATE)
            response = HttpResponse(error_obj.get(), content_type="application/json")
            return response

        user_id = request.user.id
        emp_service = EmployeeService(scope)
        emp_id=request.employee_id

        resp_obj = asset_serv.create_valuechange_assetdetails(asset_json, emp_id,request)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@api_view([ 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def valuechange_checkersummary(request):
    scope=request.scope

    if request.method == 'POST':
        assetvalue_filter_json = json.loads(request.body)
        user_id = request.user.id
        emp_service = EmployeeService(scope)
        assetvalue_serv = AssetValueChange(scope)
        emp_id=request.employee_id
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        resp_obj = assetvalue_serv.valuechange_checkersummary(vys_page,assetvalue_filter_json,emp_id,request)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response



@api_view([ 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def valuechange_approve(request):
    scope=request.scope

    if request.method == 'POST':
        assetvalue_json = json.loads(request.body)
        logger.info('FAL_ASSETVAL_APPROVE_DATA:{}'.format(assetvalue_json))
        user_id = request.user.id
        emp_service = EmployeeService(scope)
        assetvalue_serv = AssetValueChange(scope)
        emp_id=request.employee_id
        valuechange_approver_val=assetvalue_serv.valuechange_approver_validation(assetvalue_json,emp_id)
        if valuechange_approver_val is True:
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST)
            error_obj.set_description(ErrorDescription.INVALID_VALUECHANGEAPPROVER)
            response = HttpResponse(error_obj.get(), content_type="application/json")
            return response


        resp_obj = assetvalue_serv.valuechange_approve(assetvalue_json,emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
@api_view([ 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def valuechange_reject(request):
    scope=request.scope

    if request.method == 'POST':
        assetvalue_json = json.loads(request.body)
        logger.info('FAL_ASSETVALUE_REJECT_DATA:{}'.format(assetvalue_json))
        user_id = request.user.id
        emp_service = EmployeeService(scope)
        assetvalue_serv = AssetValueChange(scope)
        emp_id=request.employee_id
        valuechange_approver_val=assetvalue_serv.valuechange_approver_validation(assetvalue_json,emp_id)
        if valuechange_approver_val is True:
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST)
            error_obj.set_description(ErrorDescription.INVALID_VALUECHANGEAPPROVER)
            response = HttpResponse(error_obj.get(), content_type="application/json")
            return response


        resp_obj = assetvalue_serv.valuechange_reject(assetvalue_json,emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response



@api_view([ 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def valuechange_summary(request):
    scope=request.scope

    if request.method == 'POST':
        assetvalue_filter_json = json.loads(request.body)
        user_id = request.user.id
        emp_service = EmployeeService(scope)
        assetvalue_serv = AssetValueChange(scope)
        emp_id=request.employee_id
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        resp_obj = assetvalue_serv.valuechange_summary(vys_page,assetvalue_filter_json,emp_id,request)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

#@transaction.atomic()
@api_view([ 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def rollback_test(request):
    scope=request.scope
    if request.method == 'POST':
        assetvalue_serv = AssetValueChange(scope)
        resp_obj = assetvalue_serv.rollback_testing()
        response = HttpResponse('resp_obj.get()', content_type="application/json")
        return response