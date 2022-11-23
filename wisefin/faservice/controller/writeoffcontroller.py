import json
from datetime import datetime
from time import strptime

from django.db import transaction
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from faservice.models import AssetDetails
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror import NWisefinError as Error
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription,ErrorMessage
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission

from faservice.service.assetdetailsservice import AssetDetailsService
from faservice.service.writeoffservice import WriteOffService
from faservice.util.FaApiService import FaApiService


@transaction.atomic
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_writeoff(request):
    if request.method == 'POST':
        scope = request.scope
        assetdetails_serv = AssetDetailsService(scope)
        writeoff_serv = WriteOffService(scope)
        emp_service = FaApiService(scope)
        user_id = request.user.id
        emp_id=request.employee_id
        details_json = json.loads(request.body)
        resp=validate_date(details_json,request)
        if isinstance(resp,Error):
            return HttpResponse(resp.get(),content_type='application/json')
        logger.info("data writeoff : " + str(details_json))
        data_arr = details_json.get("assetdetails_id")
        reason = details_json.get("reason")
        date = details_json.get("date")
        logger.info("data_arr: " + str(data_arr))
        for i in data_arr:
            logger.info("assetdetails")
            logger.info('FAL_WRITEOFF_DATA:{}'.format(details_json))

            resp_asset = assetdetails_serv.assetdetails_writeoff(i, emp_id,request)
            # print("resp_asset1", resp_asset)
            logger.info("resp_asset" + str(resp_asset))
            if resp_asset == "success":
                logger.info("writeoff")
                # print("writeoff")
                resp_writeoff = writeoff_serv.create_writeoff(i, reason, date, emp_id,request)
                logger.info("resp_writeoff" + str(resp_writeoff))
                response = HttpResponse(resp_writeoff.get(), content_type="application/json")
            else:
                transaction.set_rollback(True)
                response = HttpResponse(resp_asset, content_type="application/json")
        return response

    elif request.method == 'GET':
        return fetch_writeoff_list(request)
def validate_date(data,request):
    scope = request.scope
    asset_id=data['assetdetails_id']
    write_date=datetime.strptime(data['date'],'%Y-%m-%d').date()
    asset_data= AssetDetails.objects.filter(id__in=asset_id)
    for data in asset_data:
        if data.capdate>write_date:
            err=Error()
            err.set_code(ErrorMessage.INVALID_CAP_DATE)
            err.set_description(ErrorDescription.INVALID_CAP_DATE)
            return err
def fetch_writeoff_list(request):
    scope = request.scope
    assetdetails_serv = AssetDetailsService(scope)
    writeoff_serv = WriteOffService(scope)
    emp_service = FaApiService(scope)
    user_id = request.user.id
    emp_id=request.employee_id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = writeoff_serv.fetch_writeoff_list(vys_page, emp_id, request)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

#maker summary - add
@api_view([ 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def search_writeoff_add(request):
    scope = request.scope
    writeoff_serv = WriteOffService(scope)
    data_obj = json.loads(request.body)
    user_id = request.user.id
    emp_service = FaApiService(scope)
    emp_id = emp_service.get_empid_from_userid(user_id, request)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = writeoff_serv.search_writeoff_add(vys_page, emp_id, data_obj, request)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

#maker summary
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def writeoff_maker(request):
    scope = request.scope
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    writeoff_serv = WriteOffService(scope)
    user_id = request.user.id
    emp_service = FaApiService(scope)
    emp_id = emp_service.get_empid_from_userid(user_id, request)
    resp_obj = writeoff_serv.writeoff_maker_summary(vys_page, emp_id, request)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

#maker summary - search
@api_view([ 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def writeoff_maker_summarysearch(request):
    scope = request.scope
    writeoff_serv = WriteOffService(scope)
    data_obj = json.loads(request.body)
    user_id = request.user.id
    emp_service = FaApiService(scope)
    emp_id = emp_service.get_empid_from_userid(user_id, request)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = writeoff_serv.writeoff_maker_summarysearch(vys_page, emp_id, data_obj, request)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_assetdetails(request, assetdetails_id):
    scope = request.scope
    writeoff_serv = WriteOffService(scope)
    user_id = request.user.id
    emp_service = FaApiService(scope)
    emp_id = emp_service.get_empid_from_userid(user_id, request)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = writeoff_serv.fetch_assetdetails(assetdetails_id, emp_id, request)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response



#checker - approve/reject
@transaction.atomic
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def writeoff_checker(request):
    scope = request.scope
    if request.method == 'POST':
        writeoff_serv = WriteOffService(scope)
        details_json = json.loads(request.body)
        action = details_json.get('action')
        # reason = details_json.get("reason")
        user_id = request.user.id
        emp_service = FaApiService(scope)
        emp_id = emp_service.get_empid_from_userid(user_id, request)

        if action == "APPROVE":
            resp_obj = writeoff_serv.writeoff_approve(details_json, emp_id,request)
            resp_obj1 = writeoff_serv.create_asset_writeoff(details_json, emp_id, request)

        elif action == "REJECT":
            resp_obj = writeoff_serv.writeoff_reject(details_json, emp_id,request)
        else:
            resp_obj = Error()
            resp_obj.set_code(ErrorMessage.INVALID_DATA)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return writeoff_checker_list(request)

def cap_validation(data):
    pass
def writeoff_checker_list(request):
    scope = request.scope
    writeoff_serv = WriteOffService(scope)
    emp_service = FaApiService(scope)
    user_id = request.user.id
    emp_id=request.employee_id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = writeoff_serv.writeoff_checker_list(vys_page, emp_id, request)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


#maker summary - search
@api_view([ 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def writeoff_checker_search(request):
    scope = request.scope
    writeoff_serv = WriteOffService(scope)
    data_obj = json.loads(request.body)
    user_id = request.user.id
    emp_service = FaApiService(scope)
    emp_id = emp_service.get_empid_from_userid(user_id, request)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = writeoff_serv.writeoff_checker_search(vys_page, emp_id, data_obj, request)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response



# summary - add
@api_view([ 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def writeoff_add(request):
    scope = request.scope
    writeoff_serv = WriteOffService(scope)
    data_obj = json.loads(request.body)
    user_id = request.user.id
    emp_service = FaApiService(scope)
    emp_id = emp_service.get_empid_from_userid(user_id, request)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = writeoff_serv.writeoff_add(vys_page, emp_id, data_obj, request)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

