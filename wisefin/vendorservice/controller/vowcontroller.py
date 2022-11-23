from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from utilityservice.data.response.nwisefinpage import NWisefinPage
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from vendorservice.service.vowservice import VOWService, VendorVOWService


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def pan_exist_check(request):
    scope = request.scope
    pan_no = request.GET.get('pan_no', None)
    vow_serv = VOWService(scope)
    pan_exist = vow_serv.get_pan_exist(pan_no)
    resp = HttpResponse(pan_exist.get(), content_type="application/json")
    return resp


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def branch_summary(request):
    code = request.GET.get('code', None)
    ven_type = request.GET.get('ven_type', 0)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    scope = request.scope
    vow_serv = VendorVOWService(scope)
    resp = vow_serv.get_supplier_summary(code, int(ven_type), vys_page)
    response = HttpResponse(resp.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def branch_details(request):
    code = request.GET.get('code', None)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    scope = request.scope
    vow_serv = VendorVOWService(scope)
    resp = vow_serv.branch_details(code, vys_page)
    response = HttpResponse(resp.get(), content_type="application/json")
    return response

