from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
import json
from vendorservice.data.request.riskrequest import RiskRequest
from vendorservice.service.riskservice import RiskService
from utilityservice.data.response.nwisefinpage import NWisefinPage
from vendorservice.service.vendorservice import VendorService


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_vendor_risk(request, vendor_id):
    if request.method == 'POST':
        employee_id = request.employee_id
        scope = request.scope
        risk_obj = json.loads(request.body)
        risk_obj = RiskRequest(risk_obj)
        risk_service = RiskService(scope)
        vendor_service = VendorService(scope)
        mod_status = vendor_service.get_modification_status(vendor_id)
        if mod_status is True:
            resp_obj = risk_service.modification_create_risk(risk_obj, employee_id, vendor_id)
        else:
            resp_obj = risk_service.create_vendor_risk(risk_obj, vendor_id, employee_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_risk_list(request, vendor_id)


def fetch_risk_list(request, vendor_id):
    scope = request.scope
    risk_service = RiskService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = risk_service.fetch_risk_list(request, vys_page, vendor_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_risk(request, vendor_id, risk_id):
    if request.method == 'GET':
        scope = request.scope
        risk_service = RiskService(scope)
        risk_obj = risk_service.fetch_risk(vendor_id, risk_id)
        response = HttpResponse(risk_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        resp_data = delete_risktype(request, risk_id, vendor_id)
        return resp_data


def delete_risktype(request, risk_id, vendor_id):
    scope = request.scope
    employee_id = request.employee_id
    risk_service = RiskService(scope)
    vendor_service = VendorService(scope)
    mod_status = vendor_service.get_modification_status(vendor_id)
    if mod_status is True:
        risk_obj = risk_service.modification_delete_risk(risk_id, vendor_id, employee_id)
    else:
        risk_obj = risk_service.delete_risk(risk_id)
    response = HttpResponse(risk_obj.get(), content_type="application/json")
    return response
