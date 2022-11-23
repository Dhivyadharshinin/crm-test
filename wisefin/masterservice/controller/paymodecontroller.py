import io
import json
from datetime import datetime

import pandas as pd
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from nwisefin.settings import logger
from masterservice.models import PayMode
from masterservice.service.paymentservice import paymentservice
from masterservice.util.masterutil import dictdefault
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from masterservice.data.request.paymoderequest import PaymodeRequest
from masterservice.service.paymodeservice import PaymodeService
from utilityservice.data.response.nwisefinpage import NWisefinPage
from userservice.service.employeeservice import EmployeeService
from utilityservice.data.response.nwisefinlist import NWisefinList

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def paymode(request):
    if request.method == 'POST':
        scope = request.scope
        paymode_service = PaymodeService(scope)
        paymode_obj = json.loads(request.body)
        paymode_json=paymode_obj
        pay_obj = PaymodeRequest(paymode_obj)
        user_id = request.employee_id
        emp_service = EmployeeService(scope)
        empid = emp_service.get_empid_from_userid(user_id)
        resp_obj = paymode_service.create_paymode(pay_obj,empid)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
       return fetch_paymode_list(request)

def fetch_paymode_list(request):
        scope = request.scope
        paymode_service = PaymodeService(scope)
        user_id = request.employee_id
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        resp_obj = paymode_service.fetch_paymode_list(vys_page)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_paymode(request, paymode_id):
    if request.method == 'GET':
        scope = request.scope
        paymode_service = PaymodeService(scope)
        user_id =request.user.id
        resp_obj = paymode_service.fetchpaymode(paymode_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
         return delete_paymode(request, paymode_id)
def delete_paymode(request, paymode_id):
    scope = request.scope
    paymode_service = PaymodeService(scope)
    user_id = request.employee_id
    resp_obj = paymode_service.delete_paymode(paymode_id,user_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def paymode_search(request):
    scope = request.scope
    paymode_service = PaymodeService(scope)
    query = request.GET.get('query')
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = paymode_service.fetch_paymode_search(query,vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def paymode_mtom(request):
    if request.method == 'POST':
        scope = request.scope
        paymode_service = PaymodeService(scope)
        paymode_obj = json.loads(request.body)
        action = request.GET.get('action')
        paymode_json=paymode_obj
        pay_obj = PaymodeRequest(paymode_obj)
        user_id = request.employee_id
        emp_service = EmployeeService(scope)
        empid = emp_service.get_empid_from_userid(user_id)
        resp_obj = paymode_service.create_paymode_mtom(pay_obj,action,empid)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def paymode_name(request):
    query = request.GET.get('query', None)
    scope = request.scope
    paymode = PayMode.objects.get(name=query)
    paymode_data = {"id": paymode.id, "code": paymode.code, "name": paymode.name}
    employee_dic = json.dumps(paymode_data, indent=4)
    return HttpResponse(employee_dic, content_type='application/json')

#micro to micro New
#Get paymode
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_paymodeone(request,paymode_id):
    paymode = PayMode.objects.get(id=paymode_id)
    paymode_data = {"id": paymode.id, "code": paymode.code, "name": paymode.name}
    paymode_dic = json.dumps(paymode_data, indent=4)
    return HttpResponse(paymode_dic, content_type='application/json')
#paymode getlist
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_paymodelist(request):
    paymode_ids = json.loads(request.body)
    paymode_id2 = paymode_ids['paymode_id']
    obj = PayMode.objects.filter(id__in=paymode_id2).values('id', 'name','code')
    paymode_list_data = NWisefinList()
    for i in obj:
        data = {"id": i['id'], "name": i['name'],"code": i['code']}
        paymode_list_data.append(data)
    return HttpResponse(paymode_list_data.get(), content_type='application/json')




@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def supplierbranch_payment(request,supplierbranch_id):
    scope=request.scope
    payment_service = paymentservice(scope)
    user_id = request.employee_id
    emp_service = EmployeeService(scope)
    employee_id = emp_service.get_empid_from_userid(user_id)
    supplier_accno = request.GET.get('supplier_accno',)
    resp_obj = payment_service.fetch_supplierbranch_payment(request, employee_id,supplierbranch_id,supplier_accno)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_paymode_download(request):
    scope = request.scope
    paymode_service = PaymodeService(scope)
    user_id = request.user.id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    pmde_resp = paymode_service.fetch_paymode_list_download(request)
    data = json.loads(json.dumps(pmde_resp.__dict__, default=dictdefault))['data']
    df = pd.DataFrame(data)
    BytesIO = io.BytesIO()
    BytesIO.name = 'EXCEL-DOWNLOAD-(' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ').xlsx'
    writer = pd.ExcelWriter(BytesIO, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1', index=False, startcol=0, startrow=5)
    worksheet = writer.sheets['Sheet1']
    workbook = writer.book
    header_format = workbook.add_format()
    header_format.set_align('center')
    header_format.set_bold()
    worksheet.write_string(2, 2, 'Paymode master excel', header_format)
    writer.save()
    BytesIO.seek(0)
    BytesIO.size = BytesIO.__sizeof__()
    file = ContentFile(BytesIO.read())
    XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response = HttpResponse(file, content_type=XLSX_MIME)
    response['Content-Disposition'] = 'attachment; filename="Paymode master.xlsx"'
    logger.info("Paymode_Download Data:"+str(datetime.now()))
    return response