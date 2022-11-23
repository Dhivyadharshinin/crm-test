import base64
import decimal
import logging
import traceback

import pandas as pd
import io
from datetime import datetime

from PIL import Image
from django.core.files.base import ContentFile
from django.db import transaction
from django.http import HttpResponse , StreamingHttpResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt

from docservice.service.documentservice import DocumentsService
from docservice.util.docutil import DocModule
from faservice.data.request.asset_details_request import Asset_Details_Request
from faservice.models import AssetDetails, AssetCapDate
from masterservice.data.request.codegenrequest import CodegenRequest
from faservice.data.request.assetdetailsrequest import AssetDetailsRequest, CheckerSummaryRequest, CapDateRequest, \
    FapvReq
from faservice.data.request.assetlocationrequest import AssetLocationRequest
from faservice.data.request.assetupdaterequest import AssetUpdateRequest
from faservice.data.response.assetdetailsresponse import AssetDetailsResponse
from faservice.service.assetdetailsservice import AssetDetailsService
from faservice.service.assetdetailupdateservice import AssetUpdateService
from faservice.service.assetlocationservice import AssetLocationService
#from masterservice.models import CodeGenHeader, CodeGenDetails
from faservice.util.FaApiService import FaApiService
from faservice.util.fautil import RequestStatus, RequestForUtil, dictdefault, AssetRequestfor, FaRefType
from masterservice.data.response.Hsnresponse import HsnResponse
from masterservice.data.response.apcategoryresponse import ApcategoryResponse
from masterservice.data.response.productresponse import ProductResponse
from masterservice.data.response.uomresponse import UomResponse
from masterservice.models import CodeGenDetails, CodeGenHeader, APsubcategory
from userservice.service.employeeservice import EmployeeService
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerror import NWisefinError as Error
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage,ErrorDescription
from utilityservice.data.response.nwisefinsuccess import SuccessMessage,NWisefinSuccess,SuccessStatus
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
import json
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.threadlocal import NWisefinThread


class Dbget(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.FA_SERVICE)
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_assetdetails(request):
    scope=request.scope
    db_get=Dbget(scope)
    emp_service = FaApiService(scope)
    assetdetails_serv = AssetDetailsService(scope)
    if request.method == 'POST':
        assetdetails_json = json.loads(request.data.get('data').replace("'",'"'))
        assetdetails_obj = AssetDetailsRequest(assetdetails_json)
        user_id = request.user.id
        emp_id = request.employee_id
        logger.info('FAL_CAPITALIZE:{}'.format(assetdetails_json))
        sav_point=transaction.savepoint(using=db_get._current_app_schema())
        resp_obj = assetdetails_serv.create_assetdetails(assetdetails_obj, emp_id,request,assetdetails_obj.assetgroup_id,assetdetails_obj.assetdetails_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")

        if isinstance(resp_obj,Error):
            transaction.savepoint_rollback(sav_point,using=db_get._current_app_schema())
            response = HttpResponse(resp_obj.get(), content_type="application/json")
            return response
        transaction.commit(using=db_get._current_app_schema())
        return response
    elif request.method == 'GET':
        return fetch_assetdetails_list(request)


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_businesssegment_list(request):
    scope=request.scope
    emp_service = FaApiService(scope)

    if request.method == 'GET':
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        bs_resp = emp_service.fetch_businesssegment_list(vys_page)
        # print(bs_resp.get())
        user_id = request.user.id
        # emp_id=request.employee_id
        response = HttpResponse(bs_resp, content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_costcentre_list(request):
    scope=request.scope
    emp_service = FaApiService(scope)

    if request.method == 'POST':
        from wisefinapi.masterapi import MasterAPI
        master_obj=MasterAPI()
        bs_resp = master_obj.get_cc_list(request)
        # print(bs_resp)
        user_id = request.user.id
        emp_id=request.employee_id
        response = HttpResponse(json.dumps(bs_resp), content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_branch_list(request):
    if request.method == 'GET':
        pass
        from wisefinapi.employeeapi import EmployeeAPI
        emp_obj=EmployeeAPI()
        branch_resp = emp_obj.fetch_branch_list(request)
        # print(branch_resp.text)
        user_id = request.user.id
        # emp_id=request.employee_id
        response = HttpResponse(branch_resp, content_type="application/json")
        return response
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_Apcat_list(request):
    scope=request.scope
    emp_service = FaApiService(scope)

    if request.method == 'GET':
        pass
        from wisefinapi.masterapi import MasterAPI
        master_obj=MasterAPI()
        bs_resp = master_obj.get_apcat_list(request)
        # print(bs_resp.text)
        user_id = request.user.id
        emp_id=request.employee_id
        response = HttpResponse(bs_resp, content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_Apsubcat_list(request):
    scope=request.scope
    emp_service = FaApiService(scope)

    if request.method == 'GET':
        pass
        from wisefinapi.masterapi import MasterAPI
        master_obj=MasterAPI()
        bs_resp = master_obj.get_apsubcat_list(request)
        # print(bs_resp)
        user_id = request.user.id
        emp_id=request.employee_id
        response = HttpResponse(bs_resp.text, content_type="application/json")
        return response
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_asset_id(request):
    if request.method == 'GET':
        scope=request.scope
        master_obj=AssetDetailsService(scope)
        page=request.GET.get('page',1)
        page = int(page)
        vys_page = NWisefinPage(page,30)
        query=request.GET.get('query','')
        bs_resp = master_obj.fetch_asset_id(query,vys_page)
        response = HttpResponse(bs_resp.get(), content_type="application/json")
        return response

def fetch_assetdetails_list(request):
    user_id = request.user.id
    scope=request.scope
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    query = request.GET.get('query', None)
    barcode = request.GET.get('barcode', None)
    assetdetails_serv = AssetDetailsService(scope)
    resp_obj = assetdetails_serv.get_all_assetdetails(vys_page,user_id, request)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_assetdetails_sum(request):
    scope=request.scope
    user_id = request.user.id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    query = request.GET.get('query', None)
    barcode = request.GET.get('barcode', None)
    assetdetails_serv = AssetDetailsService(scope)
    resp_obj = assetdetails_serv.fetch_assetdetails_sum(request, vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_assetchecker_summary(request):
    try:
        scope=request.scope
        user_id = request.user.id
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        query_obj=CheckerSummaryRequest(request)
        # barcode = request.GET.get('barcode', None)
        assetdetails_serv = AssetDetailsService(scope)
        resp_obj = assetdetails_serv.fetch_asset_checkersum(vys_page,query_obj,page,request)
        resp_obj_temp={"data":[i.__dict__ for i in resp_obj.data],
                  "pagination":resp_obj.pagination.__dict__}
        response = HttpResponse(json.dumps(resp_obj_temp,default=dictdefault))
    except Exception as e:
        traceback.print_exc()
        resp_obj_temp = {"data": [],
                         "pagination": {}}
        response = HttpResponse(json.dumps(resp_obj_temp, default=dictdefault))
    return response
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def checker_summary_approve(request):
    scope=request.scope
    user_id = request.user.id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    query_obj=CheckerSummaryRequest(request)
    # barcode = request.GET.get('barcode', None)
    # resp_obj = assetdetails_serv.fetch_asset_checkersum(vys_page,query_obj,request)
    assetdetails_serv = AssetDetailsService(scope)
    resp_obj = assetdetails_serv.checker_sum_approve(query_obj,request)
    resp_obj_temp={"data":[i.__dict__ for i in resp_obj.data],
              "pagination":resp_obj.pagination.__dict__}
    response = HttpResponse(json.dumps(resp_obj_temp,default=dictdefault))
    return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def codegenerator(request):
    scope=request.scope
    query_obj=CodegenRequest(request)
    assetdetails_serv = AssetDetailsService(scope)
    resp_obj = assetdetails_serv.fetch_codegenerator_list(query_obj)
    resp_obj_temp={"data":[i.__dict__ for i in resp_obj.data]}
    response = HttpResponse(json.dumps(resp_obj_temp,default=dictdefault))

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_assetid_grp(request):
    if request.method=="GET":
        scope=request.scope
        asset_grp_id=request.GET.get('assetgroup_id')
        page=request.GET.get('page',1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        assetdet_serv=AssetDetailsService(scope)
        response=assetdet_serv.fetch_asset_id_grp(vys_page,asset_grp_id)
        response=HttpResponse(json.dumps(response))
    return response


@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_assetchecker_view(request):
    scope=request.scope
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    checker_obj=CheckerSummaryRequest(request)
    assetdetails_serv = AssetDetailsService(scope)
    resp_obj = assetdetails_serv.fetch_asset_checkersum(vys_page, checker_obj, page,request)
    resp_obj_temp = {"data": [i.__dict__ for i in resp_obj.data],
                     "pagination": resp_obj.pagination.__dict__}
    response = HttpResponse(json.dumps(resp_obj_temp, default=dictdefault))
    return response

@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_assetchecker_non(request):
    scope=request.scope
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    checker_obj=CheckerSummaryRequest(request)
    assetdetails_serv = AssetDetailsService(scope)
    resp_obj = assetdetails_serv.fetch_asset_id_grp_non(vys_page, checker_obj,request)
    resp_obj_temp = {"data": [i.__dict__ for i in resp_obj.data],
                     "pagination": resp_obj.pagination.__dict__}
    response = HttpResponse(json.dumps(resp_obj_temp, default=dictdefault))
    return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_assetid_grp(request):
    if request.method=="GET":
        asset_grp_id=request.GET.get('assetgroup_id')
        page=request.GET.get('page',1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        scope=request.scope
        assetdet_serv=AssetDetailsService(scope)
        response=assetdet_serv.fetch_asset_id_grp(vys_page,asset_grp_id)
        response=HttpResponse(json.dumps(response,default=dictdefault))
    return response


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def faquery_get(request):

    data = json.loads(request.body)
    if 'asstsrc' in data:
        for src in data['asstsrc']:
            if src==None:
                ind=data['asstsrc'].index(src)
                data['asstsrc'].pop(ind)
    user_id = request.user.id
    scope=request.scope
    emp_service = FaApiService(scope)

    emp_id=request.employee_id
    page = request.GET.get('page', 1)
    type = request.GET.get('type',[])
    page = int(page)
    pagesize = request.GET.get('pagesize', 10)
    vys_page = NWisefinPage(page, int(pagesize))
    assetdetails_serv = AssetDetailsService(scope)
    if type=='count_flag':
        resp_obj = assetdetails_serv.get_countfa(data['value'])

    else:
        resp_obj = assetdetails_serv.fa_queryget(data, vys_page, emp_id, request)
    response = HttpResponse(json.dumps(resp_obj.__dict__,default=dictdefault), content_type="application/json")
    return response
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def faquery_get_download(request):

    data = json.loads(request.body)
    if 'asstsrc' in data:
        for src in data['asstsrc']:
            if src==None:
                ind=data['asstsrc'].index(src)
                data['asstsrc'].pop(ind)
    user_id = request.user.id
    scope=request.scope
    emp_service = FaApiService(scope)

    emp_id=request.employee_id
    page = request.GET.get('page', 1)
    type = request.GET.get('type',[])
    page = int(page)
    pagesize = request.GET.get('pagesize', 10)
    vys_page = NWisefinPage(page, int(pagesize))
    assetdetails_serv = AssetDetailsService(scope)
    if type=='count_flag':
        resp_obj = assetdetails_serv.get_countfa(data['value'])

    else:
        resp_obj = assetdetails_serv.fa_queryget_download(data, vys_page, emp_id, request)
        data=json.loads(json.dumps(resp_obj.__dict__, default=dictdefault))['data']
        df=pd.DataFrame(data)
        BytesIO=io.BytesIO()
        BytesIO.name = 'EXCEL-DOWNLOAD-(' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ').xlsx'
        writer = pd.ExcelWriter(BytesIO, engine='xlsxwriter')

        fields = {'barcode': 'Asset Barcode', 'assetdetails_id': 'Asset Transaction ID',
                  'assetdetails_status': 'Status', 'assetgroup_id': 'Asset Grp ID ',
                  'cat': 'Asset Category', 'subcat': 'Asset SubCategory', 'expense_gl': 'Expense GL ',
                  'product_id': 'Product Name', 'capdate': 'Capitalisation Date',
                  'assetdetails_value': 'Asset Value', 'ponum': 'PO Number ',
                  'invoice_id': 'Invoice No.', 'invoice_date': 'Invoice Date',
                  'vendorname': 'Vendor Name', 'branch_id': 'Branch Name ',
                  'enddate': 'Asset EndDate ', 'crnum': 'CR No.', 'valuetot': 'Asset Total Value',
                  'costtot': 'Asset Total Cost', 'source': 'Asset Source', 'requestfor': 'Requestfor'}
        order = ["Asset Barcode", "Asset Transaction ID", "Status", "Asset Grp ID ",
                 "Asset Category", "Asset SubCategory", "Expense GL ", "Product Name",
                 "Capitalisation Date", "Asset Value", "PO Number ", "Invoice No.",
                 "Invoice Date", "Vendor Name", "Branch Name ", "Asset EndDate ", "CR No.",
                 "Asset Total Value", "Asset Total Cost", "Asset Source", "Requestfor"]
        df=df.rename(columns=fields)
        df = df[order]
        df.to_excel(writer, sheet_name='Sheet1', index=False, startcol=0, startrow=5)
        worksheet = writer.sheets['Sheet1']
        workbook=writer.book
        header_format = workbook.add_format()
        header_format.set_align('center')
        header_format.set_bold()
        worksheet.write_string(2, 2,'FA QUERY excel',header_format)
        writer.save()
        BytesIO.seek(0)
        BytesIO.size = BytesIO.__sizeof__()
        file = ContentFile(BytesIO.read())
        XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response = HttpResponse(file, content_type=XLSX_MIME)
        response['Content-Disposition'] = 'attachment; filename="EXCEL_report.xlsx"'
        logger.info("Test_Download Data:")
        return response
    return resp_obj

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def faquery_version(request):
    if request.method == "GET":
        version = {"data": "BV-3.24"}
        # print('hello', version)
        empbranch_dic = json.dumps(version, indent=5)
        response = HttpResponse(empbranch_dic, content_type="application/json")
        return response
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def faquery_source_get(request):
    if request.method == "GET":
        scope=request.scope
        assetdetails_serv = AssetDetailsService(scope)
        data=assetdetails_serv.get_source()
        response = HttpResponse(data, content_type="application/json")
        return response


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def Assetclubget(request):
    data = json.loads(request.body)
    scope=request.scope
    user_id = request.user.id
    emp_service = FaApiService(scope)

    emp_id=request.employee_id
    page = request.GET.get('page', 1)
    # type = request.GET.get('type',[])
    page = int(page)
    pagesize = request.GET.get('pagesize', 10)
    vys_page = NWisefinPage(page, int(pagesize))
    assetdetails_serv = AssetDetailsService(scope)
    resp_obj = assetdetails_serv.getclubsummary(data, vys_page, emp_id, request)

    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def getparentchild(request,parentid):
    # data = json.loads(request.body)
    user_id = request.user.id
    scope=request.scope
    emp_service = FaApiService(scope)

    user_id = emp_service.get_empid_from_userid(user_id)
    page = request.GET.get('page', 1)
    # type = request.GET.get('type',[])
    page = int(page)
    pagesize = request.GET.get('pagesize', 10)
    vys_page = NWisefinPage(page, int(pagesize))
    assetdetails_serv = AssetDetailsService(scope)
    resp_obj = assetdetails_serv.parentdetail_get(parentid, vys_page,user_id,request)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def clumbmakerparentchildget(request):
    data = json.loads ( request.body )
    user_id = request.user.id
    scope=request.scope
    emp_service = FaApiService(scope)

    emp_id=request.employee_id
    page = request.GET.get('page', 1)
    type = request.GET.get('type','')
    page = int(page)
    pagesize = request.GET.get('pagesize', 10)
    vys_page = NWisefinPage(page, int(pagesize))
    assetdetails_serv = AssetDetailsService(scope)
    if type=='Approve':
        resp_obj = assetdetails_serv.get_clubapproverqueue ( emp_id , RequestStatus.PENDING , vys_page ,data ,request )
    elif type=='Child':
        resp_obj = assetdetails_serv.getparentasset ( user_id , 'Child' , vys_page , data , request )
    else:
        resp_obj = assetdetails_serv.getparentasset( user_id,'',vys_page,data,request )
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])

def clubmakerupdate(request):
    data = json.loads(request.body)
    scope=request.scope
    user_id = request.user.id
    emp_service = FaApiService(scope)

    user_id = emp_service.get_empid_from_userid(user_id)
    type = request.GET.get('type')
    assetdetails_serv = AssetDetailsService(scope)
    if type== 'moveto_checker' :
        resp_obj = assetdetails_serv.clubmakerupdate(data,user_id,AssetRequestfor.CLUB,RequestStatus.PENDING)
    if type=='Approve':
        resp_obj = assetdetails_serv.clubmakerupdate ( data , user_id , AssetRequestfor.CLUB , RequestStatus.APPROVED )
    if type =='Reject':
        resp_obj = assetdetails_serv.clubmakerupdate ( data , user_id , RequestForUtil.CLUB , RequestStatus.REJECTED )
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response



@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def checker_summary_approve(request):
    scope=request.scope
    # user_id = request.user.id
    user_id = request.user.id
    asset_list=json.loads(request.body)
    logger.info('FAL_CHECKER_APPROVE_DATA:{}'.format(asset_list))
    resp=checker_check(asset_list['assetdetails_id'],request)
    assetdetails_serv = AssetDetailsService(scope)
    if isinstance(resp,Error):
        return HttpResponse(resp.get(),content_type='application/json')
    resp_obj = assetdetails_serv.checker_sum_approve(user_id,asset_list,request)
    if isinstance(resp_obj,Error):
        response = HttpResponse(resp_obj.get(),content_type="application/json")
        return response
    response = HttpResponse(json.dumps(resp_obj,default=dictdefault))
    return response
def checker_check(asset_data,request):
    user_id=request.user.id
    scope=request.scope
    fa_obj=FaApiService(scope)
    emp_id=request.employee_id
    for data in asset_data:
        asst_data=AssetDetails.objects.get(id=data)
        if asst_data.created_by==emp_id:
            err=Error()
            err.set_code(ErrorMessage.MAKER_CANNOT_APPROVE)
            err.set_description(ErrorDescription.MAKER_CANNOT_APPROVE)
            return err
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def checker_summary_reject(request):
    scope=request.scope
    checker_request=CheckerSummaryRequest(request)
    assetdetails_serv = AssetDetailsService(scope)
    checker_response=assetdetails_serv.checker_sum_reject(checker_request,request)
    response=HttpResponse(checker_response.get(),content_type='application/json')
    return response

# PV--Anand
#assetdetails_capitalize
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def assetdetails(request):
    scope=request.scope
    # asset_serv = Asset_Details_Service(scope)
    assetdetails_serv = AssetDetailsService(scope)
    if request.method == "POST":
        try:
            logging.error("FA_ASSET_CAP_DATA: "+str(request.data))
            form_json = json.loads(request.data.get('data'))
            user_id = request.user.id
            response_obj=Asset_Details_Request(form_json)

            assetdetails_resp=assetdetails_serv.create_asset_details(response_obj)
            response = HttpResponse(assetdetails_resp.get(), content_type='application/json')
            return response
        except:
            traceback.print_exc()
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 30)
    user_id = request.user.id
    emp_service = FaApiService(scope)

    user_id = emp_service.get_empid_from_userid(user_id)
    if request.method == "POST":
        form_json = json.loads(request.body)
        # user_id = request.user.id
        logger.info('FAL_ASSETDETAILS_DATA:{}'.format(form_json))

        response_obj=Asset_Details_Request(form_json)
        assetdetails_resp=assetdetails_serv.create_asset_details(vys_page,response_obj,user_id ,request)
        response = HttpResponse(assetdetails_resp.get(), content_type='application/json')
        return response
    elif request.method == "GET":
        return overallget_assetdetails(request,user_id)
# @csrf_exempt
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
def overallget_assetdetails(request,user_id):
    # asset_serv = Asset_Details_Service(scope)
    # user_id = request.user.id

    # print(asset_serv)
    scope=request.scope
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    assetdetails_serv = AssetDetailsService(scope)
    assetmaster_resp = assetdetails_serv.get_all_assetdetails(vys_page,request,user_id)
    response = HttpResponse(assetmaster_resp.get(), content_type='application/json')
    return response


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def filter_records(request):
    scope=request.scope
    if request.method == "GET":
        user_id = request.user.id
        fa_obj = FaApiService(scope)
        emp_service = FaApiService(scope)

        user_id = request.employee_id
        branch_id=None
        try:
            branch_id=fa_obj.get_emp_branch(user_id, request).id
        except:
            err=Error()
            err.set_code(ErrorMessage.INVALID_branch_ID)
            err.set_description(ErrorDescription.INVALID_branch_ID)
            resp=HttpResponse(err.get(),content_type='application/json')
            return resp
        page = int(request.GET.get('page', 1))
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        assetdetails_serv = AssetDetailsService(scope)
        try:
            assetdetails_resp = assetdetails_serv.get_asset_update_records(branch_id,user_id,request,vys_page)
        except Exception as e:
            error_obj = Error()
            error_obj.set_code('Header ID Not Matched')
            error_obj.set_description(e)
            resp = HttpResponse(error_obj.get(), content_type='application/json')
            return resp
        return HttpResponse(assetdetails_resp.get(), content_type='application/json')


@csrf_exempt
@api_view(['GET', 'POST'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
def asset_edit_records(request):
    if request.method == "GET":
        user_id = request.user.id
        scope=request.scope
        fa_obj = FaApiService(scope)
        # user_id = emp_service.get_empid_from_userid(user_id)
        page = int(request.GET.get('page', 1))
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        assetdetails_serv = AssetDetailsService(scope)
        try:
            assetdetails_resp = assetdetails_serv.get_asset_update_edit_records(request,vys_page)
        except Exception as e:
            error_obj = Error()
            error_obj.set_code('Not Available')
            error_obj.set_description(e)
            resp = HttpResponse(error_obj.get(), content_type='application/json')
            return resp
        return HttpResponse(assetdetails_resp.get(), content_type='application/json')


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def cpdatechange_makersummary(request):
    user_id = request.user.id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    scope=request.scope
    assetdetails_serv = AssetDetailsService(scope)
    assetmaster_resp = assetdetails_serv.cpdate_makersum(vys_page,request,user_id)
    response = HttpResponse(assetmaster_resp, content_type='application/json')
    return response
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def cpdatechange_summary(request):
    user_id = request.user.id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    scope=request.scope
    assetdetails_serv = AssetDetailsService(scope)

    assetmaster_resp = assetdetails_serv.cpdate_sum(vys_page,request,user_id)
    response = HttpResponse(assetmaster_resp, content_type='application/json')
    return response
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def cpdatechange_checksummary(request):
    user_id = request.user.id
    page = request.GET.get('page', 1)
    asset_query=request.GET.get('asset_id')
    page = int(page)
    scope=request.scope
    vys_page = NWisefinPage(page, 10)
    assetdetails_serv = AssetDetailsService(scope)
    assetmaster_resp = assetdetails_serv.cpdate_checksum(vys_page,request,asset_query,user_id)
    response = HttpResponse(assetmaster_resp, content_type='application/json')
    return response
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def cpdatechange_make(request):
    user_id = request.user.id
    capdate_obj=CapDateRequest(json.loads(request.body))
    logger.info('FAL_ASSETCAPMAKE_DATA:{}'.format(capdate_obj))
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    scope=request.scope
    assetdetails_serv = AssetDetailsService(scope)
    assetmaster_resp = assetdetails_serv.cpdate_make(capdate_obj,request,user_id)
    response = HttpResponse(assetmaster_resp.get(), content_type='application/json')
    return response
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def cpdatechange_check(request):
    user_id = request.user.id
    capdate_obj=CapDateRequest(json.loads(request.body  ))
    valid=cap_valid(capdate_obj.capdate_id,user_id)
    if isinstance(valid,Error):
        return HttpResponse(valid.get(), content_type='application/json')
    logger.info('FAL_ASSETCATCHECK_DATA:{}'.format(capdate_obj))
    scope=request.scope
    assetdetails_serv = AssetDetailsService(scope)
    assetmaster_resp = assetdetails_serv.cpdate_check(capdate_obj,request,user_id)
    response = HttpResponse(assetmaster_resp.get(), content_type='application/json')
    return response
def cap_valid(asst_id_list,user_id):
    for data in asst_id_list:
        asst_data=AssetCapDate.objects.get(id=data)
        if asst_data.created_by == user_id:
            err=Error()
            err.set_code(ErrorMessage.MAKER_CANNOT_APPROVE)
            err.set_description(ErrorDescription.INVALID_APPROVER_ID)
            return err
    return True


@csrf_exempt
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def parentchildvalidation(request):
    if request.method == "POST":
        scope=request.scope
        form_json = json.loads(request.body)

        user_id = request.user.id
        # print(form_json)
        assetdetails_serv = AssetDetailsService(scope)
        assetdetails_resp = assetdetails_serv.parentchildvalidation ( form_json['barcode'] )
        return HttpResponse ( assetdetails_resp.get ( ) , content_type='application/json' )

@csrf_exempt
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def asset_emp_map(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        scope = request.scope
        assetdetails_serv = AssetDetailsService(scope)
        obj = FapvReq(data)
        emp_id = request.employee_id
        response_obj = assetdetails_serv.create_asset_map(obj, emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response

    if request.method == 'GET':
        scope = request.scope
        assetdetails_serv = AssetDetailsService(scope)
        page = int(request.GET.get('page', 1))
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        barcode = request.GET.get('query')
        emp_id = request.user.id
        emp = request.GET.get('emp')
        emp_id = request.employee_id
        response_obj = assetdetails_serv.fetch_emp_map(vys_page,barcode,emp,emp_id,request)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def asset_map_activate_inactivate(request):
    if request.method == 'POST':
        scope = request.scope
        assetdetails_serv = AssetDetailsService(scope)
        data = json.loads(request.body)
        obj = FapvReq(data)
        resp_obj = assetdetails_serv.asset_barcode_map_activate_inactivate(request,obj)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
