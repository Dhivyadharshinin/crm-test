import json
from apservice.data.request.invoicepomaprequest import InvoicePOMAPRequest
from apservice.service.invoicepomapservice import APInvoicePOMAPService
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission


@csrf_exempt
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_apmap_invoicepo(request,apinvoicehdr_id,apinvoicedtls_id):
    if request.method == 'POST':
        scope = request.scope
        apmapinvoicepo_serv=APInvoicePOMAPService(scope)
        emp_id = request.employee_id
        ap_data = json.loads(request.body)
        ap_obj=InvoicePOMAPRequest(ap_data)
        response_obj = apmapinvoicepo_serv.apinvoicepomap_create(request,ap_obj,apinvoicehdr_id,apinvoicedtls_id,emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response
    elif request.method == 'GET':
        return get_apmapinvoicepo_all_list(request)

def get_apmapinvoicepo_all_list(request):
    scope = request.scope
    apmapinvoicepo_serv = APInvoicePOMAPService(scope)
    emp_id = request.employee_id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = apmapinvoicepo_serv.get_apinvoicepomap_list(request,vys_page,emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET','DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_apmapinvoicepo(request,apinvoicepomap_id):
    if request.method == 'GET':
        scope = request.scope
        apmapinvoicepo_serv=APInvoicePOMAPService(scope)
        emp_id = request.employee_id
        response_obj = apmapinvoicepo_serv.single_get_apinvoicepo_map(request,apinvoicepomap_id,emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response
    elif request.method == 'DELETE':
        return apmapinvoicepo_single_delete(request,apinvoicepomap_id)

def apmapinvoicepo_single_delete(request,apinvoicepomap_id):
    if request.method == 'DELETE':
        scope = request.scope
        apmapinvoicepo_serv=APInvoicePOMAPService(scope)
        emp_id = request.employee_id
        response_obj = apmapinvoicepo_serv.apinvoicepomap_delete(request,apinvoicepomap_id, emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response