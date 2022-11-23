import json
import traceback
from apservice.data.request.apinvoicedetailrequest import APDebitRequest
from apservice.service.apdebitservice import APDebitService
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
@api_view(['GET','POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def apdebit(request,apinvoicehdr_id):
    if request.method == 'POST':
        try:
            direct_entry=True
            from utilityservice.service import api_service
            ap_data = json.loads(request.body)
            scope = request.scope
            apdebit_serv=APDebitService(scope)
            emp_id = request.employee_id
            apinvdtl_list = NWisefinList()
            for i in ap_data['apdebit']:
                debit_obj = APDebitRequest(i,direct_entry)
                if 'apinvoicedetail_id' not in i:
                    i['apinvoicedetail_id']=None
                response_obj = apdebit_serv.apdebit_create(debit_obj,apinvoicehdr_id,i['apinvoicedetail_id'], emp_id)
                apinvdtl_list.append(response_obj)
            response = HttpResponse(apinvdtl_list.get(), content_type='application/json')
            return response
        except Exception  as excep:
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return   HttpResponse(error_obj.get(), content_type='application/json')

    elif request.method == 'GET':
        return fetch_apdebit_list(request,apinvoicehdr_id)

def fetch_apdebit_list(request,apinvoicehdr_id):
    scope = request.scope
    apdebit_serv=APDebitService(scope)
    emp_id = request.employee_id
    resp_obj = apdebit_serv.get_apdebit_list(request,apinvoicehdr_id,emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_apdebit_invhdetails_list(request,apinvoicedetails_id):
    scope = request.scope
    apdebit_serv=APDebitService(scope)
    emp_id = request.employee_id
    resp_obj = apdebit_serv.get_apdebit_invoicedetails_list(request,apinvoicedetails_id,emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET','DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_apdebit_single(request,apdebit_id):
    if request.method == 'GET':
        scope = request.scope
        apdebit_serv=APDebitService(scope)
        emp_id = request.employee_id
        resp_obj = apdebit_serv.get_apdebit_single(request,apdebit_id,emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_apdebit_single(request, apdebit_id)


def delete_apdebit_single(request, apdebit_id):
    scope = request.scope
    apdebit_serv=APDebitService(scope)
    emp_id = request.employee_id
    resp_obj = apdebit_serv.apdebit_delete(apdebit_id, emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ap_entrydebit(request):
    if request.method == 'POST':
        ap_data = json.loads(request.body)
        scope = request.scope
        entrytype = request.GET.get('entrytype', None)
        apdebit_serv=APDebitService(scope)
        emp_id = request.employee_id
        response_obj = apdebit_serv.ap_entry_debit(request,ap_data,entrytype,emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response