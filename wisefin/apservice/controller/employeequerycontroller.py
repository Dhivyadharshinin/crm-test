import json
from apservice.service.employeequeryservice import employeequeryservice
from apservice.util.aputil import get_aptype_list, get_AP_status_list, get_dropdown_list, get_dropdown_payment_file_list
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
#listall for loan application
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def empq_list(request):
    scope = request.scope
    empqservice = employeequeryservice(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj=empqservice.empq_list(request,vys_page)
    response=HttpResponse(resp_obj.get(),content_type='application/json')
    return response


#OVERALL Get Based on CRNO:
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_crno(request,crno):
    if request.method == 'GET':
        scope = request.scope
        empqservice = employeequeryservice(scope)
        emp_id = request.employee_id
        query = request.GET.get('query')
        resp_obj = empqservice.fetch_crno(request, crno, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


#Search for empquery
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def search_empquery(request):
    scope = request.scope
    empqservice = employeequeryservice(scope)
    grn_obj = json.loads(request.body)
    from utilityservice.service import api_service
    emp_id = request.employee_id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    response_obj = empqservice.empq_search(request,vys_page,grn_obj,emp_id)
    response = HttpResponse(response_obj.get(), content_type='application/json')
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_aptype_list(request):
    resp_obj = get_aptype_list()
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


#pay based on crno:
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_pay(request,crnoo):
    if request.method == 'GET':
        scope = request.scope
        empqservice = employeequeryservice(scope)
        from utilityservice.service import api_service
        emp_id = request.employee_id
        query = request.GET.get('query')
        resp_obj = empqservice.fetch_paymentdetails(request, crnoo, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_apstatus_list(request):
    resp_obj = get_AP_status_list()
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_dropdown_list(request):
    payment_file = request.GET.get('payment_file',None)
    if payment_file:
        resp_obj =get_dropdown_payment_file_list()
    else:
        resp_obj = get_dropdown_list()
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response