from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.http import HttpResponse, JsonResponse
from pprservice.data.request.nac_income_request import ppr_clientrequest, ppr_source_request
from pprservice.util.pprutility import MASTER_SERVICE

from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from pprservice.service.nac_income_service import Income_Service
from rest_framework.permissions import IsAuthenticated
import json
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ppr_assetclass_search(request):
    scope = request.scope
    if request.method == 'GET':
        pprservice = Income_Service(scope)
        response_data = pprservice.fetch_asset_search_list()
        response = HttpResponse(response_data.get(), content_type="application/json")
        return response



@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fileupload_acti_clients(request):
    scope = request.scope
    # if request.method == 'POST':
    #     budget_service=BudgetBuilderservice(scope)
    #
    #     empid =request.emploee_id
    #     type = request.GET.get("type")
    #     resp_obj = budget_service.fileupload_acti_clients()
    #     response= HttpResponse(resp_obj.get(), content_type="application/json")
    if request.method == 'POST':
        file_name = request.FILES.getlist('file')[0].name
        extension = file_name.split('.')[-1]
        scope = request.scope
        budget_service=Income_Service(scope)
        # filetype_check = file_validation.exel_file_validation(extension)
        # user_id = request.user.id
        employee_id = request.employee_id

        # if filetype_check is False:
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.INVALID_FILETYPE)
        #     error_obj.set_description(ErrorDescription.SUPPORTED_FILE_TYPES)
        #     response = HttpResponse(error_obj.get())
        #     return HttpResponse(response, content_type='application/json')
        import pandas as pd
        import numpy as np

        excel_data = pd.read_excel(request.FILES['file'], engine='openpyxl')
        df = pd.DataFrame(excel_data)
        transation_obj = df.fillna(np.nan).replace([np.nan], [0]).to_dict(orient='records')
        resp_obj = budget_service.fileupload_acti_clients(transation_obj,employee_id)
        return HttpResponse(resp_obj.get(), content_type='application/json')

@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fileupload_cc_income(request):
    scope = request.scope
    # if request.method == 'POST':
    #     budget_service=BudgetBuilderservice(scope)
    #
    #     empid =request.emploee_id
    #     type = request.GET.get("type")
    #     resp_obj = budget_service.fileupload_acti_clients()
    #     response= HttpResponse(resp_obj.get(), content_type="application/json")
    if request.method == 'POST':
        file_name = request.FILES.getlist('file')[0].name
        extension = file_name.split('.')[-1]
        scope = request.scope
        budget_service=Income_Service(scope)
        # filetype_check = file_validation.exel_file_validation(extension)
        # user_id = request.user.id
        employee_id = request.employee_id

        # if filetype_check is False:
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.INVALID_FILETYPE)
        #     error_obj.set_description(ErrorDescription.SUPPORTED_FILE_TYPES)
        #     response = HttpResponse(error_obj.get())
        #     return HttpResponse(response, content_type='application/json')
        import pandas as pd
        import numpy as np

        excel_data = pd.read_excel(request.FILES['file'], engine='openpyxl')
        df = pd.DataFrame(excel_data)
        transation_obj = df.fillna(np.nan).replace([np.nan], [0]).to_dict(orient='records')
        resp_obj = budget_service.fileupload_cc_income(transation_obj,employee_id)
        return HttpResponse(resp_obj.get(), content_type='application/json')


@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def income_header_fetch(request):
    if request.method == 'POST':
        scope=request.scope
        budget_service = Income_Service(scope)
        employee_id = request.employee_id
        data=json.loads(request.body)
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        resp_obj = budget_service.income_header_fetch(data, employee_id,vys_page)
        return HttpResponse(resp_obj.get(), content_type='application/json')

@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def income_header_date(request):
    if request.method == 'POST':
        scope=request.scope
        budget_service = Income_Service(scope)
        employee_id = request.employee_id
        data=json.loads(request.body)
        # page = request.GET.get('page', 1)
        # page = int(page)
        # vys_page = NWisefinPage(page, 10)
        if data["Rm_id"]=="":
            data.pop("Rm_id")
        if data["client_id"]=="":
            data.pop("client_id")
        if len(data["assest_class"])==0:
            data.pop("assest_class")
        if data["product_id"]=="":
            data.pop("product_id")



        resp_obj = budget_service.income_header_date(data, employee_id)
        return HttpResponse(resp_obj.get(), content_type='application/json')

@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def income_header_amount(request):
    if request.method == 'POST':
        scope=request.scope
        budget_service = Income_Service(scope)
        employee_id = request.employee_id
        data=json.loads(request.body)
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        resp_obj = budget_service.income_header_amount(data, employee_id,vys_page)
        return HttpResponse(resp_obj, content_type='application/json')

@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def income_amount_date(request):
    if request.method == 'POST':
        scope=request.scope
        budget_service = Income_Service(scope)
        employee_id = request.employee_id
        data=json.loads(request.body)
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        if data["Rm_id"]=="":
            data.pop("Rm_id")
        if data["client_id"]=="":
            data.pop("client_id")
        if len(data["assest_class"])==0:
            data.pop("assest_class")
        if data["product_id"]=="":
            data.pop("product_id")
        resp_obj = budget_service.income_amount_date(data, employee_id,vys_page)
        return HttpResponse(resp_obj, content_type='application/json')

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ppractiveclients_list(request):
    scope = request.scope
    if request.method == 'POST':
        # page = request.GET.get('page', 1)
        # page = int(page)
        # vys_page = NWisefinPage(page, 10)
        filter_obj = json.loads(request.body)
        filter_obj = ppr_clientrequest(filter_obj)
        pprservice = Income_Service(scope)
        ppr_data = pprservice.fetch_ppr_activeclients(filter_obj)
        response = HttpResponse(ppr_data.get(), content_type="application/json")
        return response
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ppractiveclients_date(request):
    scope = request.scope
    if request.method == 'POST':
        # page = request.GET.get('page', 1)
        # page = int(page)
        # vys_page = NWisefinPage(page, 10)
        data = json.loads(request.body)
        # filter_obj = ppr_clientrequest(filter_obj)
        pprservice = Income_Service(scope)
        if data["Rm_id"]=="":
            data.pop("Rm_id")
        if data["client_id"]=="":
            data.pop("client_id")
        if len(data["assest_class"])==0:
            data.pop("assest_class")
        if data["product_id"]=="":
            data.pop("product_id")
        ppr_data = pprservice.ppractiveclients_date(data)
        response = HttpResponse(ppr_data.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ppr_assetclass(request):
    scope = request.scope
    if request.method == 'GET':
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)

        Assettype_id=request.GET.get("assettype_id")
        QUERY = request.GET.get("query")
        TYPE = request.GET.get("type")
        pprservice = Income_Service(scope)
        response_data = pprservice.get_client(Assettype_id,QUERY,TYPE,vys_page)
        response = HttpResponse(response_data.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_masterbuisness(request):
    scope = request.scope
    if request.method == 'GET':
        buisness_name=request.GET.get("buisness_name")
        pprservice = Income_Service(scope)
        response_data = pprservice.get_masterbuisness(buisness_name)
        response = HttpResponse(response_data.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ppr_income_Filedownload(request):
    scope = request.scope
    if request.method == 'POST':
        employee_id = request.employee_id
        data = json.loads(request.body)
        pprservice = Income_Service(scope)
        page = request.GET.get('page', 1)
        page = int(page)
        if data["Rm_id"]=="":
            data.pop("Rm_id")
        if data["client_id"]=="":
            data.pop("client_id")
        if len(data["assest_class"])==0:
            data.pop("assest_class")
        if data["product_id"]=="":
            data.pop("product_id")
        vys_page = NWisefinPage(page, 10)
        response_data = pprservice.income_Filedownload(data,employee_id,scope,0)
        return response_data

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_ppr_sources(request):
    scope = request.scope
    if request.method == 'POST':
        employee_id = request.employee_id
        data = json.loads(request.body)
        filter_obj = ppr_source_request(data)
        pprservice = Income_Service(scope)
        response = pprservice.insert_ppr_sources(filter_obj, employee_id)
        return HttpResponse(response.get(), content_type='application/json')

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_head_groups(request):
    scope = request.scope
    if request.method == 'POST':
        employee_id = request.employee_id
        data = json.loads(request.body)
        filter_obj = ppr_source_request(data)
        pprservice = Income_Service(scope)
        response = pprservice.insert_head_groups(filter_obj, employee_id)
        return HttpResponse(response.get(), content_type='application/json')

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_sub_groups(request):
    scope = request.scope
    if request.method == 'POST':
        employee_id = request.employee_id
        data = json.loads(request.body)
        filter_obj = ppr_source_request(data)
        pprservice = Income_Service(scope)
        response = pprservice.insert_sub_groups(filter_obj, employee_id)
        return HttpResponse(response.get(), content_type='application/json')

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ppr_sources_list(request):
    scope = request.scope
    if request.method == 'POST':
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        filter_obj = json.loads(request.body)
        filter_obj = ppr_source_request(filter_obj)
        pprservice = Income_Service(scope)
        ppr_data = pprservice.fetch_pprsources_list(filter_obj,vys_page)
        response = HttpResponse(ppr_data.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ppr_head_groups_list(request):
    scope = request.scope
    if request.method == 'POST':
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        filter_obj = json.loads(request.body)
        filter_obj = ppr_source_request(filter_obj)
        pprservice = Income_Service(scope)
        ppr_data = pprservice.fetch_headgrps_list(filter_obj,vys_page)
        response = HttpResponse(ppr_data.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ppr_sub_groups_list(request):
    scope = request.scope
    if request.method == 'POST':
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        filter_obj = json.loads(request.body)
        filter_obj = ppr_source_request(filter_obj)
        pprservice = Income_Service(scope)
        ppr_data = pprservice.fetch_subgrps_list(filter_obj,vys_page)
        response = HttpResponse(ppr_data.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_GL_subgrp(request):
    scope = request.scope
    if request.method == 'POST':
        employee_id = request.employee_id
        data = json.loads(request.body)
        filter_obj = ppr_source_request(data)
        pprservice = Income_Service(scope)
        response = pprservice.insert_GL_subgrp(filter_obj, employee_id)
        return HttpResponse(response.get(), content_type='application/json')

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ppr_GL_subgrps_list(request):
    scope = request.scope
    if request.method == 'POST':
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        filter_obj = json.loads(request.body)
        filter_obj = ppr_source_request(filter_obj)
        pprservice = Income_Service(scope)
        ppr_data = pprservice.fetch_GL_subgrp_list(filter_obj,vys_page)
        response = HttpResponse(ppr_data.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def source_list_dropdown(request):
    scope = request.scope
    if request.method == 'GET':
        query=request.GET.get("query")
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        pprservice = Income_Service(scope)
        response_data = pprservice.get_source_list(vys_page,query)
        response = HttpResponse(response_data.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def headgrp_list_dropdown(request):
    scope = request.scope
    if request.method == 'GET':
        query=request.GET.get("query")
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        pprservice = Income_Service(scope)
        response_data = pprservice.get_headgrp_list(vys_page,query)
        response = HttpResponse(response_data.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def subgrp_list_dropdown(request):
    scope = request.scope
    if request.method == 'GET':
        query=request.GET.get("query")
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        pprservice = Income_Service(scope)
        response_data = pprservice.get_subgrp_list(vys_page,query)
        response = HttpResponse(response_data.get(), content_type="application/json")
        return response

def gl_subgroup_list_dropdown(request):
    scope = request.scope
    if request.method == 'GET':
        query=request.GET.get("query")
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        pprservice = Income_Service(scope)
        response_data = pprservice.get_glsubgrp_list(vys_page,query)
        response = HttpResponse(response_data.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ppr_incomegrp_list(request):
    scope = request.scope
    if request.method == 'POST':
        filter_obj = json.loads(request.body)
        filter_obj = ppr_source_request(filter_obj)
        pprservice = Income_Service(scope)
        aa=filter_obj.get_asset_ref()
        ppr_data = pprservice.ppr_incomegrp_logic(filter_obj)
        resp_data = pprservice.ppr_income_logic(1,ppr_data.get(),aa)
        response = HttpResponse(resp_data.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ppr_incomehead_list(request):
    scope = request.scope
    if request.method == 'POST':
        filter_obj = json.loads(request.body)
        filter_obj = ppr_source_request(filter_obj)
        pprservice = Income_Service(scope)
        aa=filter_obj.get_asset_ref()
        ppr_data = pprservice.ppr_incomehead_logic(filter_obj)
        resp_data = pprservice.ppr_income_logic(2, ppr_data.get(), aa)
        response = HttpResponse(resp_data.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ppr_incomecat_list(request):
    scope = request.scope
    if request.method == 'POST':
        filter_obj = json.loads(request.body)
        filter_obj = ppr_source_request(filter_obj)
        pprservice = Income_Service(scope)
        aa=filter_obj.get_asset_ref()
        ppr_data = pprservice.ppr_incomecat_logic(filter_obj)
        resp_data = pprservice.ppr_income_logic(3, ppr_data.get(), aa)
        response = HttpResponse(resp_data.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ppr_income_subcat_list(request):
    scope = request.scope
    if request.method == 'POST':
        filter_obj = json.loads(request.body)
        filter_obj = ppr_source_request(filter_obj)
        pprservice = Income_Service(scope)
        aa=filter_obj.get_asset_ref()
        ppr_data = pprservice.ppr_income_subcat_logic(filter_obj)
        resp_data = pprservice.ppr_income_logic(4, ppr_data.get(), aa)
        response = HttpResponse(resp_data.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def new_ppr_incomegrp(request):
    scope = request.scope
    if request.method == 'POST':
        filter_obj = json.loads(request.body)
        filter_obj = ppr_source_request(filter_obj)
        pprservice = Income_Service(scope)
        aa=filter_obj.get_asset_ref()
        ppr_data = pprservice.new_ppr_incomegrp_logic(filter_obj)
        resp_data = pprservice.ppr_income_logic(1,ppr_data.get(),aa)
        response = HttpResponse(resp_data.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def new_ppr_incomehead(request):
    scope = request.scope
    if request.method == 'POST':
        filter_obj = json.loads(request.body)
        filter_obj = ppr_source_request(filter_obj)
        pprservice = Income_Service(scope)
        aa=filter_obj.get_asset_ref()
        ppr_data = pprservice.new_incomehead_logic(filter_obj)
        resp_data = pprservice.ppr_income_logic(2, ppr_data.get(), aa)
        response = HttpResponse(resp_data.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def new_ppr_incomecat(request):
    scope = request.scope
    if request.method == 'POST':
        filter_obj = json.loads(request.body)
        filter_obj = ppr_source_request(filter_obj)
        pprservice = Income_Service(scope)
        aa=filter_obj.get_asset_ref()
        ppr_data = pprservice.new_incomecat_logic(filter_obj)
        resp_data = pprservice.ppr_income_logic(3, ppr_data.get(), aa)
        response = HttpResponse(resp_data.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def new_income_subcat(request):
    scope = request.scope
    if request.method == 'POST':
        filter_obj = json.loads(request.body)
        filter_obj = ppr_source_request(filter_obj)
        pprservice = Income_Service(scope)
        aa=filter_obj.get_asset_ref()
        ppr_data = pprservice.new_incomesubcat_logic(filter_obj)
        resp_data = pprservice.ppr_income_logic(4, ppr_data.get(), aa)
        response = HttpResponse(resp_data.get(), content_type="application/json")
        return response