from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.http import HttpResponse, JsonResponse
from pprservice.data.request.budgetbuilderrequest import budgetbuilderrequest
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission

from rest_framework.permissions import IsAuthenticated

from pprservice.util.pprutility import VENDOR_SERVICE
import json
from pprservice.service.budget_builderservice import BudgetBuilderservice
from pprservice.service.ppr_reportservice import Pprservice as PPRService
from pprservice.data.request.pprfilterrequest import PPRsupplierrequest
from userservice.service.employeeservice import EmployeeService
from utilityservice.data.response.nwisefinpage import NWisefinPage
from vendorservice.service.branchservice import branchservice


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def budget_expensegrp_list(request):
    scope = request.scope
    if request.method == 'POST':
        filter_obj = json.loads(request.body)
        pagequery = request.GET.get("pagequery")
        fromyr = int(filter_obj['finyear'].split("-")[0][2:4]) - 1
        toyr = int(filter_obj['finyear'].split("-")[1][:2]) - 1
        finyr = 'FY' + str(fromyr) + '-' + str(toyr)
        finyear = {'finyear': finyr}
        filter_obj.update(finyear)
        filter_obj = budgetbuilderrequest(filter_obj)
        pprservice = PPRService(scope)
        pprlist = pprservice.new_expensegrp_list(filter_obj)
        budgetservice = BudgetBuilderservice(scope)
        future_bgt = budgetservice.future_budget_expensegrp_list(filter_obj,pagequery)
        budget_list = budgetservice.budget_expensegrp_list(filter_obj)
        compare_data = budgetservice.compare_ppr_bgt_expensegrp(pprlist.get(),budget_list.get(),filter_obj)
        compare_future_data = budgetservice.compare_future_bgt_expensegrp(future_bgt.get(),compare_data,filter_obj,pagequery)
        response_data = budgetservice.new_expensegrp_logic(compare_future_data,filter_obj)
        response = JsonResponse(response_data, content_type="application/json")
        return response
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def budget_expense_list(request):

    if request.method == 'POST':
        scope = request.scope
        pagequery = request.GET.get("pagequery")
        filter_obj = json.loads(request.body)
        fromyr = int(filter_obj['finyear'].split("-")[0][2:4]) - 1
        toyr = int(filter_obj['finyear'].split("-")[1][:2]) - 1
        finyr = 'FY' + str(fromyr) + '-' + str(toyr)
        finyear = {'finyear': finyr}
        filter_obj.update(finyear)
        filter_obj = budgetbuilderrequest(filter_obj)
        pprservice = PPRService(scope)
        pprlist = pprservice.new_expense_list(filter_obj)
        budgetservice = BudgetBuilderservice(scope)
        future_bgt = budgetservice.future_budget_expense_list(filter_obj,pagequery)
        budget_list = budgetservice.budget_expense_list(filter_obj)
        compare_data = budgetservice.compare_ppr_bgt_expense(pprlist.get(),budget_list.get(),filter_obj)
        compare_future_data = budgetservice.compare_future_bgt_expense(future_bgt.get(),compare_data,filter_obj,pagequery)
        respone_data = budgetservice.new_expense_logic(compare_future_data,filter_obj)
        response = JsonResponse(respone_data, content_type="application/json")
        return response
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def budget_subcat_list(request):
    scope = request.scope
    if request.method == 'POST':
        pagequery = request.GET.get("pagequery")
        filter_obj = json.loads(request.body)
        fromyr = int(filter_obj['finyear'].split("-")[0][2:4]) - 1
        toyr = int(filter_obj['finyear'].split("-")[1][:2]) - 1
        finyr = 'FY' + str(fromyr) + '-' + str(toyr)
        finyear = {'finyear': finyr}
        filter_obj.update(finyear)
        filter_obj = budgetbuilderrequest(filter_obj)
        pprservice = PPRService(scope)
        pprlist = pprservice.new_subcat_list(filter_obj)
        budgetservice = BudgetBuilderservice(scope)
        future_bgt = budgetservice.future_budget_subcat_list(filter_obj,pagequery)
        budget_list = budgetservice.budget_subcat_list(filter_obj)
        compare_data = budgetservice.compare_ppr_bgt_subcat(pprlist.get(),budget_list.get(),filter_obj)
        commpare_future_data = budgetservice.compare_ppr_bgt_future_subcat(future_bgt.get(),compare_data,filter_obj,pagequery)
        response_data = budgetservice.new_subcat_logic(commpare_future_data,filter_obj)
        response = JsonResponse(response_data, content_type="application/json")
        return response
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def budget_suppliergrp_list(request):
    scope = request.scope
    if request.method == "POST":
        pagequery = request.GET.get("pagequery")
        filter_obj = json.loads(request.body)
        fromyr = int(filter_obj['finyear'].split("-")[0][2:4]) - 1
        toyr = int(filter_obj['finyear'].split("-")[1][:2]) - 1
        finyr = 'FY' + str(fromyr) + '-' + str(toyr)
        finyear = {'finyear': finyr}
        filter_obj.update(finyear)
        filter_obj = PPRsupplierrequest(filter_obj)
        if pagequery is None:
            value_obj = 'query'
        else:
            value_obj='noquery'
        pprservice = PPRService(scope)
        pprlist = pprservice.supplier_detials_grp(value_obj,filter_obj)
        budgetservice = BudgetBuilderservice(scope)
        budget_list = budgetservice.budget_supplier_detials_grp(value_obj,filter_obj)
        supplier_zeroID = budgetservice.get_budget_supplier_zero(budget_list.get())
        future_bgtlist = budgetservice.future_budget_supplier_detials_grp(value_obj,filter_obj,pagequery)
        compare_ppr_bgt_data = budgetservice.compare_ppr_bgt_suppliergrp(pprlist.get(),budget_list.get(),filter_obj)
        compare_fut_data = budgetservice.compare_future_bgt_supplier(future_bgtlist.get(),compare_ppr_bgt_data,filter_obj,pagequery)
        respone_data = budgetservice.budget_suppliergrp_logic(compare_fut_data,supplier_zeroID,filter_obj)
        response = JsonResponse(respone_data, content_type="application/json")
        return response
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def budget_builder_set(request):
    scope = request.scope
    if request.method == "POST":
        filter_obj = json.loads(request.body)
        divAmount = request.GET.get('divAmount')
        divAmount = budgetbuilderrequest({'divAmount':divAmount})
        bgt_data = filter_obj["data"]
        remark = filter_obj["remark"]

        empid = request.employee_id
        budgetservice = BudgetBuilderservice(scope)
        budget_list = budgetservice.bgt_future_data_set(bgt_data,remark,empid,divAmount)
        response = HttpResponse(budget_list.get(), content_type="application/json")
        return response
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def budget_approver_set(request):
    scope = request.scope
    if request.method == "POST":
        filter_obj = json.loads(request.body)
        divAmount = request.GET.get('divAmount')
        divAmount = budgetbuilderrequest({'divAmount':divAmount})
        bgt_data = filter_obj["data"]
        remark = filter_obj["remark"]

        empid =  request.employee_id
        budgetservice = BudgetBuilderservice(scope)
        budget_list = budgetservice.bgt_future_data_viewer_set(bgt_data,remark,empid,divAmount)
        response = HttpResponse(budget_list.get(), content_type="application/json")
        return response
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def budget_employeebranch(request):
    scope = request.scope
    query = request.GET.get('query')
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    empid = request.employee_id
    budgetservice = BudgetBuilderservice(scope)
    budget_list = budgetservice.Builder_employeebranch(empid,query, vys_page)
    response = HttpResponse(budget_list.get(), content_type="application/json")
    return response
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def view_budget_status(request):
    scope = request.scope
    budgetservice = BudgetBuilderservice(scope)
    query = request.GET.get('query')
    status_list = budgetservice.get_budget_status_dropdown(query)
    response = HttpResponse(status_list.get(), content_type="application/json")
    return response
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_budgetbuilder_finyear(request):
    scope = request.scope
    budgetservice = BudgetBuilderservice(scope)
    query = request.GET.get('query')
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    finyear_list = budgetservice.fetch_finyear_list(query,vys_page)
    response = HttpResponse(finyear_list.get(), content_type="application/json")
    return response
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_budget_remark(request):
    scope = request.scope
    filter_obj = json.loads(request.body)
    budgetservice = BudgetBuilderservice(scope)
    filter_obj = budgetbuilderrequest(filter_obj)
    response = budgetservice.fetch_budget_remarks(filter_obj)
    response = HttpResponse(response.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def new_budget_expensegrp_list(request):
    scope=request.scope
    if request.method == 'POST':
        filter_obj = json.loads(request.body)
        pagequery = request.GET.get("pagequery")
        fromyr = int(filter_obj['finyear'].split("-")[0][2:4]) - 1
        toyr = int(filter_obj['finyear'].split("-")[1][:2]) - 1
        finyr = 'FY' + str(fromyr) + '-' + str(toyr)
        finyear = {'finyear': finyr}
        filter_obj.update(finyear)
        filter_obj = budgetbuilderrequest(filter_obj)
        pprservice = PPRService(scope)
        pprlist = pprservice.new_expensegrp_list(filter_obj)
        budgetservice = BudgetBuilderservice(scope)
        future_bgt = budgetservice.new_future_budget_expensegrp_list(filter_obj,pagequery)
        budget_list = budgetservice.new_budget_expensegrp_list(filter_obj)
        compare_data = budgetservice.compare_ppr_bgt_new_expensegrp(pprlist.get(),budget_list.get(),filter_obj)
        compare_future_data = budgetservice.compare_future_bgt_new_expensegrp(future_bgt.get(),compare_data,filter_obj,pagequery)
        response_data = budgetservice.expensegrp_logic(compare_future_data,filter_obj)
        response = JsonResponse(response_data, content_type="application/json")
        return response


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def new_budget_expense_list(request):
    scope = request.scope
    if request.method == 'POST':
        pagequery = request.GET.get("pagequery")
        filter_obj = json.loads(request.body)
        fromyr = int(filter_obj['finyear'].split("-")[0][2:4]) - 1
        toyr = int(filter_obj['finyear'].split("-")[1][:2]) - 1
        finyr = 'FY' + str(fromyr) + '-' + str(toyr)
        finyear = {'finyear': finyr}
        filter_obj.update(finyear)
        filter_obj = budgetbuilderrequest(filter_obj)
        pprservice = PPRService(scope)
        pprlist = pprservice.new_expense_list(filter_obj)
        budgetservice = BudgetBuilderservice(scope)
        future_bgt = budgetservice.future_budget_new_expense_list(filter_obj,pagequery)
        budget_list = budgetservice.budget_new_expense_list(filter_obj)
        compare_data = budgetservice.compare_ppr_bgt_new_expense(pprlist.get(),budget_list.get(),filter_obj)
        compare_future_data = budgetservice.compare_future_bgt_new_expense(future_bgt.get(),compare_data,filter_obj,pagequery)
        respone_data = budgetservice.expense_logic(compare_future_data,filter_obj)
        response = JsonResponse(respone_data, content_type="application/json")
        return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def new_budget_cat_list(request):
    scope = request.scope
    if request.method == 'POST':
        pagequery = request.GET.get("pagequery")
        filter_obj = json.loads(request.body)
        fromyr = int(filter_obj['finyear'].split("-")[0][2:4]) - 1
        toyr = int(filter_obj['finyear'].split("-")[1][:2]) - 1
        finyr = 'FY' + str(fromyr) + '-' + str(toyr)
        finyear = {'finyear': finyr}
        filter_obj.update(finyear)
        # filter_obj = json.loads(request.body)
        filter_obj = budgetbuilderrequest(filter_obj)
        pprservice = PPRService(scope)
        pprlist = pprservice.ppr_exp_cat_logic(filter_obj)
        budgetservice = BudgetBuilderservice(scope)
        future_bgt = budgetservice.future_budget_cat_list(filter_obj, pagequery)
        budget_list = budgetservice.budget_cat_list(filter_obj)
        compare_data = budgetservice.compare_ppr_bgt_cat(pprlist.get(), budget_list.get(), filter_obj)
        commpare_future_data = budgetservice.compare_ppr_bgt_future_cat(future_bgt.get(), compare_data, filter_obj,
                                                                        pagequery)
        response_data = budgetservice.new_cat_logic(commpare_future_data, filter_obj)
        response = JsonResponse(response_data, content_type="application/json")
        return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def budget_new_subcat_list(request):
    scope = request.scope
    if request.method == 'POST':
        pagequery = request.GET.get("pagequery")
        filter_obj = json.loads(request.body)
        fromyr = int(filter_obj['finyear'].split("-")[0][2:4]) - 1
        toyr = int(filter_obj['finyear'].split("-")[1][:2]) - 1
        finyr = 'FY' + str(fromyr) + '-' + str(toyr)
        finyear = {'finyear': finyr}
        filter_obj.update(finyear)
        filter_obj = budgetbuilderrequest(filter_obj)
        pprservice = PPRService(scope)
        pprlist = pprservice.ppr_exp_subcat_logic(filter_obj)
        budgetservice = BudgetBuilderservice(scope)
        future_bgt = budgetservice.future_budget_new_subcat_list(filter_obj, pagequery)
        budget_list = budgetservice.budget_new_subcat_list(filter_obj)
        compare_data = budgetservice.compare_ppr_bgt_new_subcat(pprlist.get(), budget_list.get(), filter_obj)
        commpare_future_data = budgetservice.compare_ppr_bgt_future_new_subcat(future_bgt.get(), compare_data,
                                                                               filter_obj, pagequery)
        response_data = budgetservice.subcat_logic(commpare_future_data, filter_obj)
        response = JsonResponse(response_data, content_type="application/json")
        return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def budget_draft_set(request):
    scope=request.scope
    if request.method == "POST":
        filter_obj = json.loads(request.body)
        filter_obj = budgetbuilderrequest(filter_obj)
        budgetservice = BudgetBuilderservice(scope)
        bgt_obj = budgetservice.bgt_future_data_checker_set(filter_obj)
        response = HttpResponse(bgt_obj.get(), content_type="application/json")
        return response
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def budget_status_set(request):
    scope = request.scope
    if request.method == "POST":
        filter_obj = json.loads(request.body)
        filter_obj = budgetbuilderrequest(filter_obj)

        empid = request.employee_id
        budgetservice = BudgetBuilderservice(scope)
        level = request.GET.get("level")
        status = request.GET.get("status")
        remark_val = request.GET.get("remark_val")
        bgt_obj = budgetservice.bgt_future_data_status_set(filter_obj,status,level,empid,remark_val)
        response = HttpResponse(bgt_obj.get(), content_type="application/json")
        return response

@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def document_upload(request):
    scope = request.scope
    if request.method == 'POST':
        budget_service=BudgetBuilderservice(scope)

        empid =request.emploee_id
        type = request.GET.get("type")
        resp_obj = budget_service.upload(request,type,empid)
        response= HttpResponse(resp_obj.get(), content_type="application/json")
        return HttpResponse(response, content_type='application/json')


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def supplier_list(request):
    scope=request.scope
    query = request.GET.get('query', None)
    page = request.GET.get('page', 1)
    budgit_service=VENDOR_SERVICE(scope)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj=budgit_service.supplier_list(vys_page,query)


    # scope=request.scope
    # branch_service = branchservice(scope)
    # query = request.GET.get('query', None)
    # page = request.GET.get('page', 1)
    # page = int(page)
    # vys_page = NWisefinPage(page, 10)
    # resp_obj = branch_service.supplier_list(vys_page,query)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response




