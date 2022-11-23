import json
import traceback
from django.db import transaction
from apservice.data.request.apheaderrequest import APHeaderRequest
from apservice.service.apheaderservice import APHeaderService
from apservice.service.apservice import APService
from apservice.util.aputil import ap_post_api_caller
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_apheader(request,apheader_id):
    if request.method == 'GET':
        from utilityservice.service import api_service
        scope = request.scope
        aphdr_serv=APHeaderService(scope)
        crno = request.GET.get('crno',None)
        emp_id = request.employee_id
        response_obj = aphdr_serv.fetch_apheader_list(request,apheader_id,crno, emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response

@csrf_exempt
@api_view(['GET','POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_apheader(request):
    if request.method == 'POST':
        try:
        #with transaction.atomic(using=DataBase.AP_DB):
            direct_entry=True
            from utilityservice.service import api_service
            scope = request.scope
            aphdr_serv=APHeaderService(scope)
            ap_data = json.loads(request.body)
            ap_obj=APHeaderRequest(ap_data,direct_entry)
            api_serv = api_service.ApiService(scope)
            emp_id = request.employee_id
            response_obj = aphdr_serv.apheader_create(request,ap_data,ap_obj,emp_id)
            #inward completed status update
            aphdr_serv = APHeaderService(scope)
            invhdr_count = aphdr_serv.get_pocket_apinvoiceheader_count(ap_data['inwarddetails_id'])
            api_json = {"api_url": '/inwdserv/inwardstatus_update', "inwarddetails_id": ap_data['inwarddetails_id']}
            api_json['status_id'] = 2
            print('invoice_count ',int(invhdr_count) , int(ap_data.get('invoice_count')))
            if int(invhdr_count) == int(ap_data.get('invoice_count')):
                api_json['status_id'] = 3
            inwardstatusupdate_resp = ap_post_api_caller(request, api_json)
            print('inwardstatusupdate_resp',inwardstatusupdate_resp)
            response = HttpResponse(response_obj.get(), content_type='application/json')
            return response
        except Exception as excep:
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return HttpResponse(error_obj.get(), content_type='application/json')
    elif request.method == 'GET':
        return get_apheader_all_list(request)


def get_apheader_all_list(request):
    scope = request.scope
    aphdr_serv = APHeaderService(scope)
    emp_id = request.employee_id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = aphdr_serv.fetch_apheader_all_list(request,vys_page,emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def aptables_delete(request):
    if request.method == 'DELETE':
        scope = request.scope
        aphdr_serv=APHeaderService(scope)
        emp_id = request.employee_id
        response_obj = aphdr_serv.aptables_delete(request, emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response


@csrf_exempt
@api_view(['DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def aptables_single_delete(request,apheader_id):
    if request.method == 'DELETE':
        scope = request.scope
        aphdr_serv=APHeaderService(scope)
        emp_id = request.employee_id
        response_obj = aphdr_serv.aptables_single_delete(request,apheader_id, emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response


#Transaction details
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_aptransget(request, No):
    if request.method == 'GET':
        scope = request.scope
        aphdr_serv = APHeaderService(scope)
        emp_id = request.employee_id
        response = aphdr_serv.ap_queuedetails(request,No)
        resp_obj = HttpResponse(response.get(), content_type="application/json")
        return resp_obj


@csrf_exempt
@api_view(['GET','DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_apheader_single(request,apheader_id):
    if request.method == 'GET':
        scope = request.scope
        aphdr_serv=APHeaderService(scope)
        emp_id = request.employee_id
        resp_obj = aphdr_serv.fetch_apheader_single(request,apheader_id,emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_apheader_single(request,apheader_id)

def delete_apheader_single(request,apheader_id):
    scope = request.scope
    aphdr_serv=APHeaderService(scope)
    emp_id = request.employee_id
    resp_obj = aphdr_serv.apheader_delete(apheader_id,emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_pocket_apheader(request,inwarddtl_id):
    if request.method == 'GET':
        scope = request.scope
        aphdr_service=APHeaderService(scope)
        emp_id = request.employee_id
        response_obj = aphdr_service.get_pocket_apheader_new(request, emp_id,inwarddtl_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response