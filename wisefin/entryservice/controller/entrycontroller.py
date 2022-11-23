import json
from django.http import HttpResponse,JsonResponse
from entryservice.data.request.entryrequest import EntryRequest
from entryservice.service.entryservice  import EntryService
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
#from vysfinutility.data.vysfinpage import VysfinPage
from utilityservice.service.entry_api_service import ApiService
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
import re

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def entrydetails(request):
    if request.method == 'POST':
        scope = request.scope
        entry_service = EntryService(scope)
        entrydetails_obj = json.loads(request.body)
        vysfinservice = ApiService(scope)
        emp_id = request.employee_id
        resp_obj = entry_service.create_entrydetails(request,emp_id,entrydetails_obj)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

    elif request.method == 'GET':
        return fetch_entry_list(request)

def fetch_entry_list(request):
        scope = request.scope
        entry_service = EntryService(scope)
        vysfinservice = ApiService(scope)
        emp_id = request.employee_id
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        query = request.GET.get('query', None)
        resp_obj = entry_service.fetch_all_entry_list(query, vys_page, emp_id, request)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([NWisefinAuthentication, NWisefinPermission])
def fetch_entrydetails(request,entry_id):
    if request.method == 'GET':
        scope = request.scope
        entry_service = EntryService(scope)
        emp_id = request.employee_id
        resp_obj = entry_service.fetch_entry(entry_id,emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_commonentrydetails(request,entry_crno):
    if request.method == 'GET':
        scope = request.scope
        entry_service = EntryService(scope)
        emp_id = request.employee_id
        resp_obj = entry_service.fetch_commonentry(entry_crno,emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def entry_filed_transaction(request):
    if request.method == 'GET':
        scope = request.scope
        entry_service = EntryService(scope)
        emp_id = request.employee_id
        entrydetails_obj = json.loads(request.body)
        page=entrydetails_obj.get('page')
        vys_page = NWisefinPage(page, 10)
        resp_obj = entry_service.entry_failed_transactions(entrydetails_obj,vys_page,emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET','POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def inactive_entry(request):
    if request.method == 'POST':
        scope = request.scope
        entry_service = EntryService(scope)
        emp_id = request.employee_id
        entrydetails_obj = json.loads(request.body)
        crno=entrydetails_obj['crno']
        ap_type=entrydetails_obj['ap_type']
        emp_id = request.employee_id
        resp_obj = entry_service.inactiveentry(crno,emp_id,ap_type)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def entry_succss_data(request):
    if request.method == 'POST':
        try:
            scope = request.scope
            entry_service = EntryService(scope)
            emp_id = request.employee_id
            entrydetails_obj = json.loads(request.body)
            page_number=entrydetails_obj.get('page_number')
            page_size=entrydetails_obj.get('page_size')
            #vys_page = NWisefinPage(page, page_size)
            #offset = (page_number * page_size) - page_size
            #limit = page_number * page_size
            limit=page_size
            offset=page_number*page_size
            output = entry_service.entry_success_transactions(entrydetails_obj,offset,limit,emp_id,scope)
            return JsonResponse(output, safe=False)
        except Exception as e:
            return JsonResponse({"MESSAGE": "ERROR_OCCURED", "DATA": str(e)})