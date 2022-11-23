import json
from django.db import transaction
from django.http import HttpResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from faservice.service.assettransferservice import AssetTransfer
from nwisefin.settings import logger
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from utilityservice.data.response.nwisefinpage import NWisefinPage
from userservice.service.employeeservice import EmployeeService
from faservice.data.request.assetidrequest import AssetidRequest
from faservice.service.assetidservice import AssetidService
from faservice.util.fautil_valid import source_valdaition
from faservice.util.fautil import get_sourcetype_list, dictdefault
from utilityservice.data.response.nwisefinerror import NWisefinError as Error
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription,ErrorMessage


@csrf_exempt
@api_view([ 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_assettransfer(request):
    if request.method == 'POST':
        scope = request.scope
        assetvalue_filter_json = json.loads(request.body)
        user_id = request.user.id
        emp_service = EmployeeService(scope)
        assettransfer_serv = AssetTransfer(scope)
        emp_id=request.employee_id
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        resp_obj = assettransfer_serv.fetch_assettransfer_list(vys_page,assetvalue_filter_json,emp_id,request)
        response = HttpResponse(json.dumps(resp_obj.__dict__,default=dictdefault), content_type="application/json")
        return response

@csrf_exempt
@api_view([ 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_assettransfer(request):
    scope = request.scope
    if request.method == 'POST':
        assetvalue_filter_json = json.loads(request.body)
        user_id = request.user.id
        emp_service = EmployeeService(scope)
        assettransfer_serv = AssetTransfer(scope)
        emp_id=request.employee_id
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        resp_obj = assettransfer_serv.get_assettransfer_list(vys_page,assetvalue_filter_json,emp_id,request)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view([ 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_assettransfer_checker(request):
    scope = request.scope
    if request.method == 'POST':
        assetvalue_filter_json = json.loads(request.body)
        user_id = request.user.id
        emp_service = EmployeeService(scope)
        assettransfer_serv = AssetTransfer(scope)
        emp_id=request.employee_id
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        resp_obj = assettransfer_serv.get_assettransfer_checker_list(vys_page,assetvalue_filter_json,emp_id,request)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_assettransfer(request):
    scope = request.scope
    if request.method == 'POST':
        asset_json = json.loads(request.body)
        logger.info('FAL_ASSETTFR_DATA:{}'.format(asset_json))
        asset_serv = AssetTransfer(scope)

        transfer_currentdate_val = asset_serv.transfer_currentdate_validation(asset_json)
        if transfer_currentdate_val is True:
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_CAPDATE)
            response = HttpResponse(error_obj.get(), content_type="application/json")
            return response

        assettransfer_capdate_val = asset_serv.assettransfer_capdate_validation(asset_json)
        if assettransfer_capdate_val is True:
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_TANSFER_DATE)
            response = HttpResponse(error_obj.get(), content_type="application/json")
            return response

        assettransfer_date_val = asset_serv.assettransfer_date_validation(asset_json)
        if assettransfer_date_val is True:
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_TANSFERDATE)
            response = HttpResponse(error_obj.get(), content_type="application/json")
            return response


        user_id = request.user.id
        emp_service = EmployeeService(scope)
        emp_id=request.employee_id

        resp_obj = asset_serv.make_assettransfer(asset_json, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def assettransfer_approve(request):
    scope = request.scope
    if request.method == 'POST':
        asset_json = json.loads(request.body)
        logger.info('FAL_ASSETTFR_APPROVE_DATA:{}'.format(asset_json))
        asset_serv = AssetTransfer(scope)
        user_id = request.user.id
        emp_service = EmployeeService(scope)
        emp_id=request.employee_id
        transfer_approver_val = asset_serv.transfer_approver_validation(asset_json, emp_id)
        if transfer_approver_val is True:
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST)
            error_obj.set_description(ErrorDescription.INVALID_VALUECHANGEAPPROVER)
            response = HttpResponse(error_obj.get(), content_type="application/json")
            return response


        resp_obj = asset_serv.transfer_approve(asset_json, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response



