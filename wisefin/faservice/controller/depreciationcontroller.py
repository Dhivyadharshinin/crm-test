import io
from datetime import datetime

import pandas
import pandas as pd
from django.core.files.base import ContentFile
from django.http import HttpResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from faservice.data.request.depreciationrequest import DepreciationRequest
from faservice.service.depreciationservice  import DepreciationService
from userservice.service.employeeservice import EmployeeService
from nwisefin.settings import logger
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
import json
from django.db.models import Q
from utilityservice.data.response.nwisefinpage import NWisefinPage
from faservice.util.fautil_valid import date_validation
from utilityservice.data.response.nwisefinerror import NWisefinError as Error
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription,ErrorMessage
from faservice.util.fautil import Fa_Doctype, dictdefault
from django.db import transaction
from faservice.util.FaApiService import FaApiService
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def createdepreciation(request):
    if request.method == 'POST':
        scope=request.scope
        emp_service = FaApiService(scope)
        depreciation_serv = DepreciationService(scope)
        depreciation_obj = json.loads(request.body)
        logger.info('FAL_ASSET_DEPRECIATION_DATA:{}'.format(depreciation_obj))
        user_id = request.user.id
        emp_id = request.employee_id
        #emp_id=user_id
        dep_obj = DepreciationRequest(depreciation_obj)
        #Date Validation
        from_date = dep_obj.get_from_date()
        to_date = dep_obj.get_to_date()
        deptype = dep_obj.get_deptype()
        val = date_validation(from_date,to_date)
        if val == True:
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INCORRECT_DATE_GIVEN)
            error_obj.set_description(ErrorDescription.INVALID_DATE_CHK)
            response = HttpResponse(error_obj.get(), content_type="application/json")
            return response
        REGULAR=Fa_Doctype.REG
        FORECASTING=Fa_Doctype.FORE
        if int(FORECASTING) == int(deptype):
            #print('FORECASTING')
            resp_obj = depreciation_serv.create_depreciation(dep_obj, emp_id)
            response = HttpResponse(resp_obj.get(), content_type="application/json")
        else:
            #print('REGULAR')
            resp_obj = depreciation_serv.create_depreciationreg(dep_obj, emp_id)
            response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == "GET":
        return get_depreciation(request)

def get_depreciation(request):
    scope = request.scope
    depreciation_serv = DepreciationService(scope)
    user_id = request.user.id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    assetdep_resp = depreciation_serv.depreciation_summary(vys_page,user_id,request)
    response = HttpResponse(assetdep_resp.get(), content_type='application/json')
    return response

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fa_migration_data(request):
    scope = request.scope
    if request.method == 'POST':
        schema_obj = json.loads(request.body)
        post_name=schema_obj['Post_Schema']
        get_name=schema_obj['Get_Schema']
        #print(post_name,get_name)
        depreciation_serv = DepreciationService(scope)
        user_id = request.user.id
        assetdep_resp = depreciation_serv.fa_migration(user_id,post_name,get_name)
        response = HttpResponse(assetdep_resp.get(), content_type='application/json')
        return response


# def fa_depreciationsingel(request):
#         depreciation_serv = DepreciationService(scope)
#         emp_id=1
#         depsingel_obj={"from_date":"2021-04-01","to_date":"2022-03-31",
#                        "deptyp":1,"assetdetails_id":25,"assetdetails_source":"1"}
#         print(depsingel_obj)
#         assetdep_resp = depreciation_serv.create_singledepreciation(depsingel_obj,emp_id)
#         response = HttpResponse(assetdep_resp.get(), content_type='application/json')
#         return response

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def itdepreciation(request):
    if request.method == 'POST':
        scope=request.scope
        emp_service = FaApiService(scope)
        depreciation_serv = DepreciationService(scope)
        depreciation_obj = json.loads(request.body)
        logger.info('FAL_ASSET_DEPRECIATION_DATA:{}'.format(depreciation_obj))
        user_id = request.user.id
        emp_id = request.employee_id
        dep_obj = DepreciationRequest(depreciation_obj)
        from_date = dep_obj.get_from_date()
        to_date = dep_obj.get_to_date()
        resp_obj = depreciation_serv.create_itdepreciation(from_date,to_date,emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == "GET":
        return get_itdepreciation(request)


def get_itdepreciation(request):
    scope = request.scope
    depreciation_serv = DepreciationService(scope)
    user_id = request.user.id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    itdep_resp = depreciation_serv.itdepreciation_summary(vys_page, user_id, request)
    data = json.loads(json.dumps(itdep_resp.__dict__, default=dictdefault))['data']
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
    worksheet.write_string(2, 2, 'IT Depreciation excel', header_format)
    writer.save()
    BytesIO.seek(0)
    BytesIO.size = BytesIO.__sizeof__()
    file = ContentFile(BytesIO.read())
    XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response = HttpResponse(file, content_type=XLSX_MIME)
    response['Content-Disposition'] = 'attachment; filename="IT Depreciation.xlsx"'
    logger.info("Test_Download Data:")
    return response


