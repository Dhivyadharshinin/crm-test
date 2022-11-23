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
from masterservice.data.request.ccbsrequest import CostCentreRequest , BusinessSegmentRequest, MasterBusinesssegmentRequest
from masterservice.service.ccbsservice import CostCentreService , BusinessSegmentService
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def costcentre(request):
    if request.method == 'POST':
        scope = request.scope
        emp_id = request.employee_id
        costcentre_service = CostCentreService(scope)
        costcentre_data = json.loads(request.body)
        # user_id = request.employee_id
        costcentre_obj = CostCentreRequest(costcentre_data)
        resp_obj = costcentre_service.create_costcentre(costcentre_obj, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_costcentre_list(request)

def fetch_costcentre_list(request):
    scope = request.scope
    costcentre_service = CostCentreService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    user_id = request.employee_id
    resp_obj = costcentre_service.fetch_costcentre_list(vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_costcentre(request,costcentre_id):
    if request.method == 'GET':
        scope = request.scope
        costcentre_service = CostCentreService(scope)
        user_id = request.employee_id
        resp_obj = costcentre_service.fetch_costcentre(costcentre_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_costcentre(request,costcentre_id)

@csrf_exempt
def delete_costcentre(request,costcentre_id):
    scope = request.scope
    costcentre_service = CostCentreService(scope)
    resp_obj = costcentre_service.delete_costcentre(costcentre_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def costcentrelist(request):
    scope = request.scope
    costcentre_service = CostCentreService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    user_id = request.employee_id
    resp_obj = costcentre_service.costcentrelist(vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def costcentre_download(request):
    scope = request.scope
    costcentre_service = CostCentreService(scope)
    user_id = request.user.id
    resp_obj = costcentre_service.fetch_costcentre_download(user_id)
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
    worksheet.write_string(2, 2, 'Costcentre Master Excel', header_format)
    writer.save()
    BytesIO.seek(0)
    BytesIO.size = BytesIO.__sizeof__()
    file = ContentFile(BytesIO.read())
    XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response = HttpResponse(file, content_type=XLSX_MIME)
    response['Content-Disposition'] = 'attachment; filename="Costcentre Master.xlsx"'
    logger.info("Test_Download Data:")
    return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def updateccstatus(request,costcentre_id):
    scope = request.scope
    emp_id = request.employee_id
    costcentre_service = CostCentreService(scope)
    # user_id = request.employee_id
    status =request.GET.get('status')
    resp_obj = costcentre_service.updateCCstatus(costcentre_id,status,emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def businesssegmentsearch(request):
    scope = request.scope
    businesssegment_service = BusinessSegmentService(scope)
    name = request.GET.get('name')
    no = request.GET.get('no')
    query = {"name": name, "no": no}
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = businesssegment_service.businesssegmentsearch(vys_page,query)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def businesssegmentsearch_mst(request):
    scope = request.scope
    businesssegment_service = BusinessSegmentService(scope)
    # name = request.GET.get('name')
    # no = request.GET.get('no')
    # query = {"name": name, "no": no}
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = businesssegment_service.businesssegmentsearch_mst(vys_page,request)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def costcentresearch(request):
    scope = request.scope
    costcentre_service = CostCentreService(scope)
    name = request.GET.get('name')
    no = request.GET.get('no')
    query = {"name": name, "no": no}
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = costcentre_service.costcentresearch(vys_page,query)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def costcentresearch_overall(request):
    scope = request.scope
    costcentre_service = CostCentreService(scope)
    name = request.GET.get('name')
    no = request.GET.get('no')
    query = {"name": name, "no": no}
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = costcentre_service.costcentresearch_overall(vys_page,query)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def costcentresearch_overall_mst(request):
    scope = request.scope
    costcentre_service = CostCentreService(scope)
    # name = request.GET.get('name')
    # no = request.GET.get('no')
    # query = {"name": name, "no": no}
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = costcentre_service.costcentresearch_overall_mst(vys_page,request)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def cclistactive(request):
    scope = request.scope
    costcentre_service = CostCentreService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    user_id = request.employee_id
    resp_obj = costcentre_service.costcentreActivelist(vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def cclistinactive(request):
    scope = request.scope
    costcentre_service = CostCentreService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    user_id = request.employee_id
    resp_obj = costcentre_service.costcentreInactivelist(vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def businesssegment(request):
    if request.method == 'POST':
        scope =request.scope
        emp_id = request.employee_id
        businesssegment_service = BusinessSegmentService(scope)
        businesssegment_data = json.loads(request.body)
        # user_id = request.employee_id
        businesssegment_obj = BusinessSegmentRequest(businesssegment_data)
        resp_obj = businesssegment_service.create_businesssegment(businesssegment_obj, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_businesssegment_list(request)

def fetch_businesssegment_list(request):
    scope = request.scope
    businesssegment_service = BusinessSegmentService(scope)
    page = request.GET.get('page', 1)
    query = request.GET.get('query')
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    user_id = request.employee_id
    resp_obj = businesssegment_service.fetch_businesssegment_list(vys_page,query)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def businesssegmentlist(request):
    scope = request.scope
    businesssegment_service = BusinessSegmentService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    user_id = request.employee_id
    resp_obj = businesssegment_service.businesssegmentlist(vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def businesssegment_download(request):
    scope = request.scope
    businesssegment_service = BusinessSegmentService(scope)
    user_id = request.user.id
    resp_obj = businesssegment_service.fetch_businesssegment_download(user_id)
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
    worksheet.write_string(2, 2, 'BusinessSegment Master Excel', header_format)
    writer.save()
    BytesIO.seek(0)
    BytesIO.size = BytesIO.__sizeof__()
    file = ContentFile(BytesIO.read())
    XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response = HttpResponse(file, content_type=XLSX_MIME)
    response['Content-Disposition'] = 'attachment; filename="BusinessSegment Master.xlsx"'
    logger.info("Test_Download Data:")
    return response

@api_view(['GET'])
def mastersegmentname(request):
    if request.method=='GET':
        scope=request.scope
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        bsserv = BusinessSegmentService(scope)
        resp_obj = bsserv.mastersegmentname_get(request, vys_page)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_businesssegment(request,businesssegment_id):
    if request.method == 'GET':
        scope = request.scope
        businesssegment_service = BusinessSegmentService(scope)
        user_id = request.employee_id
        resp_obj = businesssegment_service.fetch_businesssegment(businesssegment_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_businesssegment(request,businesssegment_id)

@csrf_exempt
def delete_businesssegment(request,businesssegment_id):
    scope =request.scope
    businesssegment_service = BusinessSegmentService(scope)
    resp_obj = businesssegment_service.delete_businesssegment(businesssegment_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def updatebsstatus(request,businesssegment_id):
    scope = request.scope
    emp_id = request.employee_id
    businesssegment_service = BusinessSegmentService(scope)
    # user_id = request.employee_id
    status =request.GET.get('status')
    resp_obj = businesssegment_service.updateBSstatus(businesssegment_id, status, emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def bslistactive(request):
    scope = request.scope
    businesssegment_service = BusinessSegmentService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    user_id = request.employee_id
    resp_obj = businesssegment_service.businesssegmentlistActive(vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def bslistinactive(request):
    scope = request.scope
    businesssegment_service = BusinessSegmentService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    user_id = request.employee_id
    resp_obj = businesssegment_service.businesssegmentlistInactive(vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def businesssegment_mtom(request):
    if request.method == 'POST':
        scope = request.scope
        emp_id = request.employee_id
        businesssegment_service = BusinessSegmentService(scope)
        businesssegment_data = json.loads(request.body)
        # user_id = request.employee_id
        action = request.GET.get('action')
        businesssegment_obj = BusinessSegmentRequest(businesssegment_data)
        resp_obj = businesssegment_service.create_businesssegment_mtom(businesssegment_obj,action, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def costcentre_mtom(request):
    if request.method == 'POST':
        scope = request.scope
        emp_id = request.employee_id
        costcentre_serv = CostCentreService(scope)
        costcentre_data = json.loads(request.body)
        # user_id = request.employee_id
        action = request.GET.get('action')
        costcentre_obj = CostCentreRequest(costcentre_data)
        resp_obj = costcentre_serv.create_costcentre_mtom(costcentre_obj,action, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
###############################
# @csrf_exempt
# @api_view(['POST'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def get_business(request):
#     id_obj = json.loads(request.body)
#     obj = BusinessSegment.objects.filter(id__in=id_obj["bs_id"]).values('id','name','code')
#     arr = []
#     for i in obj:
#         data = {"id": i['id'], "name": i['name'],"code": i['code']}
#         arr.append(data)
#     vendor_dic = json.dumps(arr, indent=4)
#     return HttpResponse(vendor_dic, content_type='application/json')
#
# @csrf_exempt
# @api_view(['POST'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def get_costcentre(request):
#     id_obj = json.loads(request.body)
#     obj = CostCentre.objects.filter(id__in=id_obj["cc_id"]).values('id','name','code')
#     arr = []
#     for i in obj:
#         data = {"id": i['id'], "name": i['name'],"code":i['code']}
#         arr.append(data)
#     vendor_dic = json.dumps(arr, indent=4)
#     return HttpResponse(vendor_dic, content_type='application/json')
#
# #micro to micro New
# #Get cc
# @csrf_exempt
# @api_view(['GET'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def fetch_cc(request):
#     query = request.GET.get('query', None)
#     cc1 = CostCentre.objects.filter(code=query)
#     cc = cc1[0]
#     cc_data = {"id": cc.id, "code": cc.code, "name": cc.name}
#     cc_dic = json.dumps(cc_data, indent=4)
#     return HttpResponse(cc_dic, content_type='application/json')
# #cc getlist
# @csrf_exempt
# @api_view(['POST'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def fetch_cclist(request):
#     cc_ids = json.loads(request.body)
#     cc_id2 = cc_ids['cc_code']
#     obj = CostCentre.objects.filter(code__in=cc_id2).values('id', 'name','code')
#     cc_list_data = NWisefinList()
#     for i in obj:
#         data = {"id": i['id'], "name": i['name'],"code": i['code']}
#         cc_list_data.append(data)
#     return HttpResponse(cc_list_data.get(), content_type='application/json')
#
# #Get bs
# @csrf_exempt
# @api_view(['GET'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def fetch_bs(request):
#     query = request.GET.get('query', None)
#     bs1 = BusinessSegment.objects.filter(code=query)
#     bs = bs1[0]
#     bs_data = {"id": bs.id, "code": bs.code, "name": bs.name}
#     bs_dic = json.dumps(bs_data, indent=4)
#     return HttpResponse(bs_dic, content_type='application/json')
# #bs getlist
# @csrf_exempt
# @api_view(['POST'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def fetch_bslist(request):
#     bs_ids = json.loads(request.body)
#     bs_id2 = bs_ids['bs_code']
#     obj = BusinessSegment.objects.filter(code__in=bs_id2).values('id', 'name','code')
#     bs_list_data = NWisefinList()
#     for i in obj:
#         data = {"id": i['id'], "name": i['name'],"code": i['code']}
#         bs_list_data.append(data)
#     return HttpResponse(bs_list_data.get(), content_type='application/json')

#
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def mastersegmentname(request):
    if request.method=='GET':
        scope = request.scope
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        tax_service = BusinessSegmentService(scope)
        resp_obj = tax_service.mastersegmentname_get(request, vys_page)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def bs_name_get(request):
    if request.method=='GET':
        scope = request.scope
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        bs_service = BusinessSegmentService(scope)
        resp_obj = bs_service.bs_name_get(request, vys_page)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def bs_activate_inactivate(request):
    if request.method == 'POST':
        # print(bs_id)
        scope = request.scope
        bs_service = BusinessSegmentService(scope)
        businesssegment_obj = json.loads(request.body)
        bs_obj = BusinessSegmentRequest(businesssegment_obj)
        resp_obj = bs_service.bs_activate_inactivate(request,bs_obj)
        # print(resp_obj.get())
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def cc_activate_inactivate(request):
    if request.method == 'POST':
        # print(cc_id)
        scope = request.scope
        cc_service = BusinessSegmentService(scope)
        costcentre_obj = json.loads(request.body)
        cc_obj = CostCentreRequest(costcentre_obj)
        resp_obj = cc_service.cc_activate_inactivate(request,cc_obj)
        # print(resp_obj.get())
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_masterbusinesssegment(request):
    if request.method == 'POST':
        scope = request.scope
        businesssegment_service = BusinessSegmentService(scope)
        businesssegment_data = json.loads(request.body)
        user_id = request.user.id
        businesssegment_obj = MasterBusinesssegmentRequest(businesssegment_data)
        resp_obj = businesssegment_service.create_masterbusinesssegment(businesssegment_obj, user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def apsectorname_get(request):
    if request.method=='GET':
        scope = request.scope
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        bs_service = BusinessSegmentService(scope)
        resp_obj = bs_service.apsectorname_get(request, vys_page)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

