import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import authentication_classes, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from masterservice.data.request.statezonecityrequest import StateZoneRequest,StateAndZoneRequest
from masterservice.util.masterutil import get_zone_type_list
from masterservice.service.statezonecityservice import statezoneService
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from utilityservice.data.response.nwisefinpage import NWisefinPage
from userservice.service.employeeservice import EmployeeService


@csrf_exempt
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_statezonecity(request):
    if request.method=='POST':
        arrobj=json.loads(request.body)
        scope=request.scope
        user_id = request.employee_id
        subject_service = statezoneService(scope)

        arr_obj=StateZoneRequest(arrobj)
        resp_obj=subject_service.create_statezonecity(arr_obj,user_id)
        response=HttpResponse(resp_obj.get(),content_type='application/json')
        return response
    elif request.method == 'GET':
        return statezonecity_list(request)
def statezonecity_list(request):
    scope = request.scope
    subject_service=statezoneService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    statemap_id = request.GET.get('statemap_id')
    resp_obj = subject_service.statezonecity_list(vys_page,statemap_id)
    response = HttpResponse(resp_obj.get(), content_type='application/json')
    return response

@csrf_exempt
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def search_statezone(request):
    scope = request.scope
    statezone_service = statezoneService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    statemap_id = request.GET.get('state')
    resp_obj = statezone_service.search_statezone_list(vys_page, statemap_id)
    response = HttpResponse(resp_obj.get(), content_type='application/json')
    return response


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def zonetype(request):
    resp_obj = get_zone_type_list()
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_stateandzone(request):
    if request.method=='POST':
        scope=request.scope
        arrobj=json.loads(request.body)
        user_id = request.employee_id
        subject_service = statezoneService(scope)

        arr_obj=StateAndZoneRequest(arrobj)
        resp_obj=subject_service.stateandzone_mapping(arr_obj,user_id)
        response=HttpResponse(resp_obj.get(),content_type='application/json')
        return response

    elif request.method == 'GET':
        scope=request.scope
        subject_service = statezoneService(scope)
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        state_name = request.GET.get('state')
        resp_obj = subject_service.statezonemapping_list(vys_page, state_name)
        response = HttpResponse(resp_obj.get(), content_type='application/json')
        return response