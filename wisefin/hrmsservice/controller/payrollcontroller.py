# WorkWeek, WorkShift, PayDay, PayrollConfigStatus


import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from hrmsservice.data.request.payrollrequest import WorkWeekRequest, WorkShiftRequest, PayDayRequest, \
    PayrollConfigStatusRequest
from hrmsservice.service.payrollservice import WorkWeekService, WorkShiftService, PayDayService, \
    PayrollConfigStatusService
from django.db import transaction


@transaction.atomic
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])

def create_workweek(request):
    scope = request.scope
    work_service = WorkWeekService(scope)
    if request.method == 'POST':
        body_data=json.loads(request.body)
        # work_request= WorkWeekRequest(body_data)
        user_id = request.employee_id
        resp_obj=work_service.create_workweek(body_data,user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    else:
        resp_obj = work_service.summary_workweek()
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


# @transaction.atomic
# @csrf_exempt
# @api_view(['DELETE','GET'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def fetch_workweek(request,id):
#     scope = request.scope
#     work_service = WorkWeekService(scope)
#     if request.method == 'DELETE':
#         # user_id = request.employee_id
#         resp_obj = work_service.del_workweek(id)
#         response=HttpResponse(json.dumps(resp_obj),content_type='application/json')
#         return response
#     else:
#         resp_obj = work_service.fetch_workweek(id)
#         response = HttpResponse(json.dumps(resp_obj), content_type='application/json')
#         return response

# @transaction.atomic
# @csrf_exempt
# @api_view(['GET'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def search_workweek(request,day):
#     scope=request.scope
#     if request.method == 'GET':
#         work_service =WorkWeekService(scope)
#         resp_obj = work_service.srch_workweek(day)
#         response=HttpResponse(json.dumps(resp_obj),content_type='application/json')
#         return response




@transaction.atomic
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_WorkShift(request):
    scope = request.scope
    work_service = WorkShiftService(scope)
    if request.method == 'POST':
        body_data=json.loads(request.body)
        work_request= WorkShiftRequest(body_data)
        user_id = request.employee_id
        resp_obj=work_service.create_WorkShift(work_request,user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    else:
        resp_obj = work_service.summary_WorkShift()
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@transaction.atomic
@csrf_exempt
@api_view(['DELETE','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_WorkShift(request,id):
    scope = request.scope
    work_service = WorkShiftService(scope)
    if request.method == 'DELETE':
        # user_id = request.employee_id
        resp_obj = work_service.del_WorkShift(id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    else:
        resp_obj = work_service.fetch_WorkShift(id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response



@transaction.atomic
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_payday(request):
    scope=request.scope
    serv=PayDayService(scope)
    if request.method == 'POST':
        body=json.loads(request.body)
        pay_request=PayDayRequest(body)
        user_id=request.employee_id
        resp=serv.create_payday(pay_request,user_id)
        response=HttpResponse(resp.get(), content_type="application/json")
        return response

@transaction.atomic
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_payday(request,id):
    scope = request.scope
    serv = PayDayService(scope)
    resp = serv.fetch_payday(id)
    response = HttpResponse(resp.get(), content_type="application/json")
    return response

@transaction.atomic
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_payrollconfigstatus(request):
    scope = request.scope
    serv = PayrollConfigStatusService(scope)
    if request.method == 'POST':
        body = json.loads(request.body)
        roll_request =  PayrollConfigStatusRequest(body)
        user_id = request.employee_id
        resp = serv.create_payrollconfigstatus(roll_request,user_id)
        response = HttpResponse(resp.get(), content_type="application/json")
        return response


@transaction.atomic
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_payrollconfigstatus(request,id):
    scope = request.scope
    serv = PayrollConfigStatusService(scope)
    resp = serv.fetch_payrollconfigstatus(id)
    response = HttpResponse(resp.get(), content_type="application/json")
    return response















