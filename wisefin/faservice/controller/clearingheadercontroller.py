import logging
import traceback

from django.http import HttpResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt

from faservice.controller.assetdetailscontroller import dictdefault
from faservice.data.request.assetlocationrequest import AssetLocationRequest
from faservice.data.request.clearingheaderrequest import ClearingHeaderRequest, ClearanceBucketRequest,BucketRequest
from faservice.data.request.clearingdetailsrequest import ClearingDetailsRequest
from faservice.models import ClearingHeader
from faservice.service.assetlocationservice import AssetLocationService
from faservice.service.clearingheaderservice import ClearingHeaderService
from  faservice.service.clearingdetailsservice import ClearingDetailsService
from faservice.util.FaApiService import FaApiService
from faservice.util.fautil import FA_ROLLBACK_EXCEPTION
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror import NWisefinError as Error
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
import json
from utilityservice.data.response.nwisefinpage import NWisefinPage
# emp_service = FaApiService(scope)
from django.db import transaction

from utilityservice.service.threadlocal import NWisefinThread

class Dbget(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.FA_SERVICE)
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_clearingheader(request):
    if request.method == 'POST':
        try:
            scope = request.scope
            clearingheader_serv = ClearingHeaderService(scope)
            schema_get = Dbget(scope)
            schema = schema_get._current_app_schema()
            with transaction.atomic(using=schema):
                clearingheader_json = json.loads(request.body)
                logger.info('FAL_ASSET_CLEARING_HEADER_DATA:{}'.format(clearingheader_json))
                clearingheader_obj = ClearingHeaderRequest(clearingheader_json)
                doc_type=json.loads(clearingheader_json.get('details').replace("'",'"'))[0]['Doc_Type']
                emp_service = FaApiService(scope)
                emp_id = request.employee_id
                try:

                    resp_obj = clearingheader_serv.create_clearingheader(clearingheader_obj, doc_type,emp_id,request)
                    if isinstance(resp_obj,Error):
                        response=HttpResponse(resp_obj.get(), content_type="application/json")
                        raise FA_ROLLBACK_EXCEPTION(response)
                except:
                    err=Error()
                    err.set_code(ErrorMessage.INVALID_CLEARINGHEADER_DATA)
                    err.set_description(ErrorDescription.INVALID_CLEARINGHEADER_DATA)
                    response=HttpResponse(err.get(),content_type="application/json")
                    raise FA_ROLLBACK_EXCEPTION(response)
                # clearing details
                logging.error("FA_Clearing_Header : Created Successfully")
                logging.error("FA_Clearing_Data : "+str(clearingheader_json))
                clearingdetail_obj = json.loads(clearingheader_json.get('details').replace("'",'"'))
                clearingheader_id = resp_obj.id
                clearingdetail_obj_arr=[]
                for obj in clearingdetail_obj:
                    clearingdetails =  ClearingDetailsRequest(obj)
                    clearingdetail_obj_arr.append(clearingdetails)
                clearingdetail_serv = ClearingDetailsService(scope)
                cleardetails =clearingdetail_serv.create_clearingdetails(clearingdetail_obj_arr,emp_id,clearingheader_id,request)
                logging.error("FA_Clearing_details : Created_SuccessFully")
                if isinstance(cleardetails,Error):
                    response = HttpResponse(cleardetails.get(), content_type="application/json")
                    raise FA_ROLLBACK_EXCEPTION(response)

                else:
                    success_obj = NWisefinSuccess()
                    success_obj.set_status(SuccessStatus.SUCCESS)
                    success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
                    transaction.commit()
                    response = HttpResponse(success_obj.get(), content_type="application/json")
                    return response
        except FA_ROLLBACK_EXCEPTION as fa_except:
            return fa_except.data

    elif request.method == 'GET':
        return fetch_clearingheader_list(request)

def fetch_clearingheader_list(request):
    user_id = request.user.id
    # emp_id=request.employee_id
    page = request.GET.get('page', 1)
    is_grp=request.GET.get('Is_Grp')
    try:
        doc_type=request.GET.get('Doc_type')
    except:
        doc_type=None
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    # clearing header
    scope=request.scope
    clearingheader_serv = ClearingHeaderService(scope)

    resp_obj = clearingheader_serv.fetch_clearingheader(vys_page,is_grp,doc_type,request)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
@csrf_exempt
@api_view(['GET'])
def buc_summary(request):
    page = request.GET.get('page')
    scope=request.scope
    vys_page = NWisefinPage(int(page), 10)
    clearingheader_serv = ClearingHeaderService(scope)

    res=clearingheader_serv.bucketsummary(vys_page,request)
    responce=HttpResponse(res.get(),content_type="application/json")
    return responce
@csrf_exempt
@api_view(['GET'])
def buc_summary_search(request):
    page = request.GET.get('page')
    scope=request.scope
    data=request.GET.get('data')
    vys_page = NWisefinPage(int(page), 10)
    clearingheader_serv = ClearingHeaderService(scope)
    res=clearingheader_serv.bucketnamesearch(vys_page,data)
    responce=HttpResponse(res.get(),content_type="application/json")
    return responce
@csrf_exempt
@api_view(['GET','POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def clearingheader_lock_status(request):
    if request.method=='POST':
        scope=request.scope
        clearingheader_serv = ClearingHeaderService(scope)

        json_data=json.loads(request.body)
        res=clearingheader_serv.clearingheader_capitalize_unlock(json_data)
    else:
        scope=request.scope
        clearingheader_serv = ClearingHeaderService(scope)

        crnum = json.loads(request.body)['crnum']
        res=clearingheader_serv.get_clearing_lock_status(crnum)
    responce = HttpResponse(res.get(), content_type="application/json")
    return responce

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def clearance_movetobucket(request):
    if request.method == 'POST':
        # print(request.body.decode('utf-8'))
        clearancebucket_json = json.loads(request.body.decode('utf-8'))
        logger.info('FAL_ASSET_BUCKET_MOVE_DATA:{}'.format(clearancebucket_json))
        user_id = request.user.id
        scope = request.scope
        emp_service = FaApiService(scope)
        clearingheader_serv = ClearingHeaderService(scope)

        emp_id = request.employee_id
        resp_obj = clearingheader_serv.clearance_bucket(clearancebucket_json,emp_id)
        response = HttpResponse(resp_obj ,content_type="application/json")
        return response
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_bucket(request):
    if request.method == 'POST':
        clearancebucket_json = json.loads(request.body)
        logger.info('FAL_ASSET_BUCKET_MAKE_DATA:{}'.format(clearancebucket_json))
        buck_res=BucketRequest(clearancebucket_json)
        user_id = request.user.id
        scope=request.scope
        emp_service = FaApiService(scope)
        clearingheader_serv = ClearingHeaderService(scope)

        emp_id = request.employee_id
        resp_obj=clearingheader_serv.createnewbucket(buck_res,emp_id)
        response = HttpResponse(json.dumps(resp_obj,default=dictdefault), content_type="application/json")
    else:
        query=request.GET.get('query',None)
        scope=request.scope
        clearingheader_serv = ClearingHeaderService(scope)

        resp_obj = clearingheader_serv.fetch_bucket(query)
        response = HttpResponse(resp_obj, content_type="application/json")
    return response





# def fetch_assetlocation_list(request):
#     user_id = request.user.id
#     page = request.GET.get('page', 1)
#     page = int(page)
#     vys_page = NWisefinPage(page, 10)
#     query = request.GET.get('query', None)
#     resp_obj = assetlocation_serv.fetch_assetlocation_list(query, vys_page)
#     response = HttpResponse(resp_obj.get(), content_type="application/json")
#     return response
#
#
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
