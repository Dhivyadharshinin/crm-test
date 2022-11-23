import json
from django.db import transaction
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from faservice.service.assetdetailsservice import AssetDetailsService
from faservice.service.impairservice import ImpairService
from userservice.service.employeeservice import EmployeeService

from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror import NWisefinError as Error
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription,ErrorMessage
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from faservice.util.FaApiService import FaApiService

#maker summary - impair
@api_view([ 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def search_impairmapping(request):
    scope=request.scope
    impair_serv = ImpairService(scope)
    data_obj = json.loads(request.body)
    user_id = request.user.id
    emp_service = FaApiService(scope)
    emp_id = emp_service.get_empid_from_userid(user_id, request)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = impair_serv.search_impairmapping(vys_page, emp_id, data_obj, request)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@transaction.atomic
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def cgu_mapping(request):
    scope = request.scope
    impair_serv = ImpairService(scope)
    user_id = request.user.id
    emp_service = FaApiService(scope)
    emp_id = emp_service.get_empid_from_userid(user_id, request)
    details_json = json.loads(request.body)
    logger.info('FAL_ASSET_CGU_MAPPING_DATA:{}'.format(details_json))
    logger.info("data cgu_mapping : " + str(details_json))
    resp = impair_serv.cgu_mapping(details_json, emp_id)
    logger.info("call cgu_mapping resp" + str(resp))
    response = HttpResponse(resp.get(), content_type="application/json")
    return response


#maker summary - add
@api_view([ 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def search_impair_add(request):
    scope = request.scope
    impair_serv = ImpairService(scope)
    data_obj = json.loads(request.body)
    user_id = request.user.id
    emp_service = FaApiService(scope)
    emp_id = emp_service.get_empid_from_userid(user_id, request)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = impair_serv.search_impair_add(vys_page, emp_id, data_obj, request)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@transaction.atomic
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def impair_maker(request):
    if request.method == 'POST':
        scope = request.scope
        assetdetails_serv = AssetDetailsService(scope)
        impair_serv = ImpairService(scope)
        user_id = request.user.id
        emp_service = FaApiService(scope)
        emp_id = emp_service.get_empid_from_userid(user_id, request)
        details_json = json.loads(request.body)
        logger.info('FAL_ASSET_IMPAIR_MAKE_DATA:{}'.format(details_json))
        logger.info("data impair add : " + str(details_json))
        data_arr = details_json.get("barcode")
        reversed_value = details_json.get("reversed_value")
        oldtotal_value = details_json.get("oldtotal_value")
        cgu_id = details_json.get("cgu_id")
        reason = details_json.get("reason")
        resp_asset = assetdetails_serv.assetdetails_impair(data_arr, reversed_value, oldtotal_value, emp_id)
        logger.info("resp_asset" + str(resp_asset))
        logger.info("after asset success call split")
        resp = impair_serv.create_impair(data_arr, reversed_value, reason, cgu_id, emp_id)
        impairh_id = resp.id
        # print(impairh_id)
        resp1 = impair_serv.create_impairdt(data_arr, impairh_id, reversed_value, emp_id)
        logger.info("impair resp" + str(resp1))
        # else:
        #     logger.info("impair resp: rollback")
        #     transaction.set_rollback(True)
        response = HttpResponse(resp.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return impair_maker_list(request)

def impair_maker_list(request):
    scope = request.scope
    impair_serv = ImpairService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = impair_serv.impairmaker_summary(vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@api_view([ 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def impair_maker_search(request):
    scope = request.scope
    impair_serv = ImpairService(scope)
    data_obj = json.loads(request.body)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = impair_serv.impairmaker_summary_search(vys_page, data_obj)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


# checker - approve/reject
@transaction.atomic
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def impair_checker(request):
    if request.method == 'POST':
        scope = request.scope
        impair_serv = ImpairService(scope)
        details_json = json.loads(request.body)
        logger.info('FAL_ASSET_IMPAIR_CHECKER_DATA:{}'.format(details_json))
        action = details_json.get('action')
        user_id = request.user.id
        emp_service = FaApiService(scope)
        emp_id = emp_service.get_empid_from_userid(user_id, request)
        if action == "APPROVE":
            resp_obj = impair_serv.impair_approve(details_json, emp_id)
        elif action == "REJECT":
            resp_obj = impair_serv.impair_reject(details_json, emp_id)
        else:
            resp_obj = Error()
            resp_obj.set_code(ErrorMessage.INVALID_DATA)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return impair_checker_list(request)

def impair_checker_list(request):
    scope = request.scope
    impair_serv = ImpairService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = impair_serv.impairchecker_summary(vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@api_view([ 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def impair_checker_search(request):
    scope = request.scope
    impair_serv = ImpairService(scope)
    data_obj = json.loads(request.body)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = impair_serv.impairchecker_summary_search(vys_page, data_obj)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
