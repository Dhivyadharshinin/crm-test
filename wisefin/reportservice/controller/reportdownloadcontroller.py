import json
import mimetypes
import os
from io import BytesIO
from pathlib import Path

from django.http import HttpResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
import boto3
from django.http import HttpResponse, StreamingHttpResponse
import pandas as pd
import json
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from docservice.service.documentservice import DocumentsService
from docservice.util.docutil import DocModule
from nwisefin import settings
from nwisefin.settings import logger
from reportservice.service.reportdownloadservice import ReportDownloadService
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_parameterlist(request):
    if request.method == 'POST':
        scope = request.scope
        report_service = ReportDownloadService(scope)
        # user_id = request.employee
        param_details = json.loads(request.body)
        module_id = param_details['module_id']
        report_id = param_details['report_id']
        emp_id = request.employee_id
        emp_name = param_details['report_name']
        resp_obj = report_service.fetch_parameterlist(module_id,report_id,emp_id)
        query = json.dumps(resp_obj, indent=6)
        return HttpResponse(query, content_type='application/json')
        # response = HttpResponse(resp_obj.get(), content_type="application/json")
        # return response


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_reportdownload(request):
    if request.method == 'POST':
        scope = request.scope
        report_service = ReportDownloadService(scope)
        # user_id = request.employee
        param_details = json.loads(request.body)
        report_id = param_details['report_id']
        emp_id = 1
        resp_obj = report_service.report_download(report_id,emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_reportdownload(request):
        scope = request.scope
        report_service = ReportDownloadService(scope)
        # user_id = request.employee
        resp=[]
        param_details = json.loads(request.body)
        emp_id = request.employee_id
        resp_obj = report_service.generate_report_download(param_details,emp_id,scope)
        XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response = HttpResponse(resp_obj, content_type=XLSX_MIME)
        logger.info("Test_Download Data:")
        response['Content-Disposition'] = 'attachment; filename="EXCEL_report.xlsx"'
        return response
        # response = StreamingHttpResponse(resp_obj, content_type='application/octet-stream')
        # return HttpResponse(response)
        # response = HttpResponse(resp_obj.get(), content_type="application/json")
        # return response


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_downloadlist(request):
    if request.method == 'GET':
        scope = request.scope
        report_service = ReportDownloadService(scope)
        # user_id = request.employee
        # param_details = json.loads(request.body)
        # id = request.GET.get('id')
        # emp_id = 1
        resp_obj = report_service.fetch_downloadlist()
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def downloadreport(request,id):
    try:
        if request.method == 'GET':
            logger.info("Test_Download Start:")
            scope = request.scope
            user_id = 1
            doc_serv = DocumentsService(scope)
            resp = doc_serv.doc_download(id,user_id)
            # BASE_DIR = Path(__file__).resolve().parent.parent
            # dirname = os.path.dirname(BASE_DIR)
            # response = dirname +'\\media\\REPORT_16_demo.xlsx'
            response = StreamingHttpResponse(resp, content_type='application/octet-stream')
            return HttpResponse(response)
    except Exception as e:
            logger.info("Test_Download exception data :" + str(e))


# @csrf_exempt
# @api_view(['GET', 'POST'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def downloadreport(request,id):
#     try:
#         if request.method == 'GET':
#             logger.info("Test_Download Start:")
#             scope = request.scope
#             from django.core.files.storage import default_storage
#             print(os.path.curdir)
#             file_list=os.listdir(settings.MEDIA_ROOT)
#             file_name=os.listdir(settings.MEDIA_ROOT)[0]
#             file = default_storage.open(file_name)
#             file_url = default_storage.url(file_name)
#             XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
#             response = HttpResponse(file, content_type=XLSX_MIME)
#             response['Content-Disposition'] = 'attachment; filename="EXCEL_report.xlsx"'
#             logger.info("Test_Download Data:")
#             return response
#     except Exception as e:
#         logger.info("Test_Download exception data :" + str(e))

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_vendor(request,vendor_id):
    if request.method == 'GET':
        scope = request.scope
        report_service = ReportDownloadService(scope)
        # user_id = request.employee
        # param_details = json.loads(request.body)
        # id = request.GET.get('id')
        # emp_id = 1
        resp_obj = report_service.fetch_vendor(vendor_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response