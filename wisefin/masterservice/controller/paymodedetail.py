import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from masterservice.data.request.paymodedetailrequest import PaymodedetailRequest
from masterservice.service.paymodedetailservice import paymodedetailservice
from utilityservice.data.response.nwisefinpage import NWisefinPage
from userservice.service.employeeservice import EmployeeService

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated,NWisefinPermission])
def paymodedtl(request):
    if request.method == 'GET':
        scope = request.scope
        paymode_service = paymodedetailservice(scope)
        user_id = request.employee_id
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        resp_obj = paymode_service.fetch_paymodedtl_list(vys_page)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated,NWisefinPermission])
def getcreditgl(request,pay_id):
    if request.method == 'GET':
        scope = request.scope
        paymode_service = paymodedetailservice(scope)
        user_id = request.employee_id
        resp_obj = paymode_service.fetch_creditgl_list(pay_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated,NWisefinPermission])
def paymodedetail_create(request):
    if request.method == 'POST':
        scope=request.scope
        obj = json.loads(request.body)
        paymode_service = paymodedetailservice(scope)
        paymode_obj = PaymodedetailRequest(obj)
        user_id = request.user.id
        emp_service = EmployeeService(scope)
        empid = emp_service.get_empid_from_userid(user_id)
        resp_obj = paymode_service.paymodedetail_create(paymode_obj, empid)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated,NWisefinPermission])
def paymodedetails_active_inactive(request):
    if request.method == 'POST':
        scope=request.scope
        paymode_service = paymodedetailservice(scope)
        user_id = request.user.id
        paymode_data = json.loads(request.body)
        paymodedetails_obj = PaymodedetailRequest(paymode_data)
        emp_service = EmployeeService(scope)
        empid = emp_service.get_empid_from_userid(user_id)
        resp_obj = paymode_service.paymodedetails_active_inactive(request, paymodedetails_obj, empid)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

