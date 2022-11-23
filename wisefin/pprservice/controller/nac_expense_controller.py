from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.http import HttpResponse
from pprservice.data.request.nac_expense_request import  ppr_expense_request as expense_request
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from pprservice.service.nac_expense_service import Expense_Service
from rest_framework.permissions import IsAuthenticated
import json

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ppr_expense_overall_upload(request):
    scope = request.scope
    if request.method == 'POST':
        filter_obj = json.loads(request.body)
        # filter_obj = expense_request(filter_obj)
        employee_id = request.employee_id
        pprservice = Expense_Service(scope)
        ppr_data = pprservice.expense_overall_upload(filter_obj,employee_id,request)
        response = HttpResponse(ppr_data.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ppr_expensegrp_list(request):
    scope = request.scope
    if request.method == 'POST':
        filter_obj = json.loads(request.body)
        filter_obj = expense_request(filter_obj)
        aa=filter_obj.get_asset_ref()
        pprservice = Expense_Service(scope)
        ppr_data = pprservice.ppr_expensegrp_list(filter_obj)
        resp_data = pprservice.ppr_expensegrp_logic(1,ppr_data.get(),aa)
        response = HttpResponse(resp_data.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ppr_expensehead_list(request):
    scope = request.scope
    if request.method == 'POST':
        filter_obj1 = json.loads(request.body)
        filter_obj = expense_request(filter_obj1)
        pprservice = Expense_Service(scope)
        aa=filter_obj.get_asset_ref()
        ppr_data = pprservice.ppr_expensehead_list(filter_obj)
        resp_data = pprservice.ppr_expensegrp_logic(2,ppr_data.get(),aa)
        response = HttpResponse(resp_data.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ppr_category_list(request):
    scope = request.scope
    if request.method == 'POST':
        filter_obj = json.loads(request.body)
        filter_obj = expense_request(filter_obj)
        pprservice = Expense_Service(scope)
        aa=filter_obj.get_asset_ref()
        ppr_data = pprservice.ppr_cat_list(filter_obj)
        resp_data = pprservice.ppr_expensegrp_logic(3,ppr_data.get(),aa)
        response = HttpResponse(resp_data.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ppr_subcategory_list(request):
    scope = request.scope
    if request.method == 'POST':
        filter_obj = json.loads(request.body)
        filter_obj = expense_request(filter_obj)
        aa=filter_obj.get_asset_ref()
        pprservice = Expense_Service(scope)
        ppr_data = pprservice.ppr_subcat_list(filter_obj)
        resp_data = pprservice.ppr_expensegrp_logic(4,ppr_data.get(),aa)
        response = HttpResponse(resp_data.get(), content_type="application/json")
        return response