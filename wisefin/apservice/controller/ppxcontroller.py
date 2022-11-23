import json
from apservice.data.request.apheaderrequest import APppxHeaderRequest, APppxDetailsRequest
from apservice.service.ppxdetailsservice import APppxDetailsService
from apservice.service.ppxheaderservice import APppxHeaderService
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated



@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ap_ppxheader(request):
    if request.method == 'POST':
        get_api = request.GET.get('get', None)
        if get_api:
            return get_ap_ppxheader(request)
        ap_data = json.loads(request.body)
        scope = request.scope
        ap_ppxhdr_serv=APppxHeaderService(scope)
        ap_obj=APppxHeaderRequest(ap_data)
        emp_id = request.employee_id
        response_obj = ap_ppxhdr_serv.create_ap_ppxheader(request,ap_obj,emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response


def get_ap_ppxheader(request):
    if request.method == 'POST':
        apjson_data = json.loads(request.body)
        scope = request.scope
        ap_ppxhdr_serv = APppxHeaderService(scope)
        page = request.GET.get('page', 1)
        vys_page = NWisefinPage(int(page), 10)
        emp_id = request.employee_id
        response_obj = ap_ppxhdr_serv.get_ppxheader_liquidation(apjson_data,vys_page,emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response




@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_ap_ppxheader_and_details(request):
    if request.method == 'POST':
        from utilityservice.service import api_service
        ap_data = json.loads(request.body)
        scope = request.scope
        header_update = request.GET.get('header_update', None)
        ap_ppxhdr_serv=APppxHeaderService(scope)
        ap_ppxdtl_serv = APppxDetailsService(scope)
        apppxdtl_obj = APppxDetailsRequest(ap_data)
        ap_obj=APppxHeaderRequest(ap_data)
        emp_id = request.employee_id
        apppxheader_id = None
        if header_update:
            #apppxdtl_id
            apppxdtl_id=None
            ap_ppxhdr_serv.ap_ppxheader_update(apppxdtl_obj.get_ppxdetails_balance(), apppxdtl_id, emp_id)
        else:
            #apppxheader_id
            apppxheader_id=None
            hdrresponse_obj = ap_ppxhdr_serv.create_ap_ppxheader(request, ap_obj, emp_id)

        response_obj = ap_ppxdtl_serv.create_ap_ppxdetails(request, apppxheader_id, apppxdtl_obj, emp_id)
        apppxdtl_id=response_obj.__dict__['id']

        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response



@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ap_ppxdetails(request):
    if request.method == 'POST':
        get_api = request.GET.get('get', None)
        delete_api = request.GET.get('delete', None)
        if get_api:
            return get_ap_ppxdetails(request)
        if delete_api == 'true':
            return delete_ap_ppxdetails(request)
        ap_data = json.loads(request.body)
        scope = request.scope
        ap_ppxdtl_serv = APppxDetailsService(scope)
        emp_id = request.employee_id
        response_obj = ap_ppxdtl_serv.create_ap_ppxdetails(request, ap_data, emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response


def get_ap_ppxdetails(request):
    if request.method == 'POST':
        apjson_data = json.loads(request.body)
        scope = request.scope
        ap_ppxdtl_serv = APppxDetailsService(scope)
        page = request.GET.get('page', 1)
        vys_page = NWisefinPage(int(page), 10)
        emp_id = request.employee_id
        response_obj = ap_ppxdtl_serv.get_ppx_liquidation(apjson_data,vys_page,emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response


def delete_ap_ppxdetails(request):
    scope = request.scope
    ap_data = json.loads(request.body)
    ecfheader_id=ap_data['ecfheader_id']
    ap_ppxdtl_serv=APppxDetailsService(scope)
    emp_id = request.employee_id
    resp_obj = ap_ppxdtl_serv.ppxdetails_delete(ecfheader_id,emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response



