import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import authentication_classes, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from masterservice.service.leaveattendanceservice import OrgIpService, OrgDetailsService, AttendanceConfigService, \
    LeaveTypeService, HolidayService
from masterservice.data.request.leaveattendancerequest import OrgIpRequest, OrgDetailsRequest, \
    AttendanceConfigRequest, LeaveTypeRequest, HolidayRequest
from masterservice.service.addressservice import AddressService
from masterservice.data.request.addressrequest import AddressRequest


# org_ip
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def org_ip(request):
    scope = request.scope
    service = OrgIpService(scope)
    if request.method == 'POST':
        # 1 for update and single create 2 for bulk create
        status = int(request.GET.get('status', 1))
        leave_data = json.loads(request.body)
        req_data = OrgIpRequest(leave_data)
        if status == 2:
            resp = service.bulk_create_org_ip(req_data)
        else:
            resp = service.create_org_ip(req_data)
    else:
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        query = request.GET.get('query', None)
        resp = service.org_ip_list(vys_page, query)
    response = HttpResponse(resp.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_ip_org(request, org_id):
    scope = request.scope
    service = OrgIpService(scope)
    if request.method == 'GET':
        resp = service.fetch_org_ip(org_id)
    else:
        resp = service.delete_org_ip(org_id)
    response = HttpResponse(resp.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_org_detail_ips(request, org_id):
    scope = request.scope
    service = OrgIpService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp = service.get_org_details_ips(org_id, vys_page)
    response = HttpResponse(resp.get(), content_type="application/json")
    return response


# org_details
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def org_details(request):
    scope = request.scope
    employee_id = request.employee_id
    service = OrgDetailsService(scope)
    if request.method == 'POST':
        leave_data = json.loads(request.body)
        req_data = OrgDetailsRequest(leave_data)
        res_obj = AddressRequest(leave_data["address"])
        res = AddressService(scope).create_address(res_obj, employee_id)
        resp = service.create_org_details(req_data,res,employee_id)
    else:
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        query = request.GET.get('query', None)
        resp = service.org_details_list(vys_page, query)
    response = HttpResponse(resp.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_org_details(request, detail_id):
    scope = request.scope
    service = OrgDetailsService(scope)
    if request.method == 'GET':
        resp = service.fetch_org_details(detail_id)
    else:
        resp = service.delete_org_details(detail_id)
    response = HttpResponse(resp.get(), content_type="application/json")
    return response


# attendance
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def attendance(request):
    scope = request.scope
    employee_id = request.employee_id
    service = AttendanceConfigService(scope)
    if request.method == 'POST':
        leave_data = json.loads(request.body)
        req_data = AttendanceConfigRequest(leave_data)
        resp = service.create_attendance_config(req_data, employee_id)
    else:
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        query = request.GET.get('query', None)
        resp = service.attendance_config_list(vys_page, query)
    response = HttpResponse(resp.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_attendance(request, attendance_id):
    scope = request.scope
    service = AttendanceConfigService(scope)
    if request.method == 'GET':
        resp = service.fetch_attendance_config(attendance_id)
    else:
        resp = service.delete_attendance_config(attendance_id)
    response = HttpResponse(resp.get(), content_type="application/json")
    return response


# leave type
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def leave_type(request):
    scope = request.scope
    employee_id = request.employee_id
    service = LeaveTypeService(scope)
    if request.method == 'POST':
        leave_data = json.loads(request.body)
        req_data = LeaveTypeRequest(leave_data)
        resp = service.create_leave_type(req_data, employee_id)
    else:
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        query = request.GET.get('query', None)
        resp = service.leave_type_list(vys_page, query)
    response = HttpResponse(resp.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_leave_type(request, type_id):
    scope = request.scope
    service = LeaveTypeService(scope)
    if request.method == 'GET':
        resp = service.fetch_leave_type(type_id)
    else:
        resp = service.delete_leave_type(type_id)
    response = HttpResponse(resp.get(), content_type="application/json")
    return response


# Holiday
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def holiday(request):
    scope = request.scope
    employee_id = request.employee_id
    service = HolidayService(scope)
    if request.method == 'POST':
        leave_data = json.loads(request.body)
        req_data = HolidayRequest(leave_data)
        resp = service.create_holiday(req_data, employee_id)
    else:
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        query = request.GET.get('query', None)
        resp = service.holiday_list(vys_page, query)
    response = HttpResponse(resp.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_holiday(request, holiday_id):
    scope = request.scope
    service = HolidayService(scope)
    if request.method == 'GET':
        resp = service.fetch_holiday(holiday_id)
    else:
        resp = service.delete_holiday(holiday_id)
    response = HttpResponse(resp.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def org_arc_details(request,org_id):
    scope = request.scope
    employee_id = request.employee_id
    service = OrgDetailsService(scope)
    if request.method == 'POST':
        org_data = json.loads(request.body)
        req_data = OrgDetailsRequest(org_data)
        address_obj = AddressRequest(org_data["address"])
        address_serv = AddressService(scope).create_address(address_obj, employee_id)
        org_serv = service.create_org_arc_details(req_data, address_serv, org_id)
        response = HttpResponse(org_serv.get(), content_type="application/json")
        return response
    else:
        action = request.GET.get('action')
        if action == 'deactivate':
            resp = service.org_arc_deactivate(org_id)
        else:
            resp = service.fetch_org_arc_details(org_id)
        response = HttpResponse(resp.get(), content_type="application/json")
        return response

