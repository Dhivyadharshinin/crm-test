import json

from django.db import transaction
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from faservice.service.splitservice import SplitService
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
def create_split(request):
    if request.method == 'POST':
        scope = request.scope
        assetdetails_serv = AssetDetailsService(scope)
        split_serv = SplitService(scope)
        emp_service = FaApiService(scope)
        user_id = request.user.id
        emp_id=request.employee_id

        details_json = json.loads(request.body)
        logger.info("data split : " + str(details_json))

        assetdetailsid = details_json.get("assetdetailsid")
        assetdetails_value = details_json.get("assetdetails_value")
        reason = details_json.get("reason")
        date = details_json.get("date")
        split_detail = details_json.get("split_detail")
        logger.info('FAL_SPLIT_DATA:{}'.format(details_json))

        resp_asset = assetdetails_serv.assetdetails_split(assetdetailsid, emp_id,request)
        if resp_asset == "success":
            logger.info("after asset success call split")
            resp = split_serv.create_split(assetdetailsid, assetdetails_value, reason, date, split_detail,details_json, emp_id, request)
            assetsplitheader = resp.id
            split_detail.pop(0)
            resp1 = split_serv.create_splitdetail(split_detail, assetsplitheader, assetdetails_value, emp_id,request)
            response = HttpResponse(resp.get(), content_type="application/json")
        else:
            transaction.set_rollback(True)
            response = HttpResponse(resp_asset, content_type="application/json")
        logger.info("resp_split" + str(response))
        return response

    elif request.method == 'GET':
        return fetch_split_list(request)


def fetch_split_list(request):
    scope = request.scope
    split_serv = SplitService(scope)
    emp_service = FaApiService(scope)
    user_id = request.user.id
    emp_id=request.employee_id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = split_serv.fetch_split_list(vys_page, emp_id, request)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


# maker summary - search
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def split_maker_search(request):
    scope = request.scope
    split_serv = SplitService(scope)
    emp_service = FaApiService(scope)
    data_obj = json.loads(request.body)
    user_id = request.user.id
    emp_id=request.employee_id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = split_serv.split_maker_summarysearch(vys_page, emp_id, data_obj, request)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def split_get(request):
    scope = request.scope
    split_serv = SplitService(scope)
    emp_service = FaApiService(scope)
    user_id = request.user.id
    emp_id=request.employee_id
    query = request.GET.get('query')
    resp_obj = split_serv.split_get(query, emp_id, request)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


# checker - approve/reject
@transaction.atomic
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def split_checker(request):
    scope = request.scope
    if request.method == 'POST':
        split_serv = SplitService(scope)
        details_json = json.loads(request.body)
        action = details_json.get('action')
        user_id = request.user.id
        emp_service = FaApiService(scope)
        emp_id = request.employee_id
        if action == "APPROVE":
            resp_obj = split_serv.split_approve(details_json, emp_id,request)
        elif action == "REJECT":
            resp_obj = split_serv.split_reject(details_json, emp_id,request)
        else:
            resp_obj = Error()
            resp_obj.set_code(ErrorMessage.INVALID_DATA)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return split_checker_list(request)


def split_checker_list(request):
    scope = request.scope
    split_serv = SplitService(scope)
    emp_service = FaApiService(scope)
    user_id = request.user.id
    emp_id=request.employee_id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = split_serv.split_checker_list(vys_page, emp_id, request)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


# maker summary - search
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def split_checker_search(request):
    scope = request.scope
    split_serv = SplitService(scope)
    emp_service = FaApiService(scope)
    data_obj = json.loads(request.body)
    user_id = request.user.id
    emp_id=request.employee_id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = split_serv.split_checker_search(vys_page, emp_id, data_obj, request)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


#checker split summary
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def split_assetlist(request):
    scope = request.scope
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    split_serv = SplitService(scope)
    user_id = request.user.id
    emp_service = FaApiService(scope)
    emp_id = emp_service.get_empid_from_userid(user_id, request)
    resp_obj = split_serv.split_assetlist(vys_page, emp_id, request)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

#codegenerator for split
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def codegenerator_split(request):
    scope = request.scope
    # print(request.META['HTTP_USER_AGENT'])
    split_serv = SplitService(scope)
    emp_service = FaApiService(scope)
    user_id = request.user.id
    emp_id=request.employee_id
    query = request.GET.get('query')
    count = int(request.GET.get('count'))
    resp_obj = split_serv.codegenerator_split(query,count, emp_id, request)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response