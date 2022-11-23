# EmployeePay, EmployeeAdvanceRequest, EmployeeAdvanceApproval
import json
from django.http import HttpResponse


from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from hrmsservice.data.request.employeepayrequest import EmployeePayRequest, EmployeeAdvanceRequestRequest, \
    EmployeeAdvanceApprovalRequest
from hrmsservice.service.employeepayservice import EmployeePayService, EmployeeAdvanceRequestService, \
    EmployeeAdvanceApprovalService
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission


@transaction.atomic
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_employeepay(request):
    scope=request.scope
    service=EmployeePayService(scope)
    if request.method=='POST':
        body_data=json.loads(request.body)
        pay_request=EmployeePayRequest(body_data)
        user_id=request.employee_id
        resp=service.create_employeepay(pay_request,user_id)
        response = HttpResponse(resp.get(), content_type="application/json")
        return response
    else:
        resp=service.summary_employeepay()
        response = HttpResponse(resp.get(), content_type="application/json")
        return response


@transaction.atomic
@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_employeepay(request,id):
    scope=request.scope
    service=EmployeePayService(scope)
    if request.method=='GET':
        resp=service.fetch_employeepay(id)
        response = HttpResponse(resp.get(), content_type="application/json")
        return response
    else:
        resp=service.del_employeepay(id)
        response = HttpResponse(resp.get(), content_type="application/json")
        return response




@transaction.atomic
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_employee_advancerequest(request):
    scope=request.scope
    service=EmployeeAdvanceRequestService(scope)
    if request.method=='POST':
        body_data=json.loads(request.body)
        emp_request=EmployeeAdvanceRequestRequest(body_data)
        user_id=request.employee_id
        resp=service.create_employee_advancerequest(emp_request,user_id)
        response = HttpResponse(resp.get(), content_type="application/json")
        return response
    else:
        resp=service.summary_employee_advancerequest()
        response = HttpResponse(resp.get(), content_type="application/json")
        return response


@transaction.atomic
@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_employee_advancerequest(request,id):
    scope=request.scope
    service=EmployeeAdvanceRequestService(scope)
    if request.method=='GET':
        resp=service.fetch_employee_advancerequest(id)
        response = HttpResponse(resp.get(), content_type="application/json")
        return response
    else:
        resp=service.del_employee_advancerequest(id)
        response = HttpResponse(resp.get(), content_type="application/json")
        return response



@transaction.atomic
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_employee_advanceapproval(request):
    scope=request.scope
    service=EmployeeAdvanceApprovalService(scope)
    if request.method=='POST':
        body_data=json.loads(request.body)
        emp_request=EmployeeAdvanceApprovalRequest(body_data)
        user_id=request.employee_id
        resp=service.create_employee_advanceapproval(emp_request,user_id)
        response = HttpResponse(resp.get(), content_type="application/json")
        return response
    else:
        resp=service.summary_employee_advanceapproval()
        response = HttpResponse(resp.get(), content_type="application/json")
        return response

@transaction.atomic
@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_employee_advanceapproval(request,id):
    scope = request.scope
    service = EmployeeAdvanceApprovalService(scope)
    if request.method=='GET':
        resp = service.fetch_employee_advanceapproval(id)
        response = HttpResponse(resp.get(), content_type="application/json")
        return response
    else:
        resp = service.del_employee_advanceapproval(id)
        response = HttpResponse(resp.get(), content_type="application/json")
        return response









