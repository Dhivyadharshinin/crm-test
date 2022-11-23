import json
from apservice.data.request.apinvoicedetailrequest import APInvoiceDetailsRequest
from apservice.service.apinvoicedetailsservice import APInvoiceDetailService
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission


@csrf_exempt
@api_view(['GET','POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def apinvoicedetails(request,apinvoicehdr_id):
    if request.method == 'POST':
        scope = request.scope
        ap_data = json.loads(request.body)
        apinvdtls_serv=APInvoiceDetailService(scope)
        emp_id = request.employee_id
        apinvdtl_list = NWisefinList()
        for i in ap_data['invoicedtls']:
            apinv_obj = APInvoiceDetailsRequest(i)
            response_obj = apinvdtls_serv.apinvdtl_create(apinv_obj,apinvoicehdr_id, emp_id)
            apinvdtl_list.append(response_obj)
        response = HttpResponse(apinvdtl_list.get(), content_type='application/json')
        return response
    elif request.method == 'GET':
        return fetch_apinvoicedetails_list(request,apinvoicehdr_id)

def fetch_apinvoicedetails_list(request,apinvoicehdr_id):
    scope = request.scope
    apinvdtls_serv=APInvoiceDetailService(scope)
    emp_id = request.employee_id
    print('emp_id ',emp_id)
    resp_obj = apinvdtls_serv.fetch_apinvoicedetails(request,apinvoicehdr_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET','DELETE','POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_apinvoicedetails_single(request,apinvoicedetails_id):
    if request.method == 'GET':
        scope = request.scope
        apinvdtls_serv=APInvoiceDetailService(scope)
        emp_id = request.employee_id
        print('emp_id ',emp_id)
        resp_obj = apinvdtls_serv.get_apinvoicedetails_single(request,apinvoicedetails_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_apinvoicedetails_single(request, apinvoicedetails_id)
    elif request.method == 'POST':
        return update_apinvoicedetails_single(request, apinvoicedetails_id)



def delete_apinvoicedetails_single(request, apinvoicedetails_id):
    scope = request.scope
    apinvdtls_serv=APInvoiceDetailService(scope)
    emp_id = request.employee_id
    resp_obj = apinvdtls_serv.apinvoicedetails_delete(apinvoicedetails_id, emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

def update_apinvoicedetails_single(request, apinvoicedetails_id):
    scope = request.scope
    apinvdtls_serv=APInvoiceDetailService(scope)
    ap_data = json.loads(request.body)
    entry_flag=ap_data['entry_flag']
    emp_id = request.employee_id
    resp_obj = apinvdtls_serv.apinvoicedetails_entryflag_update(apinvoicedetails_id,entry_flag, emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response