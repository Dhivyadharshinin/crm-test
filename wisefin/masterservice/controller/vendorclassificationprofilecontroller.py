import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from masterservice.data.request.vendorclassficationprofilerequest import VendorclassficationprofileRequest
from masterservice.service.vendorclassficationprofileservice import VendorclassficationService
from masterservice.util.masterutil import Vendor_classfiction_composite, Vendorclassfication_type, \
    process_composite_type
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission


@csrf_exempt
@api_view(['POST', 'GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def vendorclassfication_create(request):
    if request.method == 'POST':
        data_json = json.loads(request.body)
        scope = request.scope
        user_id = request.employee_id
        for i in data_json:
            vendorclassfication_req = VendorclassficationprofileRequest(i)
            vendorclassfication_obj = VendorclassficationService(scope)
            req_obj = vendorclassfication_obj.vendorclassfication_create(vendorclassfication_req, user_id)
        response = HttpResponse(req_obj.get(), content_type='application/json')
        return response

    elif request.method == 'GET':
        scope = request.scope
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        vendorclassfication_serv = VendorclassficationService(scope)
        req_obj = vendorclassfication_serv.fetch_vendorclassficationprofile(vys_page,request)
        response = HttpResponse(req_obj.get(), content_type='application/json')
        return response

@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_vendorclassfication(request, id):
    if request.method == 'GET':
        scope = request.scope
        vendorclassfication_serv = VendorclassficationService(scope)
        req_obj = vendorclassfication_serv.get_vendorclassfication(id)
        response = HttpResponse(req_obj.get(), content_type='application/json')
        return response
    elif request.method == 'DELETE':
        scope = request.scope
        vendorclassfication_serv = VendorclassficationService(scope)
        req_obj = vendorclassfication_serv.del_vendorclassfication(id)
        response = HttpResponse(req_obj.get(), content_type='application/json')
        return response


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_vendorclassficationtype(request):
    if request.method == 'POST':
        scope = request.scope
        data_json = json.loads(request.body)

        vendorclassfication_serv = VendorclassficationService(scope)

        req_obj = vendorclassfication_serv.get_vendorclassfication_type(data_json)
        response = HttpResponse(req_obj.get(), content_type='application/json')
        return response



@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def period_drop_down(request):
    if request.method == 'GET':
        req_obj = Vendor_classfiction_composite()
        response = HttpResponse(req_obj.get(), content_type='application/json')
        return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def period_drop_downget(request, type_id):
    if request.method == 'GET':
        type_id = int(type_id)
        req_obj = Vendorclassfication_type(type_id)
        response = HttpResponse(req_obj.get(), content_type='application/json')
        return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def process_drop_down(request):
    if request.method == 'GET':
        req_obj = process_composite_type()
        response = HttpResponse(req_obj.get(), content_type='application/json')
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def questiontype_by_vendorcat(request):
    if request.method == 'POST':
        serv=VendorclassficationService(request)
        data_dict = json.loads(request.body)
        req_obj = serv.get_questiontype_by_vendorcat(data_dict)
        req =json.dumps(req_obj,indent=4)
        response = HttpResponse(req, content_type='application/json')
        return response