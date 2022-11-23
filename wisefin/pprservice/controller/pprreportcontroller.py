import json
from nwisefin import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from pprservice.service.ppr_reportservice import Pprservice as PPRService
from pprservice.data.request.pprfilterrequest import PPRreportrequest, PPRsupplierrequest, Pprccbsrequest
from utilityservice.service.ta_api_service import ApiService
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission


val_url = settings.VYSFIN_URL
from nwisefin.settings import SERVER_IP
import base64
import requests

# @csrf_exempt
# @api_view(['GET', 'POST'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def pprinsert(request):
#     scope = request.scope
#     if request.method == 'GET':
#         getreq = request.GET.get("term")
#         if getreq == 'log_main':
#             pprservice = PPRService(scope)
#             pprserv_arr = []
#             i = 0
#             while True:
#                 arr = pprservice.pprlog_main(i, i + 10)
#                 if len(arr) <= 0:
#                     break
#                 pprserv = pprservice.create_ppr(arr)
#                 pprserv_arr.append(pprserv.get())
#                 i = i + 10
#             response = {"MESSAGE":pprserv_arr}
#             response = JsonResponse(response, content_type="application/json")
#             return response
#         elif getreq == 'mono_log':
#             ppr_mono_log = ppr_log()
#             response = JsonResponse(ppr_mono_log, content_type="application/json")
#             return response
#         elif getreq == 'pprmonolog':
#             pprmonolog = ppr_monolog()
#             response = JsonResponse(pprmonolog, content_type="application/json")
#             return response
#         elif getreq == 'ppr_scheduler':
#             run_ppr_scheduler()
#             ppr = json.dumps({"MESSAGE":"scheduler_triggered"})
#             response = HttpResponse(ppr, content_type="application/json")
#             return response
#
# @csrf_exempt
# @api_view(['GET'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def ppr_nac_insert(request):
#     scope = request.scope
#     getreq = request.GET.get("term")
#     if getreq == "mono_log":
#         response = run_monolog_nac()
#         response = JsonResponse(response, content_type="application/json")
#         return response
#     elif getreq == "mono_micro_log":
#         ppr_mono_log = ppr_log()
#         response = JsonResponse(ppr_mono_log, content_type="application/json")
#         return response
#     elif getreq == "micro_log_main":
#         pprservice = PPRService(scope)
#         pprserv_arr = []
#         i = 0
#         while True:
#             arr = pprservice.pprlog_main(i, i + 10)
#             if len(arr) <= 0:
#                 break
#             pprserv = pprservice.create_ppr(arr)
#             pprserv_arr.append(pprserv.get())
#             i = i + 10
#         response = {"MESSAGE": pprserv_arr}
#         response = JsonResponse(response, content_type="application/json")
#         return response
#
#
# @csrf_exempt
# @api_view(['GET'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def ppr_nac_insert_single(request):
#     scope = request.scope
#     mono = run_monolog_nac()
#     ppr_mono_log = ppr_log()
#     pprservice = PPRService(scope)
#     pprserv_arr = []
#     i = 0
#     while True:
#         arr = pprservice.pprlog_main(i, i + 10)
#         if len(arr) <= 0:
#             break
#         pprserv = pprservice.create_ppr(arr)
#         pprserv_arr.append(pprserv.get())
#         i = i + 10
#     response = {"MESSAGE": pprserv_arr}
#     response = JsonResponse(response, content_type="application/json")
#     return response
#

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ppr_report(request):
    scope = request.scope
    if request.method == 'POST':
        filter_obj = json.loads(request.body)
        filter_obj = PPRreportrequest(filter_obj)
        pprservice = PPRService(scope)
        pprlist = pprservice.ppr_list(filter_obj)
        ppr_response = pprservice.ppr_businesslogic(pprlist.get(), filter_obj)
        response = JsonResponse(ppr_response, content_type="application/json")
        return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def finyear_search(request):
    scope = request.scope
    if request.method == 'GET':
        query = request.GET.get('query')
        page = request.GET.get('page', 1)
        page = int(page)
        scope=request.scope
        vys_page = NWisefinPage(page, 10)
        pprservice = PPRService(scope)
        response_data = pprservice.fetch_finyear_search_list(query, vys_page)
        response = HttpResponse(response_data.get(), content_type="application/json")
        return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ppr_supplier(request):
    scope = request.scope
    if request.method == 'GET':
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        data_get = {
            "apexpense_id": request.GET.get('apexpense_id'),
            "apsubcat_id": request.GET.get('apsubcat_id'),
            "transactionmonth": request.GET.get('transactionmonth'),
            "quarter": request.GET.get('quarter'),
            "masterbusinesssegment_name": request.GET.get('masterbusinesssegment_name'),
            "sectorname": request.GET.get('sectorname'),
            "yearterm": request.GET.get('yearterm'),
            "divAmount": request.GET.get('divAmount'),
            "finyear":request.GET.get('finyear'),
            "bs_name":request.GET.get('bs_name'),
            "cc_name":request.GET.get('cc_name'),
            "apinvoicebranch_id":request.GET.get('apinvoicebranch_id')
        }
        filter_obj = PPRsupplierrequest(data_get)
        pprservice = PPRService(scope)
        supplierdetials = pprservice.supplier_detial_individual(filter_obj,vys_page)
        # response_data = pprservice.Suppliergrp_logic(supplierdetials.get())
        response = HttpResponse(supplierdetials.get(), content_type="application/json")
        return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ppr_mstbusiness_segment(request):
    scope = request.scope
    if request.method == 'GET':
        budget_builder_dropDown = request.GET.get('budget_builder')
        sectorid = request.GET.get('sectorid')
        branchid = request.GET.get('branchid')
        # branchcode = request.GET.get('branchcode')
        query = request.GET.get('query')
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        pprservice = PPRService(scope)

        empid =  request.employee_id
        response_data = pprservice.ppr_mstbusinesssegement(sectorid, query, vys_page,empid,branchid,budget_builder_dropDown)#
        response = HttpResponse(response_data.get(), content_type="application/json")
        return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ppr_businesssegment(request):
    scope = request.scope
    if request.method == 'GET':
        budget_builder_dropDown = request.GET.get('budget_builder')
        mstbusinessid = request.GET.get('mstbusinessid')
        branchid = request.GET.get('branchid')
        # branchcode = request.GET.get('branchcode')
        query = request.GET.get('query')
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        pprservice = PPRService(scope)

        empid = request.employee_id
        response_data = pprservice.businesssegement(mstbusinessid, query, vys_page,empid,branchid,budget_builder_dropDown)#
        response = HttpResponse(response_data.get(), content_type="application/json")
        return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ppr_costcentre(request):
    scope = request.scope
    businessid = request.GET.get('businessid')
    query = request.GET.get('query')
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    service =ApiService(scope)
    pro_list = service.get_cc_details(businessid, query, vys_page)
    response = HttpResponse(pro_list.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ppr_suppliergrp(request):
    scope = request.scope
    filter_obj = json.loads(request.body)
    filter_obj = PPRsupplierrequest(filter_obj)
    pprservice = PPRService(scope)
    supplier_data = pprservice.supplier_detials_grp(filter_obj)
    supplier_detialsgrp = pprservice.suppliergrp_logic(supplier_data.get(),filter_obj)
    response = JsonResponse(supplier_detialsgrp, content_type="application/json")
    return response


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ppr_ccbsdetials(request):
    scope = request.scope
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    filter_obj = json.loads(request.body)
    filter_obj = Pprccbsrequest(filter_obj)
    pprservice = PPRService(scope)
    ccbs_data = pprservice.fetch_ppr_ccbs(filter_obj,vys_page)
    response = HttpResponse(ccbs_data.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def new_expense_list(request):
    scope = request.scope
    if request.method == 'POST':
        # page = request.GET.get('page', 1)
        # page = int(page)
        # vys_page = PPRVysfinPage(page, 5)
        filter_obj = json.loads(request.body)
        filter_obj = PPRreportrequest(filter_obj)
        pprservice = PPRService(scope)
        newexpense = pprservice.new_expense_list(filter_obj)#vys_page
        expense_response = pprservice.new_expense_logic(newexpense.get(), filter_obj)
        response = JsonResponse(expense_response, content_type="application/json")
        return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def new_expensegrp_list(request):
    scope = request.scope
    if request.method == 'POST':
        # page = request.GET.get('page', 1)
        # page = int(page)
        # vys_page = VysfinPage(page, 10)
        filter_obj = json.loads(request.body)
        filter_obj = PPRreportrequest(filter_obj)
        pprservice = PPRService(scope)
        newexpensegrp = pprservice.new_expensegrp_list(filter_obj)
        print(newexpensegrp.get())
        expensegrp_response = pprservice.new_expensegrp_logic(newexpensegrp.get(),filter_obj)
        print(expensegrp_response)
        response = JsonResponse(expensegrp_response,content_type="application/json")
        return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def new_subcat_list(request):
    scope = request.scope
    if request.method == 'POST':
        # page = request.GET.get('page', 1)
        # page = int(page)
        # vys_page = PPRVysfinPage(page, 5)
        filter_obj = json.loads(request.body)
        filter_obj = PPRreportrequest(filter_obj)
        pprservice = PPRService(scope)
        newsubcat = pprservice.new_subcat_list(filter_obj)#vys_page
        subcat_response = pprservice.new_subcat_logic(newsubcat.get(),filter_obj)
        response = JsonResponse(subcat_response.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def new_expensegrptable_set(request):
    scope = request.scope
    pprservice = PPRService(scope)
    expensegrpTable = pprservice.new_expensegrptable()
    response = HttpResponse(expensegrpTable.get(), content_type="application/json")
    return response



@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ppr_ecf(request):
    scope = request.scope
    if request.method == 'POST':
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        filter_obj = json.loads(request.body)
        filter_obj = PPRsupplierrequest(filter_obj)
        pprservice = PPRService(scope)
        ecf_detials = pprservice.ECF_detials(filter_obj,vys_page)
        response = HttpResponse(ecf_detials, content_type="application/json")
        return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ppr_ecf_Filelist(request):
    scope = request.scope
    filter_obj = json.loads(request.body)
    filter_obj = PPRsupplierrequest(filter_obj)
    pprservice = PPRService(scope)
    ecf_detials = pprservice.Ecf_filesList(filter_obj)
    response = HttpResponse(ecf_detials.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ppr_ecf_Filedownload(request):
    scope = request.scope
    filename = request.GET.get("filename")
    cr_no = request.GET.get("cr_no")
    mono_fileid = request.GET.get("file_gid")
    mono_invoiceheaderid = request.GET.get("invoiceheaderid")

    empid = request.employee_id
    pprservice = PPRService(scope)
    fileDownoad = pprservice.Ecf_FileDownload(filename,cr_no,mono_fileid,mono_invoiceheaderid,empid)
    return fileDownoad

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ppr_supplier_dropdown(request):
    scope = request.scope
    query = request.GET.get('query')
    filter_obj = json.loads(request.body)
    fromyr = int(filter_obj['finyear'].split("-")[0][2:4]) - 1
    toyr = int(filter_obj['finyear'].split("-")[1][:2]) - 1
    finyr = 'FY' + str(fromyr) + '-' + str(toyr)
    finyear = {'finyear': finyr}
    filter_obj.update(finyear)
    filter_obj = PPRsupplierrequest(filter_obj)
    pprservice = PPRService(scope)
    # response = pprservice.supplier_dropdown(filter_obj)
    response = pprservice.pprsupplier_dropdown(filter_obj,query)
    response = HttpResponse(response.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def new_cat_list(request):
    scope = request.scope
    if request.method == 'POST':
        filter_obj = json.loads(request.body)
        filter_obj = PPRreportrequest(filter_obj)
        pprservice = PPRService(scope)
        response_data = pprservice.ppr_exp_cat_logic(filter_obj)
        # response1=pprservice.ppr_exp_cat_logic(response_data.get(),filter_obj)
        response1=pprservice.new_cat_logic(response_data.get(),filter_obj)
        response = JsonResponse(response1, content_type="application/json")
        return response


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def new_subcat_list(request):
    scope = request.scope
    if request.method == 'POST':
        filter_obj = json.loads(request.body)
        filter_obj = PPRreportrequest(filter_obj)
        pprservice = PPRService(scope)
        subcat_obj = pprservice.ppr_exp_subcat_logic(filter_obj)
        response = pprservice.new_subcat_logic(subcat_obj.get(),filter_obj)
        response = JsonResponse(response, content_type="application/json")
        return response


def get_authtoken_PPR():
    ip_address=SERVER_IP+'/usrserv/auth_token'
    username = 'apuser'
    password = b'vsolv123'
    password = base64.b64encode(password)
    password=password.decode("utf-8")
    datas = json.dumps({"username": username, "password": password})
    resp = requests.post(ip_address,  data=datas,verify=False)
    token_data = json.loads(resp.content.decode("utf-8"))
    ### Validations
    if resp.status_code == 200:
        return token_data["token"]
        # response = HttpResponse(token_data["token"], content_type="application/json")
        # return response
    # else:
    #     response = HttpResponse('token_data["token"]', content_type="application/json")
    #     return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def new_expensegrp_masterlist(request):
    scope = request.scope
    if request.method == 'POST':
        # page = request.GET.get('page', 1)
        # page = int(page)
        # vys_page = VysfinPage(page, 10)
        filter_obj = json.loads(request.body)
        filter_obj = PPRreportrequest(filter_obj)
        pprservice = PPRService(scope)
        flag = request.GET.get('is_asset','N')
        newexpensegrp = pprservice.new_expensegrp_masterlist(filter_obj,flag)
        expensegrp_response = pprservice.new_expensegrp_logic(newexpensegrp.get(),filter_obj)
        response = JsonResponse(expensegrp_response,content_type="application/json")
        return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def new_expense_masterlist(request):
    scope = request.scope
    if request.method == 'POST':
        # page = request.GET.get('page', 1)
        # page = int(page)
        # vys_page = PPRVysfinPage(page, 5)
        filter_obj = json.loads(request.body)
        filter_obj = PPRreportrequest(filter_obj)
        pprservice = PPRService(scope)
        newexpense = pprservice.new_expense_masterlist(filter_obj)  # vys_page
        expense_response = pprservice.new_expense_logic(newexpense.get(), filter_obj)
        response = JsonResponse(expense_response, content_type="application/json")
        return response

