import base64
import io
import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
from django.http import StreamingHttpResponse
from datetime import datetime, date
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from docservice.service.documentservice import DocumentsService
from docservice.util import docutil
from docservice.util.docutil import DocModule
# from faservice.controller.cwipgroupcontroller import fa_obj
from faservice.data.request.assetupdaterequest import AssetUpdateRequest
from faservice.models import AssetDetails
from faservice.service.assetdetailupdateservice import AssetUpdateService
from faservice.util.FaApiService import FaApiService, DictObj
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess
from utilityservice.data.response.nwisefinerror import NWisefinError as Error
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription,ErrorMessage
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission




@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def assetupdate(request):
    scope=request.scope
    if request.method == "POST":
        emp_id = request.employee_id
        form_json = json.loads(request.data.get('data'))
        logger.info('FAL_ASSETUPDATE_DATA:{}'.format(form_json))
        response_obj = AssetUpdateRequest(form_json)
        doc_id = 1
        asset_update = AssetUpdateService(scope)
        assetupdate_resp = asset_update.create_asset_update(response_obj, doc_id, emp_id)
        return HttpResponse(assetupdate_resp.get(), content_type='application/json')
    elif request.method == "GET":
        return get_full_assetupdate(request)



def get_full_assetupdate(request):
    scope=request.scope

    asset_update = AssetUpdateService(scope)
    user_id = request.user.id
    fa_obj=FaApiService(scope)
    branch_id = fa_obj.get_emp_branch(user_id, request).id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    assetdetails_resp = asset_update.get_all_assetupdate(vys_page, user_id, branch_id, request)
    # print('assetdetails_resp', assetdetails_resp, type(assetdetails_resp))
    return HttpResponse(assetdetails_resp.get(), content_type='application/json')


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def approver(request):
    scope=request.scope

    asset_update = AssetUpdateService(scope)
    if request.method == "POST":
        form_json = json.loads(request.body)
        logger.info('FAL_ASSETUPDATE_APPROVE_DATA:{}'.format(form_json))
        response_obj = AssetUpdateRequest(form_json)
        assetupdate_resp = asset_update.create_asset_update1(response_obj)
        return HttpResponse(assetupdate_resp.get(), content_type='application/json')
    elif request.method == "GET":
        return get_full_assetupdate(request)


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def approver_save(request):
    scope=request.scope

    asset_update = AssetUpdateService(scope)
    if request.method == "POST":
        form_json = json.loads(request.body)
        logger.info('FAL_ASSET_UPDATE_SAVE_DATA:{}'.format(form_json))
        response_obj = AssetUpdateRequest(form_json)
        assetupdate_resp = asset_update.approver_save(response_obj)
        return HttpResponse(assetupdate_resp.get(), content_type='application/json')


# @csrf_exempt
# def addrow_duplicate(request,update_id):
#     asset_update= AssetUpdateService(scope)
#     if request.method == "GET":
#         assetdetails_resp=asset_update.duplicate_record(update_id)
#         return HttpResponse(assetdetails_resp.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def branchfilter(request):
    scope=request.scope

    asset_update = AssetUpdateService(scope)
    if request.method == "GET":
        user_id = request.employee_id
        fa_obj = FaApiService(scope)
        emp_service = FaApiService(scope)
        user_id = emp_service.get_empid_from_userid(user_id)
        branch_id = None
        try:
            branch_code = fa_obj.get_emp_branch(user_id, request).code
            # ctrlbranch = fa_obj.get_emp_branch(user_id, request).ctrlbranch
        except:
            err = Error()
            err.set_code(ErrorMessage.INVALID_branch_ID)
            err.set_description(ErrorDescription.INVALID_branch_ID)
            resp = HttpResponse(err.get(), content_type='application/json')
            return resp
        page = int(request.GET.get('page', 1))
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        assetdetails_resp = asset_update.get_asset_update_records(branch_code, user_id, request, vys_page)
        return HttpResponse(json.dumps(assetdetails_resp), content_type='application/json')


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def branchupdate1(request):
    scope=request.scope

    asset_update = AssetUpdateService(scope)
    if request.method == "GET":
        fa_obj = FaApiService(scope)
        page = int(request.GET.get('page', 1))
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        assetdetails_resp = asset_update.get_asset_branch_update_records_Dup(request, vys_page)
        return HttpResponse(assetdetails_resp.get(), content_type='application/json')


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fullapproverupdate1(request):
    scope=request.scope

    asset_update = AssetUpdateService(scope)
    if request.method == "GET":
        fa_obj = FaApiService(scope)
        page = int(request.GET.get('page', 1))
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        assetdetails_resp = asset_update.get_asset_update_records_Dup(request, vys_page)
        return HttpResponse(assetdetails_resp.get(), content_type='application/json')


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def branchupdate(request):
    scope=request.scope

    asset_update = AssetUpdateService(scope)
    if request.method == "GET":
        user_id = request.employee_id
        fa_obj = FaApiService(scope)
        emp_service = FaApiService(scope)
        user_id = emp_service.get_empid_from_userid(user_id)
        branch_id = None
        try:
            branch_code = fa_obj.get_emp_branch(user_id, request).code
            # ctrlbranch = fa_obj.get_emp_branch(user_id, request).ctrlbranch
        except:
            err = Error()
            err.set_code(ErrorMessage.INVALID_branch_ID)
            err.set_description(ErrorDescription.INVALID_branch_ID)
            resp = HttpResponse(err.get(), content_type='application/json')
            return resp
        page = int(request.GET.get('page', 1))
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        assetdetails_resp = asset_update.get_asset_branch_update_records(branch_code, user_id, request, vys_page)
        return HttpResponse(json.dumps(assetdetails_resp), content_type='application/json')


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def branchfile_download(request):
    scope=request.scope

    if request.method == "GET":
        import io
        BytesIO = io.BytesIO()
        asset_update = AssetUpdateService(scope)
        output = BytesIO
        user_id = request.user.id
        fa_obj = FaApiService(scope)
        emp_service = FaApiService(scope)
        user_id = emp_service.get_empid_from_userid(user_id)
        branch_id = None
        branch_id = fa_obj.get_emp_branch(user_id, request)
        if branch_id is None:
            collection = asset_update.get_json_excel_branch_records1(request)
        if branch_id is not None:
            collection = asset_update.get_json_excel_branch_records(request,branch_id.code,user_id)
        df = pd.DataFrame.from_dict(collection, orient='index')
        df = df.transpose()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Sheet1', index=True)
        writer.save()
        output.seek(0)
        file_name = 'Summary-Report-EXCEL-DOWNLOAD-(' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ').xlsx'
        response = StreamingHttpResponse(output, content_type='application/octet-stream')
        response['Content-Disposition'] = 'inline; filename="{}"'.format(file_name)
        return response


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fullfile_download(request):
    scope=request.scope

    if request.method == "GET":
        import io
        user_id = request.user.id
        fa_obj = FaApiService(scope)
        emp_service = FaApiService(scope)
        user_id = emp_service.get_empid_from_userid(user_id)
        branch_id = None
        BytesIO = io.BytesIO()
        asset_update = AssetUpdateService(scope)
        branch_id = fa_obj.get_emp_branch(user_id, request)
        if branch_id is None:
            collection = asset_update.get_json_excel_full_records1(request, branch_id.code)
        if branch_id is not None:
            collection = asset_update.get_json_excel_full_records(request, branch_id.code, user_id)
        BytesIO = io.BytesIO()
        asset_update = AssetUpdateService(scope)
        output = BytesIO
        df = pd.DataFrame.from_records(collection)
        # df.fillna('')
        # df.dropna(how='all')
        # print('df1',df)
        # df = df.transpose()
        # print('df2', df)
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Sheet1', index=True)
        writer.save()
        output.seek(0)
        file_name = 'Summary-Report-EXCEL-DOWNLOAD-(' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ').xlsx'
        response = StreamingHttpResponse(output, content_type='application/octet-stream')
        response['Content-Disposition'] = 'inline; filename="{}"'.format(file_name)
        return response


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def assetupdate1(request):
    scope=request.scope

    resp_list = []
    emp_id = request.employee_id
    # emp_id = 1
    form_json = json.loads(request.data.get('data'))
    for request_file in request.FILES.getlist('file'):
        file_name = request_file.name
        extension = file_name.split('.')[-1]
        filetype_check = docutil.file_validation(extension)
        if filetype_check is False:
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_FILETYPE)
            error_obj.set_description(ErrorDescription.SUPPORTED_FILE_TYPES)
            response = HttpResponse(error_obj.get())
            return HttpResponse(response, content_type='application/json')
        elif filetype_check is True:
            if request_file.name:
                mod_obj = DocModule()
                doc_param = {"module": mod_obj.FA, "ref_type": -1,
                             "ref_id": -1}
                doc_obj = DocumentsService(scope)
                img_resp = doc_obj.upload_single_doc(request_file, doc_param)
                asset_update = AssetUpdateService(scope)

                imgresp_json = json.loads(img_resp)

                response_obj = AssetUpdateRequest(form_json)
                assetupdate_resp = asset_update.create_asset_update(response_obj, imgresp_json['id'].split('_')[1],
                                                                    emp_id)

            return HttpResponse('{}', content_type='application/json')


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def add_row1(request):
    scope=request.scope
    resp_list = []
    emp_id = request.employee_id
    # emp_id = 1
    form_json = json.loads(request.data.get('data'))
    if request.FILES.getlist('file'):
        for request_file in request.FILES.getlist('file'):
            file_name = request_file.name
            extension = file_name.split('.')[-1]
            filetype_check = docutil.file_validation(extension)
            if filetype_check is False:
                error_obj = Error()
                error_obj.set_code(ErrorMessage.INVALID_FILETYPE)
                error_obj.set_description(ErrorDescription.SUPPORTED_FILE_TYPES)
                response = HttpResponse(error_obj.get())
                return HttpResponse(response, content_type='application/json')
            elif filetype_check is True:
                if request_file.name:
                    mod_obj = DocModule()
                    doc_param = {"module": mod_obj.FA, "ref_type": -1,
                                 "ref_id": -1}
                    doc_obj = DocumentsService(scope)
                    img_resp = doc_obj.upload_single_doc(request_file, doc_param)
                    asset_update = AssetUpdateService(scope)
                    imgresp_json = json.loads(img_resp)
                    response_obj = AssetUpdateRequest(form_json)
                    barcode = []
                    if response_obj not in barcode:
                        new_barcode = response_obj.get_barcode()
                        asset_details = AssetDetails.objects.filter(barcode=new_barcode)
                        if len(asset_details) > 0:
                            err = Error()
                            err.set_code(ErrorMessage.INVALID_ASSETID_ID)
                            err.set_description(ErrorDescription.INVALID_ASSETID_ID)
                            resp = HttpResponse(err.get(), content_type='application/json')
                            return resp
                    assetupdate_resp = asset_update.create_asset_update(response_obj, imgresp_json['id'].split('_')[1],
                                                                        emp_id)
        response = HttpResponse(assetupdate_resp.get(), content_type="application/json")
        return response
    else:
        res=add_row(request)
        return res

def add_row(request):
    scope=request.scope

    asset_update = AssetUpdateService(scope)
    if request.method == "POST":
        emp_id = request.employee_id
        form_json = json.loads(request.data.get('data'))
        response_obj = AssetUpdateRequest(form_json)
        barcode = []
        if response_obj not in barcode:
            new_barcode = response_obj.get_barcode()
            asset_details = AssetDetails.objects.filter(barcode=new_barcode)
            if len(asset_details) > 0:
                err = Error()
                err.set_code(ErrorMessage.INVALID_ASSETID_ID)
                err.set_description(ErrorDescription.INVALID_ASSETID_ID)
                resp = HttpResponse(err.get(), content_type='application/json')
                return resp
        doc_id = 1
        assetupdate_resp = asset_update.new_record(response_obj, doc_id, emp_id)
    response = HttpResponse(assetupdate_resp.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def update_pv1(request):
    scope=request.scope

    resp_list = []
    emp_id = request.user.id
    # emp_id = 1
    form_json = json.loads(request.data.get('data'))
    if request.FILES.getlist('file'):
        for request_file in request.FILES.getlist('file'):
            file_name = request_file.name
            extension = file_name.split('.')[-1]
            filetype_check = docutil.file_validation(extension)
            if filetype_check is False:
                error_obj = Error()
                error_obj.set_code(ErrorMessage.INVALID_FILETYPE)
                error_obj.set_description(ErrorDescription.SUPPORTED_FILE_TYPES)
                response = HttpResponse(error_obj.get())
                return HttpResponse(response, content_type='application/json')
            elif filetype_check is True:
                if request_file.name:
                    mod_obj = DocModule()
                    doc_param = {"module": mod_obj.FA, "ref_type": -1,
                                 "ref_id": -1}
                    doc_obj = DocumentsService(scope)
                    img_resp = doc_obj.upload_single_doc(request_file, doc_param)
                    asset_update = AssetUpdateService(scope)
                    imgresp_json = json.loads(img_resp)
                    response_obj = AssetUpdateRequest(form_json)
                    assetupdate_resp = asset_update.update_pv_new1(response_obj, imgresp_json['id'].split('_')[1],
                                                                        emp_id)
        response = HttpResponse(assetupdate_resp.get(), content_type="application/json")
        return response
    else:
        res=add_row(request)
        return res


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])

def update_pv(request):
    scope=request.scope

    asset_update = AssetUpdateService(scope)
    if request.method == "POST":
        emp_id = request.user.id
        form_json = json.loads(request.data.get('data'))
        response_obj = AssetUpdateRequest(form_json)
        doc_id = 1
        assetupdate_resp = asset_update.update_pv_new(response_obj, doc_id, emp_id)
    response = HttpResponse(assetupdate_resp.get(), content_type="application/json")
    return response

# def add_row(request):
#     emp_id = request.user.id
#     form_json = json.loads(request.POST.get('data'))
#     for request_file in request.FILES.getlist('images'):
#         file_name = request_file.name
#         extension = file_name.split('.')[-1]
#         filetype_check = docutil.file_validation(extension)
#         if filetype_check is False:
#             error_obj = Error()
#             error_obj.set_code(ErrorMessage.INVALID_FILETYPE)
#             error_obj.set_description(ErrorDescription.SUPPORTED_FILE_TYPES)
#             response = HttpResponse(error_obj.get())
#             return HttpResponse(response, content_type='application/json')
#         elif filetype_check is True:
#             if request_file.name:
#                 mod_obj = DocModule()
#                 doc_param = {"module": mod_obj.FA, "ref_type": -1,
#                              "ref_id": -1}
#                 doc_obj = DocumentsService(scope)
#                 img_resp = doc_obj.upload_single_doc(request_file, doc_param)
#                 asset_update = AssetUpdateService(scope)
#                 imgresp_json = json.loads(img_resp)
#                 response_obj = AssetUpdateRequest(form_json)
#                 barcode = []
#                 if response_obj not in barcode:
#                     new_barcode = response_obj.get_barcode()
#                     asset_details = AssetDetails.objects.filter(barcode=new_barcode)
#                     if len(asset_details) > 0:
#                         err = Error()
#                         err.set_code(ErrorMessage.INVALID_ASSETID_ID)
#                         err.set_description(ErrorDescription.INVALID_ASSETID_ID)
#                         resp = HttpResponse(err.get(), content_type='application/json')
#                         return resp
#
#                 assetupdate_resp = asset_update.new_record(response_obj, imgresp_json['id'].split('_')[1],emp_id)
#                 return HttpResponse(assetupdate_resp.get(), content_type='application/json')
