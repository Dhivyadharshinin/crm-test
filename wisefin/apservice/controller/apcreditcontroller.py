import json
import traceback
from apservice.data.request.apcreditrequest import APCreditRequest
from apservice.service.apcreditservice import APCreditService
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission


@csrf_exempt
@api_view(['GET','POST','DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def apcredit(request,apinvoiceheader_id):
    if request.method == 'POST':
        from utilityservice.service import api_service
        ap_data = json.loads(request.body)
        scope = request.scope
        apcredit_serv=APCreditService(scope)
        emp_id = request.employee_id
        apinvdtl_list = NWisefinList()
        try:
            for i in ap_data['apcredit']:
                manual=True
                apcrtedit_obj = APCreditRequest(i,manual)
                response_obj = apcredit_serv.apcredit_create(apcrtedit_obj,apinvoiceheader_id, emp_id)
                apinvdtl_list.append(response_obj)
            response = HttpResponse(apinvdtl_list.get(), content_type='application/json')
            return response
        except Exception  as excep:
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return HttpResponse(error_obj.get(), content_type='application/json')
    elif request.method == 'GET':
        return get_apcredit_list(request,apinvoiceheader_id)

    elif request.method == 'DELETE':
        return delete_apcredit_entry(request,apinvoiceheader_id)

def delete_apcredit_entry(request,apinvoiceheader_id):
    scope = request.scope
    apcredit_serv=APCreditService(scope)
    emp_id = request.employee_id
    resp_obj = apcredit_serv.apcredit_delete_entry(apinvoiceheader_id,emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

def get_apcredit_list(request,apinvoiceheader_id):
    from utilityservice.service import api_service
    scope = request.scope
    apcredit_serv=APCreditService(scope)
    emp_id = request.employee_id
    resp_obj = apcredit_serv.fetch_apcredit_list(request,apinvoiceheader_id, emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response




@csrf_exempt
@api_view(['GET','DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_apcredit_single(request,apcredit_id):
    if request.method == 'GET':
        from utilityservice.service import api_service
        scope = request.scope
        apcredit_serv=APCreditService(scope)
        emp_id = request.employee_id
        resp_obj = apcredit_serv.get_apcredit_single(request,apcredit_id,emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_apcredit_single(request,apcredit_id)


def delete_apcredit_single(request,apcredit_id):
    scope = request.scope
    apcredit_serv=APCreditService(scope)
    emp_id = request.employee_id
    resp_obj = apcredit_serv.apcredit_delete(apcredit_id, emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response



@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_aptds(request,creditamount,tds_persent):
    if request.method == 'GET':
        from utilityservice.service import api_service
        scope = request.scope
        apcredit_serv=APCreditService(scope)
        emp_id = request.employee_id
        response_obj = apcredit_serv.fetch_tdsrate_calculation(request,creditamount,tds_persent,emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response