import io
import json
from datetime import datetime

import pandas as pd
from django.core.files.base import ContentFile

from masterservice.data.response.delmatresponse import DelmatResponse
from masterservice.util.masterutil import Delmat
from masterservice.service.delmatservice import DelmatService
from nwisefin.settings import logger
from userservice.service.employeeservice import EmployeeService
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinpage import NWisefinPage
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from masterservice.data.request.delmatrequest import DelmatRequest
from masterservice.util.masterutil import get_delmat_type_list, dictdefault
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage
from utilityservice.service.api_service import ApiService
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from docservice.util.docutil import DocModule, DocPrefix

# @csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_delmat(request):
    if request.method == 'POST':
        scope = request.scope
        delmat_data = json.loads(request.body)
        delmat_obj = DelmatRequest(delmat_data)
        emp_id = request.employee_id
        delmat_service = DelmatService(scope)
        # with transaction.atomic(using=DataBase.PRPO_DB):
        response_obj = delmat_service.create_Delmat(delmat_obj, emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response
    elif request.method == 'GET':
        return fetch_delmat_list(request)

def fetch_delmat_list(request):
    scope = request.scope
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    delmat_service = DelmatService(scope)
    emp_id = request.employee_id
    response_obj = delmat_service.fetch_Delmat_list(vys_page, emp_id, request)
    response = HttpResponse(response_obj.get(), content_type="application/json")
    return response

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def delmat_download(request):
    scope = request.scope
    delmat_service = DelmatService(scope)
    user_id = request.user.id
    response_obj = delmat_service.fetch_delmat_download(user_id, request)
    data = json.loads(json.dumps(response_obj.__dict__, default=dictdefault))['data']
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
    worksheet.write_string(2, 2, 'Delmat Maker Master Excel', header_format)
    writer.save()
    BytesIO.seek(0)
    BytesIO.size = BytesIO.__sizeof__()

    # file='Delmat Maker Master Excel'
    # XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    # response = HttpResponse(1, content_type=XLSX_MIME)
    # response['Content-Disposition'] = 'attachment; filename="Delmat Maker Master.xlsx"'
    logger.info("Test_Download Data:")
    # BytesIO.contents=response
    file = ContentFile(BytesIO.read())
    file.name = BytesIO.name
    Master_docs = Delmat()
    common_api = ApiService(scope)
    mod_obj = DocModule()
    doc_param = {"module": mod_obj.MASTER, "ref_type": Master_docs.REF_TYPE_VAL,
                 "ref_id": Master_docs.REF_TYPE_VAL_DELMAT}
    try:
        img_resp = common_api.upload_single_file(file, doc_param, request)
        doc_data = DelmatResponse()
        doc_data.id=img_resp.id
        doc_data.file_name=img_resp.file_name
        doc_data.file_gen_name=img_resp.gen_file_name
        doc_data.status=True
        # response = HttpResponse(img_resp.get(), content_type="application/json")
        resp = NWisefinSuccess()
        resp.set_status(SuccessStatus.SUCCESS)
        resp.set_message(SuccessMessage.CREATE_MESSAGE)
        response = HttpResponse(doc_data.get(), content_type="application/json")
        return response
    except:
        error_obj = NWisefinError()
        error_obj.status = False
        error_obj.set_code(ErrorMessage.INVALID_DATA)
        error_obj.set_description(ErrorDescription.INVALID_DATA)
        response = HttpResponse(error_obj.get(), content_type="application/json")
        return response


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def download_file(request, file_id):
    scope=request.scope
    common_service =ApiService(scope)
    emp_id = request.user.id
    emp_service = EmployeeService(scope)
    user_id = common_service.get_empsingle_id(request,emp_id)
    resp_obj = common_service.download_file(request, file_id, emp_id)
    return resp_obj



#dropdown
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_delmattype(request):
    scope = request.scope
    resp_obj = get_delmat_type_list()
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def pending_list(request):
    scope = request.scope
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    delmat_service = DelmatService(scope)
    emp_id = request.employee_id
    response_obj = delmat_service.fetch_DelmatPending_list(vys_page, emp_id, request)
    response = HttpResponse(response_obj.get(), content_type="application/json")
    return response

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def delmat_approval_download(request):
    scope = request.scope
    delmat_service = DelmatService(scope)
    user_id = request.user.id
    response_obj = delmat_service.fetch_delmat_approval_download(user_id, request)
    data = json.loads(json.dumps(response_obj.__dict__, default=dictdefault))['data']
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
    worksheet.write_string(2, 2, 'Delmat Approval Master Excel', header_format)
    writer.save()
    BytesIO.seek(0)
    BytesIO.size = BytesIO.__sizeof__()
    file = ContentFile(BytesIO.read())
    XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response = HttpResponse(file, content_type=XLSX_MIME)
    response['Content-Disposition'] = 'attachment; filename="Delmat Approval Master.xlsx"'
    logger.info("Test_Download Data:")
    return response


#dropdown
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_delmattype(request):
    scope = request.scope
    resp_obj = get_delmat_type_list()
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def listactive(request):
    scope = request.scope
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    delmat_service = DelmatService(scope)
    emp_id = request.employee_id
    response_obj = delmat_service.fetch_Delmat_listActive(vys_page, emp_id, request)
    response = HttpResponse(response_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def listinactive(request):
    scope = request.scope
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    delmat_service = DelmatService(scope)
    emp_id = request.employee_id
    response_obj = delmat_service.fetch_Delmat_listInActive(vys_page, emp_id, request)
    response = HttpResponse(response_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def updateapproved(request):
    scope = request.scope
    delmat_data = json.loads(request.body)
    delmat_service = DelmatService(scope)
    emp_id = request.employee_id
    # with transaction.atomic(using=DataBase.PRPO_DB):
    response_obj = delmat_service.status_UpdateApproved(delmat_data, emp_id)
    response = HttpResponse(response_obj.get(), content_type='application/json')
    return response


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def updaterejected(request):
    scope = request.scope
    delmat_data = json.loads(request.body)
    delmat_service = DelmatService(scope)
    emp_id = request.employee_id
    # with transaction.atomic(using=DataBase.PRPO_DB):
    response_obj = delmat_service.status_UpdateRejected(delmat_data, emp_id)
    response = HttpResponse(response_obj.get(), content_type='application/json')
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_delmat(request, delmat_id):
    if request.method == 'GET':
        scope = request.scope
        delmat_service = DelmatService(scope)
        emp_id = request.employee_id
        resp_obj = delmat_service.fetch_Delmat(delmat_id, emp_id, request)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_delmat(request, delmat_id)

def delete_delmat(request, delmat_id):
    scope = request.scope
    delmat_service = DelmatService(scope)
    emp_id = request.employee_id
    resp_obj = delmat_service.delete_Delmat(delmat_id,emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def delmatsearch(request):
    scope = request.scope
    delmat_obj = json.loads(request.body)
    delmat_service = DelmatService(scope)
    emp_id = request.employee_id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = delmat_service.search_DelmatAll(vys_page, delmat_obj, emp_id, request)
    return HttpResponse(resp_obj.get(), content_type='application/json')
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def delmatsearch_mst(request):
    scope = request.scope
    delmat_obj = json.loads(request.body)
    delmat_service = DelmatService(scope)
    emp_id = request.employee_id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = delmat_service.search_DelmatAll_mst(vys_page, delmat_obj, emp_id, request)
    return HttpResponse(resp_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def searchpending(request):
    scope = request.scope
    delmat_obj = json.loads(request.body)
    delmat_service = DelmatService(scope)
    emp_id = request.employee_id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = delmat_service.search_DelmatPendingAll(delmat_obj, emp_id, vys_page, request)
    return HttpResponse(resp_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def searchpending_mst(request):
    scope = request.scope
    delmat_obj = json.loads(request.body)
    delmat_service = DelmatService(scope)
    emp_id = request.employee_id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = delmat_service.search_DelmatPendingAll_mst(delmat_obj, emp_id, vys_page, request)
    return HttpResponse(resp_obj.get(), content_type='application/json')
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def updatestatus(request, delmat_id):
    scope = request.scope
    delmat_service = DelmatService(scope)
    emp_id = request.employee_id
    status =request.GET.get('status')
    # with transaction.atomic(using=DataBase.PRPO_DB):
    resp_obj = delmat_service.updatestatus(delmat_id, status, emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def search_employeelimit(request):
    scope = request.scope
    pr_service = DelmatService(scope)
    emp_id = request.employee_id
    commodityid = request.GET.get('commodityid')
    type = request.GET.get('type')
    employee = request.GET.get('employee')
    query = {"commodityid": commodityid, "type": type, "employee": employee}
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    print(query, emp_id, vys_page)
    response_obj = pr_service.search_employeelimit(query, emp_id, vys_page, request)
    response = HttpResponse(response_obj.get(), content_type='application/json')
    return response
# delmat_activate_inactivate
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def delmat_activate_inactivate(request):
    if request.method == 'POST':
        scope = request.scope
        fin_serv = DelmatService(scope)
        fin_obj = json.loads(request.body)
        finyr_obj = DelmatRequest(fin_obj)
        resp_obj = fin_serv.delmat_activate_inactivate(request,finyr_obj)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_delmat_mtom(request):
    if request.method == 'POST':
        scope = request.scope
        delmat_data = json.loads(request.body)
        delmat_service = DelmatService(scope)
        delmat_obj = DelmatRequest(delmat_data)
        emp_id = request.employee_id
        action = request.GET.get('action')
        response_obj = delmat_service.create_Delmat_mtom(delmat_obj,action, emp_id, request)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def delmatapprove_mtom(request):
    scope = request.scope
    delmat_data = json.loads(request.body)
    delmat_service = DelmatService(scope)
    emp_id = request.employee_id
    response_obj = delmat_service.delmatapprove_mtom(delmat_data, emp_id, request)
    response = HttpResponse(response_obj.get(), content_type='application/json')
    return response


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def delmatreject_mtom(request):
    scope = request.scope
    delmat_data = json.loads(request.body)
    delmat_service = DelmatService(scope)
    emp_id = request.employee_id
    response_obj = delmat_service.delmatreject_mtom(delmat_data, emp_id, request)
    response = HttpResponse(response_obj.get(), content_type='application/json')
    return response

# import base64
# import requests
# from nwisefin.settings import SERVER_IP
# from django.http import HttpResponse
# import json
#
# def get_authtoken_micro():
#     ip_address=SERVER_IP+'/usrserv/auth_token'
#     username = 'apuser'
#     password = b'vsolv123'
#     password = base64.b64encode(password)
#     password=password.decode("utf-8")
#     datas = json.dumps({"username": username, "password": password})
#     resp = requests.post(ip_address,  data=datas,verify=False)
#     token_data = json.loads(resp.content.decode("utf-8"))
#     ### Validations
#     if resp.status_code == 200:
#         return token_data["token"]
