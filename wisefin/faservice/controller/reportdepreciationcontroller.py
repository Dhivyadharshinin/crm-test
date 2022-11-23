import os
import traceback
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
from faservice.service.reportdepreciationservice import ReportDepreciationService
from faservice.util.fautil import FaRefType
from docservice.models.docmodels import FADocs
from nwisefin import settings
from nwisefin.settings import logger
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from utilityservice.service.threadlocal import NWisefinThread


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def reportdepreciation(request):
    if request.method == "GET":
        scope = request.scope
        logger.info("Depreciation_Excel Start:")
        import io
        from django.core.files.base import ContentFile
        BytesIO = io.BytesIO()
        user_id = request.user.id
        team_serv = ReportDepreciationService(scope)
        collection = team_serv.report_depreciation_fin(user_id, request)
        df = pd.DataFrame(collection)
        df['Asset_Create_Date'] = df['Asset_Create_Date'].dt.strftime('%Y-%m-%d::%H-%M')
        df['End_Date'] = df['End_Date'].dt.strftime('%Y-%m-%d::%H-%M')
        BytesIO.name = 'EXCEL-DOWNLOAD-(' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ').xlsx'
        writer = pd.ExcelWriter(BytesIO, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Sheet1', index=True, startcol=0, startrow=5)
        worksheet = writer.sheets['Sheet1']
        worksheet.write_string(2, 2, '\033' + 'Forecast excel' + '\033')
        writer.save()
        BytesIO.seek(0)
        # from django.core.files.storage import default_storage
        # file_name = default_storage.save(BytesIO.name, BytesIO)
        # BytesIO.seek(0)
        BytesIO.size = BytesIO.__sizeof__()
        resp = []
        fa_docs = FaRefType()
        mod_obj = DocModule()
        doc_param = {"module": mod_obj.FA, "ref_type": fa_docs.DEPRECIATION_SETTING,
                     "ref_id": 10}
        # print(doc_param)
        doc_obj = DocumentsService(scope)
        file=ContentFile(BytesIO.read())
        file.name=BytesIO.name
        img_resp = doc_obj.upload_single_doc(file, doc_param)
        # img_resp={"file_status":"SUCCESS"}
        resp.append(img_resp)
        response = StreamingHttpResponse(resp, content_type='application/octet-stream')
        logger.info("Depreciation_Excel Data:")
        return HttpResponse(response)


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def tempreportdepreciation(request):
    try:

        if request.method == "GET":
            gen_file_name = "FA_211224_063145EXCEL-DOWNLOAD-(2021-12-24_06-29-12).xlsx"
            logger.info("Test_Download Start:")
            s3 = boto3.resource('s3', aws_access_key_id='AKIAWA5L3SZ42JOYR5UT',
                                aws_secret_access_key='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')
            s3_obj = s3.Object(bucket_name='memo-project-assets-uat', key=gen_file_name)
            body = s3_obj.get()['Body']
            logger.info("Test_Download Body:" + str(body))
            XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            response = HttpResponse(body, content_type=XLSX_MIME)
            logger.info("Test_Download Data:")
            response['Content-Disposition'] = 'attachment; filename="EXCEL_report.xlsx"'
            return response

    except Exception as e:
        logger.info("Test_Download exception data :" + str(e))


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def downloadforecast(request):
    try:
        if request.method == 'GET':
            logger.info("Test_Download Start:")
            # file = request.id
            class DBGet(NWisefinThread):
                def __init__(self,scope):
                    super().__init__(scope)
                    self._set_namespace(ApplicationNamespace.DCO_SERVICE)
            db_obj=DBGet(request.scope)
            file = FADocs.objects.using(db_obj._current_app_schema()).latest('id')
            # print(file.id)
            user_id = request.user.id
            scope = request.scope
            doc_obj = DocumentsService(scope)
            doc_param = 'FA_' + str(file.id)
            file_id = doc_obj.file_download(doc_param, user_id)
            XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            response = HttpResponse(file_id, content_type=XLSX_MIME)
            response['Content-Disposition'] = 'attachment; filename="EXCEL_report.xlsx"'
            logger.info("Test_Download Data:")
            return response
    except Exception as e:
        traceback.print_exc()
        logger.info("Test_Download exception data :" + str(e))


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def reportdepreciationregular(request):
    if request.method == "GET":
        logger.info("Depreciation_Excel Start:")
        import io
        BytesIO = io.BytesIO()
        user_id = request.user.id
        scope = request.scope
        team_serv = ReportDepreciationService(scope)
        collection = team_serv.report_depreciation_regular(user_id, request)
        df = pd.DataFrame(collection)
        df['Asset_Create_Date'] = df['Asset_Create_Date'].dt.strftime('%Y-%m-%d::%H-%M')
        df['End_Date'] = df['End_Date'].dt.strftime('%Y-%m-%d::%H-%M')
        BytesIO.name = 'EXCEL-DOWNLOAD-(' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ').xlsx'
        writer = pd.ExcelWriter(BytesIO, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Sheet1', index=True, startcol=0, startrow=5)
        worksheet = writer.sheets['Sheet1']
        worksheet.write_string(2, 2, '\033' + 'Regular excel' + '\033')
        writer.save()
        BytesIO.seek(0)
        BytesIO.size = BytesIO.__sizeof__()
        resp = []
        fa_docs = FaRefType()
        mod_obj = DocModule()
        logger.info("Depreciation_Excel Data:")
        XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response = HttpResponse(BytesIO, content_type=XLSX_MIME)
        logger.info("Test_Download Data:")
        response['Content-Disposition'] = 'attachment; filename="EXCEL_report.xlsx"'
        return response


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def downloadregular(request):
    try:
        if request.method == 'GET':
            logger.info("Test_Download Start:")
            file = FADocs.objects.latest('id')
            # print(file.id)
            user_id = request.user.id
            scope = request.scope
            doc_obj = DocumentsService(scope)
            doc_param = 'FA_' + str(file.id)
            file_id = doc_obj.download(doc_param, user_id)
            XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            response = HttpResponse(file_id, content_type=XLSX_MIME)
            response['Content-Disposition'] = 'attachment; filename="EXCEL_report.xlsx"'
            logger.info("Test_Download Data:")
            return response
    except Exception as e:
        logger.info("Test_Download exception data :" + str(e))


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def tempreportdepreciationregular(request):
    try:

        if request.method == "GET":
            gen_file_name = "FA_211228_080657EXCEL-DOWNLOAD-(2021-12-28_08-04-19).xlsx'"
            logger.info("Test_Download Start:")
            s3 = boto3.resource('s3', aws_access_key_id='AKIAWA5L3SZ42JOYR5UT',
                                aws_secret_access_key='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')
            s3_obj = s3.Object(bucket_name='memo-project-assets-uat', key=gen_file_name)
            body = s3_obj.get()['Body']
            logger.info("Test_Download Body:" + str(body))
            XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            response = HttpResponse(body, content_type=XLSX_MIME)
            logger.info("Test_Download Data:")
            response['Content-Disposition'] = 'attachment; filename="EXCEL_report.xlsx"'
            return response

    except Exception as e:
        logger.info("Test_Download exception data :" + str(e))


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def reportdepreciationfar(request):
    if request.method == "GET":
        logger.info("Depreciation_Excel Start:")
        import io
        BytesIO = io.BytesIO()
        user_id = request.user.id
        scope = request.scope
        team_serv = ReportDepreciationService(scope)
        collection = team_serv.report_depreciation_far(user_id, request, scope)
        df = pd.DataFrame(collection)
        if df.empty:
            df=df
        else:
            df['Cap_Date'] = pd.to_datetime(df['Cap_Date'], errors='coerce')
            df['Cap_Date'] = df['Cap_Date'].dt.strftime('%Y-%m-%d')
            df['End_Date'] = pd.to_datetime(df['End_Date'], errors='coerce')
            df['End_Date'] = df['End_Date'].dt.strftime('%Y-%m-%d')
        # df['Cap_Date'] = df['Cap_Date'].dt.strftime('%Y-%m-%d')
        # Cap_Date = datetime.now()
        # df['Cap_Date'] = Cap_Date.strftime('%Y-%m-%d::%H-%M-%S')
        # End_Date = datetime.now()
        # df['End_Date'] = End_Date.strftime('%Y-%m-%d::%H-%M-%S')
        # df['End_Date'] = df['End_Date'].dt.strftime('%Y-%m-%d')
        BytesIO.name = 'EXCEL-DOWNLOAD-(' + datetime.today().strftime("%Y-%m-%d") + ').xlsx'
        writer = pd.ExcelWriter(BytesIO, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Sheet1', index=True, startcol=0, startrow=5)
        worksheet = writer.sheets['Sheet1']
        worksheet.write_string(2, 2, '\033' + 'Depreciation FAR' + '\033')
        writer.save()
        BytesIO.seek(0)
        BytesIO.size = BytesIO.__sizeof__()
        resp = []
        # fa_docs = FaRefType()
        # mod_obj = DocModule()
        # doc_param = {"module": mod_obj.FA, "ref_type": fa_docs.DEPRECIATION_SETTING,
        #              "ref_id": 10}
        # # print(doc_param)
        # doc_obj = DocumentsService(scope)
        # img_resp = doc_obj.upload_single_doc(BytesIO, doc_param)
        # resp.append(json.loads(img_resp))
        response = StreamingHttpResponse(BytesIO, content_type='application/octet-stream')
        logger.info("Depreciation_Excel Data:")
        return HttpResponse(response)
