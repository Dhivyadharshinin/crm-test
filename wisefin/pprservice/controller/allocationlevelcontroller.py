import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from pprservice.data.request.allocationlevelrequest import AllocationLevelRequest,New_AllocationLevelRequest,allocation_request
from pprservice.service.allocationlevelservice import AllocationLevelService
from userservice.service.employeeservice import EmployeeService
from masterservice.models import Bank
from utilityservice.data.response.nwisefinlist import NWisefinList

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def allocationlevel(request):
    if request.method == 'POST':
        scope=request.scope
        business_service = AllocationLevelService(scope)
        business_data = json.loads(request.body)
        business_obj = AllocationLevelRequest(business_data)
        empid = request.employee_id
        resp_obj = business_service.create_allocationlevel(business_obj, empid)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_allocationlevel_list(request)


def fetch_allocationlevel_list(request):
    scope=request.scope
    business_service = AllocationLevelService(scope)
    page = request.GET.get('page', 1)
    query = request.GET.get('query', None)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = business_service.fetch_allocationlevel_list(vys_page,query)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_allocationlevel(request,allocationlevel_id):
    if request.method == 'GET':
        scope=request.scope
        business_service = AllocationLevelService(scope)
        user_id = request.user.id
        resp_obj = business_service.fetch_allocationlevel(allocationlevel_id,user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_allocationlevel(request,allocationlevel_id)


@csrf_exempt
def delete_allocationlevel(request,allocationlevel_id):
    scope=request.scope
    business_service = AllocationLevelService(scope)
    user_id = request.user.id
    resp_obj = business_service.delete_allocation(allocationlevel_id,user_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def allocationlevel_search(request):
    scope=request.scope
    business_service = AllocationLevelService(scope)
    query = request.GET.get('query')
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = business_service.fetch_costdriver_search(query,vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def new_allocation_level_list(request):
    scope = request.scope
    if request.method == 'POST':
        business_data = json.loads(request.body)
        business_obj = New_AllocationLevelRequest(business_data)
        business_service = AllocationLevelService(scope)
        level_resp = business_service.fetch_new_allocation_level(business_obj)
        response = HttpResponse(level_resp.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def new_allocation_pprinsert(request):
    scope = request.scope
    if request.method == 'POST':
        employee_id = request.employee_id
        load_data = json.loads(request.body)
        filter_obj = New_AllocationLevelRequest(load_data)
        business_service = AllocationLevelService(scope)
        final_resp = business_service.allocation_ppr_create(filter_obj,employee_id,request,load_data)
        response = HttpResponse(final_resp.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_core(request):
    scope = request.scope
    if request.method == 'POST':
        filter_obj = json.loads(request.body)
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        filter_obj =allocation_request(filter_obj)
        pprservice = AllocationLevelService(scope)
        response_data = pprservice.get_core_level(filter_obj,vys_page)
        final_resp = pprservice.get_corelevel_logic(response_data.get())
        response = HttpResponse(final_resp.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def bussiness_data(request):
    scope = request.scope
    if request.method == 'GET':
        query = request.GET.get('query')
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        pprservice = AllocationLevelService(scope)
        empid = request.employee_id
        response_data = pprservice.ppr_mstbusinesssegement(query, vys_page)  #
        response = HttpResponse(response_data.get(), content_type="application/json")
        return response
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def bs_data(request):
    scope = request.scope
    if request.method == 'GET':
        query = request.GET.get('query')
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        pprservice = AllocationLevelService(scope)
        empid = request.employee_id
        response_data = pprservice.ppr_businesssegement(query, vys_page)  #
        response = HttpResponse(response_data.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def cc_data(request):
    scope = request.scope
    if request.method == 'GET':
        query = request.GET.get('query')
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        pprservice = AllocationLevelService(scope)
        empid = request.employee_id
        response_data = pprservice.ppr_cc(query, vys_page)  #
        response = HttpResponse(response_data.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ppr_allocation_create(request):
    scope = request.scope
    if request.method == 'POST':
        filter_obj = json.loads(request.body)
        employee_id = request.employee_id
        pprservice =AllocationLevelService(scope)
        data_obj=allocation_request(filter_obj)
        ppr_data =pprservice.insert_allocation(data_obj,employee_id)
        ppr_data=pprservice.to_allocation_create(data_obj,ppr_data,employee_id)
        response = HttpResponse(ppr_data.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_allocation(request, id):
    scope=request.scope
    allocation_service = AllocationLevelService(scope)
    scope = request.scope
    if request.method == 'GET':
        allocation_service = AllocationLevelService(scope)
        user_id = request.employee_id
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        resp_obj = allocation_service.fetch_all(id,vys_page)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def allcation_search(request):
    scope = request.scope
    allocation_service = AllocationLevelService(scope)
    query = request.GET.get('query')
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    if query is not None:
        resp_obj=allocation_service.business_search(query,vys_page)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    else:
        from_date = request.GET.get('from')
        to_date = request.GET.get('to')
    resp_obj =allocation_service.fetch_allocationsearch(query,from_date,vys_page,to_date)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def instatus_edit(request):
    scope=request.scope
    allocation_service = AllocationLevelService(scope)
    scope = request.scope
    if request.method == 'GET':
        allocation_service = AllocationLevelService(scope)
        user_id = request.employee_id
        query = request.GET.get('query')
        status = request.GET.get('status')
        resp_obj = allocation_service.implement_status(query,status,user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_all(request):
    scope=request.scope
    allocation_service = AllocationLevelService(scope)
    scope = request.scope
    if request.method == 'GET':
        allocation_service = AllocationLevelService(scope)
        user_id = request.employee_id
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)

        resp_obj = allocation_service.fetch(request,vys_page)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ppr_data(request):
    scope = request.scope
    if request.method == 'GET':
        bizname = request.GET.get('bizname')
        bs_code=request.GET.get('bs_code')
        cc_code = request.GET.get('cc_code')
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        pprservice = AllocationLevelService(scope)

        empid = request.employee_id
        response_data = pprservice.total_amount(bizname,bs_code,cc_code)  #
        response = HttpResponse(response_data.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def modify_allocation(request):
    scope = request.scope
    if request.method == 'POST':
        filter_obj = json.loads(request.body)
        employee_id = request.employee_id
        pprservice =AllocationLevelService(scope)
        data_obj=allocation_request(filter_obj)
        ppr_data =pprservice.edit_allocationfrom(data_obj,employee_id)
        ppr_data=pprservice.edit_allocationto(data_obj,employee_id)
        response = HttpResponse(ppr_data.get(), content_type="application/json")
        return response