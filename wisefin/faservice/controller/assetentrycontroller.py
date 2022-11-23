import requests
from django.http import HttpResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt

from faservice.data.request.assetcatrequest import AssetCatRequest
from faservice.data.request.assetdetailsrequest import CheckerSummaryRequest, CheckerSumRequest
from faservice.data.request.assetentryrequest import AssetEntryRequest
from faservice.service.assetcatservice import AssetCatService
#from inwardservice.data.request.escalationtyperequest import EscalatonTypeRequest
#from inwardservice.service.escalationtypeservice import EscalationTypeService
#from userservice.service.employeeservice import EmployeeService
from faservice.service.assetdetailsservice import AssetDetailsService
from faservice.service.assetentryservice import AssetentryService
from faservice.util.FaApiService import FaApiService
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror import NWisefinError as Error
from utilityservice.data.response.nwisefinsuccess import SuccessMessage,NWisefinSuccess as Success,SuccessStatus
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
import json
from utilityservice.data.response.nwisefinpage import NWisefinPage
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_assetentry(request,assetdetails_id):
    scope = request.scope
    if request.method == 'POST':
        assetcat_json = json.loads(request.body)
        logger.info('FAL_ASSETENTRY_DATA:{}'.format(assetcat_json))

        escaltiontype_obj = AssetEntryRequest(assetcat_json)
        assetdetails_id = int(assetdetails_id)
        user_id = request.user.id
        emp_service = FaApiService(scope)
        emp_id = request.employee_id
        assetcat_serv = AssetentryService(scope)

        resp_obj = assetcat_serv.create_assetentry(emp_id,assetdetails_id,request)
        resp_list=['debit','credit']
        resp_obj= {key:json.loads(value.get()) for key,value in zip(resp_list,resp_obj)}
        response = HttpResponse(json.dumps(resp_obj), content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_fundservice(request,assetdetails_id):
    if request.method == 'GET':
        assetdetails_id = int(assetdetails_id)
        scope = request.scope
        assetcat_serv = AssetentryService(scope)

        resp_obj = assetcat_serv.create_fundservice(assetdetails_id,request)
        if isinstance(resp_obj,Error):
            return HttpResponse(resp_obj.get(),content_type="application/json")
        response = HttpResponse(json.dumps(resp_obj), content_type="application/json")
        return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])

def repost(request):
    if request.method == 'POST':
        scope = request.scope
        assetcat_json = json.loads(request.body)
        logger.info('FAL_ASSETENTRY_DATA:{}'.format(assetcat_json))
        escaltiontype_obj = CheckerSumRequest(assetcat_json)
        # escdet = (escaltiontype_obj.assetdetails_id)
        # print("esc",escdet)
        # grp = (escaltiontype_obj.assetgroup)
        # print("grp",grp)
        user_id = request.user.id
        emp_service = FaApiService(scope)
        emp_id = request.employee_id
        assetcat_serv = AssetentryService(scope)

        resp_obj = assetcat_serv.repost(assetcat_json,emp_id,request)
        if isinstance(resp_obj,dict):
            if 'CbsStatus' in resp_obj:
                if resp_obj['CbsStatus'][0]['Status']=='Success':
                    resp_obj=Success()
                    resp_obj.set_message(SuccessMessage.APPROVED_MESSAGE)
                    resp_obj.set_status(SuccessStatus.SUCCESS)
                    response = HttpResponse(resp_obj, content_type="application/json")
        if isinstance(resp_obj,Error):
            return HttpResponse(resp_obj.get(),content_type='application/json')

        return response

def Accounting_details(request,barcode):
    scope = request.scope
    if request.method == 'GET':
        assetcat_serv = AssetentryService(scope)
        resp_obj = assetcat_serv.Assetentry_get(barcode,request)
        response = HttpResponse(resp_obj.get(), content_type="application/json")

        return response
