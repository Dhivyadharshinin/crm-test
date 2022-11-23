import io
import json
from datetime import datetime

import pandas as pd
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from faservice.util.fautil import dictdefault
from masterservice.data.request.ccbsmappingrequest import CcbsMappingRequest
from masterservice.service.ccbsmappingservice import CcbsMappingService
from nwisefin.settings import logger
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
# from userservice.service.ccbsservice import CostCentreService , BusinessSegmentService
from utilityservice.data.response.nwisefinpage import NWisefinPage

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ccbsmapping(request):
    if request.method == 'POST':
        scope = request.scope
        emp_id = request.employee_id
        ccbsmapping_service = CcbsMappingService(scope)
        ccbsmapping_data = json.loads(request.body)
        # user_id = request.employee_id
        ccbsmapping_obj = CcbsMappingRequest(ccbsmapping_data)
        resp_obj = ccbsmapping_service.create_ccbsmapping(ccbsmapping_obj, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_ccbsmapping_list(request)

def fetch_ccbsmapping_list(request):
    scope = request.scope
    ccbsmapping_service = CcbsMappingService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    user_id = request.employee_id
    resp_obj = ccbsmapping_service.fetch_ccbsmapping_list(vys_page)
    #
    # cc_service = CostCentreService()
    # bs_service = BusinessSegmentService()
    # x = resp_obj.data
    # for i in x:
    #     costcentre_id = i.costcentre_id
    #     businesssegment_id =i.businesssegment_id
    #     if costcentre_id is not None :
    #         costcentre = cc_service.fetch_costcentre(costcentre_id)
    #         i.costcentre = costcentre
    #     if businesssegment_id is not None :
    #         businesssegment = bs_service.fetch_businesssegment(businesssegment_id)
    #         i.businesssegment = businesssegment

    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

# def fetch_ccbsmapping_list(request):
#     ccbsmapping_service = CcbsMappingService()
#     page = request.GET.get('page', 1)
#     page = int(page)
#     vys_page = NWisefinPage(page, 10)
#     user_id = request.employee_id
#     resp_obj = ccbsmapping_service.fetch_ccbsmapping_list(vys_page)
#
#     cc_service = CostCentreService()
#     bs_service = BusinessSegmentService()
#     x = resp_obj.data
#     for i in x:
#         costcentre_id = i.costcentre_id
#         businesssegment_id =i.businesssegment_id
#         if costcentre_id is not None :
#             costcentre = cc_service.fetch_costcentre(costcentre_id)
#             i.costcentre = costcentre
#         if businesssegment_id is not None :
#             businesssegment = bs_service.fetch_businesssegment(businesssegment_id)
#             i.businesssegment = businesssegment
#
#     response = HttpResponse(resp_obj.get(), content_type="application/json")
#     return response

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ccbsmapping_download(request):
    scope = request.scope
    ccbsmapping_service = CcbsMappingService(scope)
    user_id = request.user.id
    resp_obj = ccbsmapping_service.fetch_ccbsmapping_download(user_id)
    data = json.loads(json.dumps(resp_obj.__dict__, default=dictdefault))['data']
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
    worksheet.write_string(2, 2, 'CCBS Master Excel', header_format)
    writer.save()
    BytesIO.seek(0)
    BytesIO.size = BytesIO.__sizeof__()
    file = ContentFile(BytesIO.read())
    XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response = HttpResponse(file, content_type=XLSX_MIME)
    response['Content-Disposition'] = 'attachment; filename="CCBS Master.xlsx"'
    logger.info("Test_Download Data:")
    return response

@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_ccbsmapping(request,ccbsmapping_id):
    if request.method == 'GET':
        scope = request.scope
        ccbsmapping_service = CcbsMappingService(scope)
        user_id = request.employee_id
        resp_obj = ccbsmapping_service.fetch_ccbsmapping(ccbsmapping_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_ccbsmapping(request,ccbsmapping_id)

@csrf_exempt
def delete_ccbsmapping(request,ccbsmapping_id):
    scope = request.scope
    ccbsmapping_service = CcbsMappingService(scope)
    resp_obj = ccbsmapping_service.delete_ccbsmapping(ccbsmapping_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def searchcostcentre(request):
    scope = request.scope
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    query = request.GET.get('query','')
    ccbsmapping_service = CcbsMappingService(scope)
    resp_obj = ccbsmapping_service.searchcostcentre(vys_page, query)
    return HttpResponse(resp_obj.get(), content_type='application/json')


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def searchbusinesssegment(request):
    scope = request.scope
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    query = request.GET.get('query','')
    ccbsmapping_service = CcbsMappingService(scope)
    resp_obj = ccbsmapping_service.searchbusinesssegment(vys_page, query)
    return HttpResponse(resp_obj.get(), content_type='application/json')


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def search_ccbs(request):
    scope = request.scope
    ccbs_obj = json.loads(request.body)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    ccbsmapping_service = CcbsMappingService(scope)
    resp_obj = ccbsmapping_service.search_ccbs(vys_page, ccbs_obj)
    return HttpResponse(resp_obj.get(), content_type='application/json')


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def listactive(request):
    scope = request.scope
    ccbsmapping_service = CcbsMappingService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = ccbsmapping_service.ccbsmapping_listactive(vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def listinactive(request):
    scope = request.scope
    ccbsmapping_service = CcbsMappingService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = ccbsmapping_service.ccbsmapping_listInactive(vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def searchbs_cc(request):
    scope = request.scope
    ccbsmapping_service = CcbsMappingService(scope)
    query = request.GET.get('query')
    bs_id = request.GET.get('bs_id', None)
    resp_obj = ccbsmapping_service.searchbs_cc(bs_id, query)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
