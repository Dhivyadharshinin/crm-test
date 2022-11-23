from django.http import HttpResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from faservice.data.request.assetlocationrequest import AssetLocationRequest
from faservice.data.request.clearingdetailsrequest import ClearingDetailsRequest
from faservice.data.request.clearingheaderrequest import ClearingHeaderRequest, ClearanceBucketRequest
from faservice.service.assetlocationservice import AssetLocationService
from faservice.service.clearingdetailsservice import ClearingDetailsService
from faservice.service.clearingheaderservice import ClearingHeaderService
from faservice.util.FaApiService import FaApiService
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror import NWisefinError as Error
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription,ErrorMessage
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
import json
from utilityservice.data.response.nwisefinpage import NWisefinPage
# clearingdetails_serv = ClearingDetailsService(scope)
# clearingheader_serv = ClearingHeaderService(scope)

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_clearingdetails(request):
    scope=request.scope
    if request.method == 'POST':
        clearingdetails_json = json.loads(request.body)
        clearingheader_serv = ClearingHeaderService(scope)
        logger.info('FAL_ASSET_CLEARING_DETAILS_DATA:{}'.format(clearingdetails_json))
        user_id = request.user.id
        emp_service = FaApiService(scope)
        emp_id=request.employee_id
        #print(clearingdetails_json,'clearingdetails_json')
        # total_invoice_amount=clearingdetails_json.get('totinvoiceamount')
        clearingheader_obj = ClearingHeaderRequest(clearingdetails_json)
        #balanceamount calculation here ***
        # balanceamount = get_totinvoiceamount_cal(total_invoice_amount)

        resp_obj = clearingheader_serv.create_clearingheader(clearingheader_obj, emp_id)
        clearingheader_id=resp_obj.id


        clearingdetails_json=clearingdetails_json['Details']
        #print(clearingdetails_json,'clearingdetails_json')
        clearinddtls_list = NWisefinList()
        for clearingdtls_json in clearingdetails_json:
            clearingdetails_serv = ClearingDetailsService
            clearingdetails_obj =  ClearingDetailsRequest(clearingdtls_json)
            resp_obj = clearingdetails_serv.create_clearingdetails(clearingdetails_obj, emp_id,clearingheader_id)
            clearinddtls_list.append(resp_obj)
        response = HttpResponse(clearinddtls_list.get(), content_type="application/json")
        return response

    # elif request.method == 'GET':
    #     return fetch_clearingdetails_list(request)


# def fetch_clearingdetails_list(request):
#     user_id = request.user.id
#     page = request.GET.get('page', 1)
#     page = int(page)
#     vys_page = NWisefinPage(page, 10)
#     doctype = request.GET.get('doctype',str())
#     invno = request.GET.get('invno',str())
#     invdate = request.GET.get('invdate',str())
#
#     if doctype is str():
#         error_obj = Error()
#         error_obj.set_code(ErrorMessage.INVALID_DOCTYPE)
#         error_obj.set_description(ErrorDescription.INVALID_DOCTYPE)
#         response = HttpResponse(error_obj.get(), content_type="application/json")
#         return response
#
#     resp_obj = clearingdetails_serv.fetch_clearingdetails_list(doctype,invno,invdate, vys_page)
#
#     response = HttpResponse(resp_obj.get(), content_type="application/json")
#     return response

@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_clearingdetails(request, clearingdetails_id):
    if request.method == 'GET':
        user_id = request.user.id
        clearingdetails_serv = ClearingDetailsService
        resp_obj = clearingdetails_serv.fetch_clearingdetails(clearingdetails_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_clearingdetails(request, clearingdetails_id)


def delete_clearingdetails(request, clearingdetails_id):
    scope = request.scope
    user_id = request.user.id
    emp_service = FaApiService(scope)

    emp_id=request.employee_id
    clearingdetails_serv = ClearingDetailsService
    resp_obj = clearingdetails_serv.delete_clearingdetails(clearingdetails_id,emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_clearingdetails_list(request,clearingheader_id):
    user_id = request.user.id
    clearingdetails_serv = ClearingDetailsService
    resp_obj = clearingdetails_serv.fetch_clearingdetails_list(clearingheader_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_clearingheaderdetails(request):
    user_id = request.user.id
    scope=request.scope
    clearingheader_id=request.GET.get('clearing_header_id')
    # print(clearingheader_id)
    clearingdetails_serv = ClearingDetailsService(scope)
    resp_obj = clearingdetails_serv.view_clearingdetails(clearingheader_id,user_id,request)
    if isinstance(resp_obj,Error):
        response=HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    response = HttpResponse(json.dumps(resp_obj,default=default_for_decial), content_type="application/json")
    return response

def default_for_decial(obj):
    from decimal import Decimal
    import datetime
    if isinstance(obj, Decimal):
        return float(str(obj))
    if isinstance(obj, datetime.datetime):
        return str(obj)
    raise TypeError("Object of type '%s' is not JSON serializable" % type(obj).__name__)