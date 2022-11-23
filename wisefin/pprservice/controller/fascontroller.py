import json

from userservice.service.employeeservice import EmployeeService
from nwisefin import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from utilityservice.data.response.nwisefinlist import NWisefinList
from rest_framework.permissions import IsAuthenticated
import pandas as pd
from pprservice.data.response.success import Success as Message
from pprservice.data.response.warning import File_warning
from pprservice.service.fas_service import FasService
from pprservice.data.request.fasrequest import FasRequest

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def income_upload(request):
    scope = request.scope
    if request.method == 'POST':
        levelquery = request.GET.get('level')
        sectorquery = request.GET.get('sector')
        file_obj = request.FILES['file']
        file_obj = pd.read_excel(file_obj).to_dict(orient='records')
        print(list(file_obj[0].keys()))
        columnKeys = ['V_BRANCH_CODE', 'PROD_CODE', 'AC_NO', 'GL DESCRIPTION',
                      'DRCR_IND', 'RELATED_CUSTOMER', 'VERTICAL_CLASS', 'LCY_AMOUNT',
                      'FIC_MIS_DATE', 'BS', 'CC','BS_Code','CC_Code']

        emp_service = EmployeeService(scope)
        empid = request.employee_id
        if list(file_obj[0].keys()) == columnKeys:
            service = FasService(scope)
            response = service.incomedata_create(file_obj,empid,levelquery,sectorquery)
            response = HttpResponse(response.get(),content_type="application/json")
            return response
        else:
            message = Message()
            message.set_status(File_warning.INVALID_COLUMNS)
            return HttpResponse(message.get(),content_type="application/json")

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def level_fetch(request):
    scope = request.scope
    if request.method == 'POST':
        filter_obj = json.loads(request.body)
        request_obj = FasRequest(filter_obj)
        service = FasService(scope)
        response = service.level_fetch(request_obj)
        response = service.level_logic(response.get(),request_obj)
        return JsonResponse(response)

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def expenseGrp_fetch(request):
    scope = request.scope
    if request.method == 'POST':
        filter_obj = json.loads(request.body)
        request_obj = FasRequest(filter_obj)
        service = FasService(scope)
        response = service.fas_expenseGrp_fetch(request_obj)
        response = service.expenseGrp_logic(response.get(), request_obj)
        return JsonResponse(response)

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def expense_fetch(request):
    scope = request.scope
    if request.method == 'POST':
        filter_obj = json.loads(request.body)
        request_obj = FasRequest(filter_obj)
        service = FasService(scope)
        response = service.fas_expense_fetch(request_obj)
        response = service.expense_logic(response.get(), request_obj)
        return JsonResponse(response)

@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def expense_fetch(request):
    scope = request.scope
    if request.method == 'POST':
        filter_obj = json.loads(request.body)
        request_obj = FasRequest(filter_obj)
        service = FasService(scope)
        response = service.fas_expense_fetch(request_obj)
        response = service.expense_logic(response.get(), request_obj)
        return JsonResponse(response)

@csrf_exempt
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def category_fetch(request):
    scope = request.scope
    if request.method == 'POST':
        filter_obj = json.loads(request.body)
        request_obj = FasRequest(filter_obj)
        service = FasService(scope)
        response = service.fas_cat_fetch(request_obj)
        response = service.cat_logic(response.get(), request_obj)
        return JsonResponse(response)

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def subcat_fetch(request):
    scope = request.scope
    filter_obj = json.loads(request.body)
    request_obj = FasRequest(filter_obj)
    service = FasService(scope)
    response = service.fas_subcat_fetch(request_obj)
    response = service.subcat_logic(response.get(), request_obj)
    return JsonResponse(response)


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def hr_data_upload(request):
    scope = request.scope
    if request.method == 'POST':
        file_obj = request.FILES['file']
        file_obj = pd.read_excel(file_obj).to_dict(orient='records')
        Clolumns_keys = ['transactiondate','glno','hr_amount','bizname','bs_code','cc_code','sectorname','branch_code']
        empid =  request.employee_id
        if list(file_obj[0].keys()) == Clolumns_keys:
            service = FasService(scope)
            response = service.hr_data_create(file_obj,empid)
            response = HttpResponse(response.get(), content_type="application/json")
            return response
        else:
            message = Message()
            message.set_status(File_warning.INVALID_COLUMNS)
            return HttpResponse(message.get(),content_type="application/json")

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fas_level_four(request):
    scope = request.scope
    if request.method == 'POST':
        filter_obj = json.loads(request.body)
        request_obj = FasRequest(filter_obj)
        service = FasService(scope)
        response = service.level_four(request_obj)
        response = service.level_four_logic(response.get(), request_obj)
        return JsonResponse(response)
