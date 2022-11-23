import json

from django.db import transaction
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from faservice.models import AssetDetails
from faservice.service.mergeservice import MergeService
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror import NWisefinError as Error
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription,ErrorMessage
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission

from faservice.service.assetdetailsservice import AssetDetailsService
from faservice.util.FaApiService import FaApiService


@transaction.atomic
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_merge(request):
    if request.method == 'POST':
        scope = request.scope
        assetdetails_serv = AssetDetailsService(scope)
        merge_serv = MergeService(scope)
        emp_service = FaApiService(scope)
        user_id = request.user.id
        emp_id=request.employee_id
        details_json = json.loads(request.body)
        logger.info("data writeoff : " + str(details_json))
        data_arr = details_json.get("assetdetails_id")
        # new_asset_id = details_json.get("new_asset_id")
        reason = details_json.get("reason")
        date = details_json.get("date")
        value = details_json.get("value")
        source_id = details_json.get("source_id")
        # print(source_id)
        logger.info("data_arr: " + str(data_arr))
        logger.info("assetdetails")
        asset_value = 0
        for assetdetails_id in data_arr:
            assetdetails = AssetDetails.objects.get(id=assetdetails_id)
            asset_value += assetdetails.assetdetails_value
        from decimal import Decimal
        values = Decimal(round(value, 2))
        intValue = float(values)
        asset_value= round(asset_value, 2)
        asset_value = float(asset_value)
        # print(type(value))
        # print(type(asset_value))
        logger.info("given value: " + str(values))
        logger.info("asset_value: " + str(asset_value))
        if values == asset_value:
            logger.info("value same update merge")
            # print("value same update merge")
            logger.info('FAL_MERGE_DATA:{}'.format(details_json))

            resp_asset = assetdetails_serv.assetdetails_merge(data_arr, emp_id,request)
            logger.info("resp_asset" + str(resp_asset))
            logger.info("after asset success call split")
            if resp_asset == "success":
                resp = merge_serv.create_merge(source_id, value, reason, date, emp_id, request)
                assetsplitheader = resp.id
                logger.info("mergeheaderId" + str(assetsplitheader))

                resp1 = merge_serv.create_mergedetail(data_arr, assetsplitheader, value, emp_id,request)
                response = HttpResponse(resp.get(), content_type="application/json")
            else:
                transaction.set_rollback(True)
                response = HttpResponse(resp_asset, content_type="application/json")
            logger.info("resp_split" + str(response))
        else:
            error_obj = {}
            error_obj['error'] = "Error"
            error_obj['description'] = "Please Check the Value"
            responce = json.dumps(error_obj)
            response = HttpResponse(responce, content_type="application/json")
        return response

    elif request.method == 'GET':
        return merge_maker_list(request)

def merge_maker_list(request):
    scope = request.scope
    merge_serv = MergeService(scope)
    emp_service = FaApiService(scope)
    user_id = request.user.id
    emp_id=request.employee_id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = merge_serv.merge_maker_list(vys_page, emp_id, request)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def merge_maker_search(request):
    scope = request.scope
    merge_serv = MergeService(scope)
    emp_service = FaApiService(scope)
    data_obj = json.loads(request.body)
    user_id = request.user.id
    emp_id=request.employee_id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = merge_serv.merge_maker_search(vys_page, emp_id, data_obj, request)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def merge_checker_search(request):
    scope = request.scope
    merge_serv = MergeService(scope)
    emp_service = FaApiService(scope)
    data_obj = json.loads(request.body)
    user_id = request.user.id
    emp_id=request.employee_id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = merge_serv.merge_checker_search(vys_page, emp_id, data_obj, request)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

# view
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def merge_get(request):
    scope = request.scope
    merge_serv = MergeService(scope)
    emp_service = FaApiService(scope)
    user_id = request.user.id
    emp_id=request.employee_id
    query = request.GET.get('query')
    resp_obj = merge_serv.merge_get(query, emp_id, request)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


# checker - approve/reject
@transaction.atomic
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def merge_checker(request):
    scope = request.scope
    if request.method == 'POST':
        merge_serv = MergeService(scope)
        details_json = json.loads(request.body)
        action = details_json.get('action')
        user_id = request.user.id
        emp_service = FaApiService(scope)
        emp_id = emp_service.get_empid_from_userid(user_id, request)
        if action == "APPROVE":
            resp_obj = merge_serv.merge_approve(details_json, emp_id,request)
        elif action == "REJECT":
            resp_obj = merge_serv.merge_reject(details_json, emp_id,request)
        else:
            resp_obj = Error()
            resp_obj.set_code(ErrorMessage.INVALID_DATA)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return merge_checker_list(request)

def merge_checker_list(request):
    scope = request.scope
    merge_serv = MergeService(scope)
    emp_service = FaApiService(scope)
    user_id = request.user.id
    emp_id=request.employee_id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = merge_serv.merge_checker_list(vys_page, emp_id, request)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


# maker summary - search
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def merge_checker_search(request):
    scope = request.scope
    merge_serv = MergeService(scope)
    emp_service = FaApiService(scope)
    data_obj = json.loads(request.body)
    user_id = request.user.id
    emp_id=request.employee_id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = merge_serv.merge_checker_search(vys_page, emp_id, data_obj, request)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


