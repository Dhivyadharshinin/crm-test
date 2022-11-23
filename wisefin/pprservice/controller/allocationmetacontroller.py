import json
from nwisefin import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from utilityservice.data.response.nwisefinlist import NWisefinList
from rest_framework.permissions import IsAuthenticated
from pprservice.data.request.allocationmetarequest import from_AllocationMeta_request,AllocationToPprrequest
from pprservice.service.allocationmetaservice import AllocationMeta_service
from userservice.service.employeeservice import EmployeeService

from django.db import transaction
import pandas as pd
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
import datetime
# from datetime import datetime,timedelta
@transaction.atomic
@csrf_exempt
@api_view(['GET','POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def allocationmeta_create(request):
    if request.method == 'POST':
        scope=request.scope
        filter_obj = json.loads(request.body)
        allocation_request = from_AllocationMeta_request(filter_obj)
        empid = request.employee_id
        allocationMetaservice=AllocationMeta_service(scope)
        from_response = allocationMetaservice.from_allocation_create(allocation_request,empid)
        to_response = allocationMetaservice.to_allocation_create(allocation_request,from_response,empid)
        response = HttpResponse(from_response.get(), content_type="application/json")
        return response
        # else:
        #     response = HttpResponse(from_response.get(), content_type="application/json")
        #     return response
            # to_response = allocationMetaservice.to_allocation_create(allocation_request,from_response.get(),empid)
        # response = JsonResponse(from_response.get(), content_type="application/json")
        # return response
    elif request.method == 'GET':
        return allocation_fetch_all(request)


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def allocation_fetch_individual(request,id):
    scope=request.scope
    type = request.GET.get('type', None)
    frombscc = request.GET.get('frombscc', None)
    month = request.GET.get('month', None)
    year = request.GET.get('year', None)
    date1 = request.GET.get('date', None)
    if type=='Genrate':
        allocationMetaservice=AllocationMeta_service(scope)
        response = allocationMetaservice.fetch_individual_genrate(frombscc,month,year,date1)
    else:
        allocationMetaservice=AllocationMeta_service(scope)
        response = allocationMetaservice.fetch_individual(id)
    response = HttpResponse(response.get(), content_type="application/json")
    return response



def allocation_fetch_all(request):
    scope=request.scope
    search_key = request.GET.get('query')
    frombscccode = request.GET.get('frombscccode',None)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    allocationMetaservice=AllocationMeta_service(scope)
    response = allocationMetaservice.fetch_all(vys_page,frombscccode)
    response = HttpResponse(response.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def remsbased_allocation(request):
    scope=request.scope
    allocationservice = AllocationMeta_service(scope)
    allocation_type = request.GET.get('type', None)
    bs_code = request.GET.get('bs_code', None)
    cc_code = request.GET.get('cc_code', None)
    transactionmonth = request.GET.get('transactionmonth', None)
    transactionyear = request.GET.get('transactionyear', None)
    resp_obj=[]
    if allocation_type==None:
        resp_obj=allocationservice.remsbased_allocation(int(bs_code),int(cc_code),int(transactionmonth),int(transactionyear))
    elif allocation_type=='otherthenrems':
        resp_obj = allocationservice.otherthenrems_allocation(int(bs_code),int(cc_code),int(transactionmonth),int(transactionyear))
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def tech_allocation(request):
    scope=request.scope
    allocationservice = AllocationMeta_service(scope)
    bs_code = request.GET.get('bs_code', None)
    cc_code = request.GET.get('cc_code', None)
    transactionmonth = request.GET.get('transactionmonth', None)
    transactionyear = request.GET.get('transactionyear', None)
    resp_obj = allocationservice.tech_allocation(bs_code,cc_code,int(transactionmonth),int(transactionyear))
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@transaction.atomic
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def allocationtoppr(request):
    if request.method == 'POST':
        scope=request.scope
        allocationMetaservice=AllocationMeta_service(scope)
        # allocation_obj = json.loads(request.body)
        allocation_data = json.loads(request.body)
        level_id = request.GET.get('level_id', None)
        month = request.GET.get('month', None)
        year = request.GET.get('year', None)
        check_val=allocationMetaservice.checkallocation_genrated(level_id,month,year)
        if check_val==1:
            error_obj = NWisefinError()
            error_obj.set_code('Allocation Already Genrated')
            error_obj.set_description('Allocation Already Genrated')
            response = HttpResponse(error_obj.get(), content_type="application/json")
            return response
        status = request.GET.get('status', 2)
        allocation_array = allocation_data.get('Allocation')
        allocation_list = list()
        for i in allocation_array:
            allocation_obj = AllocationToPprrequest(i)
            allocation_list.append(allocation_obj)
        empid = request.employee_id
        from_response = allocationMetaservice.allocationtoppr(allocation_list,empid)
        response = HttpResponse(from_response.get(), content_type="application/json")
        return response
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def inactive_allocation(request,allocation_id):
    scope=request.scope
    allocationservice = AllocationMeta_service(scope)
    status = request.GET.get('status', 2)
    empid = request.employee_id
    resp_obj = allocationservice.inactive_allocation(allocation_id,empid,status)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def allocationexcel_report(request,allocation_id):
    scope=request.scope
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    user_id = request.user.id
    emp_id =request.employee_id
    par_obj = json.loads(request.body)
    query = request.GET.get('query')
    allocationservice = AllocationMeta_service(scope)
    resp_obj = allocationservice.fetch_individual(allocation_id)
    test = resp_obj.get()
    test2 = json.loads(test)
    d1 = json.dumps(test2['to_data'])
    for d1_data in d1:
        d1['bsname']=d1['bs_data']
    response_data = pd.read_json(d1)
    XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response = HttpResponse(content_type=XLSX_MIME)
    response['Content-Disposition'] = 'attachment; filename="MepUtilization.xlsx"'
    writer = pd.ExcelWriter(response, engine='xlsxwriter')
    final_df = response_data[['bscc_data','bs_data', 'cc_data', 'input_value', 'parameter', 'premium_amount',
                             'ratio', 'to_amount', 'validity_from',
                             'validity_to',
                             ]]
    final_df.columns = ['ALLOCATION FROM', 'BS NAME', 'CC NAME', 'INPUT VALUE', 'PARAMETER', 'PREMIUM AMOUNT',
                        'RATIO', 'TO AMOUNT', 'VALIDITY FROM','VALIDITY TO',
                        # 'GRN AMOUNT',
                        # 'ECF AMOUNT', 'AP AMOUNT', 'UTILIZED AMOUNT', 'UNUTILIZED AMOUNT',
                        # 'ISBUDGETED'
                        ]
    final_df.to_excel(writer, index=False)
    writer.save()
    return HttpResponse(response)

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def genrate_gl(request):
    scope=request.scope
    allocationservice = AllocationMeta_service(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    user_id = request.user.id
    type = request.GET.get('type',None)
    bs_id = request.GET.get('bs_id',None)
    cc_id = request.GET.get('cc_id', None)
    transactionmonth = request.GET.get('transactionmonth', None)
    transactionyear = request.GET.get('transactionyear', None)
    empid = request.employee_id
    resp_obj = allocationservice.genrate_gl(type,bs_id,cc_id,transactionmonth,transactionyear,vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def transaction_ratioallocation(request):
    scope=request.scope
    allocationservice = AllocationMeta_service(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    user_id = request.user.id
    type = request.GET.get('type',None)
    bs_id = request.GET.get('bs_id',None)
    cc_id = request.GET.get('cc_id', None)
    transactionmonth = request.GET.get('transactionmonth', None)
    transactionyear = request.GET.get('transactionyear', None)
    frombscccode = request.GET.get('frombscccode', None)
    allocationto_ppr = request.GET.get('allocationto_ppr', None)
    empid = request.employee_id
    if allocationto_ppr=='Genrate':
        resp_obj = allocationservice.genrate_ratioallocation(type,bs_id,cc_id,transactionmonth,transactionyear,frombscccode,allocationto_ppr)
    else:
        resp_obj = allocationservice.transaction_ratioallocation(type,bs_id,cc_id,transactionmonth,transactionyear,frombscccode,vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response