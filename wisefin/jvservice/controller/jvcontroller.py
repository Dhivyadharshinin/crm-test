import json
import traceback

import pandas as pd
from django.db import transaction
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from docservice.service.documentservice import DocumentsService
from docservice.util.docutil import DocModule
from ecfservice.util.ecfutil import get_fileextension_val
from jvservice.data.request.jvdetailrequest import JVDetailEntryrequest
from jvservice.data.request.jventryrequest import JVEntryrequest
from jvservice.data.response.jvdetailresponse import JVDetailEntryresponse
from jvservice.models import JVFiles
from jvservice.service.jvdetailservice import JVDetailService
from jvservice.service.jventryservice import JVEntryService
from jvservice.util.jvutil import get_Journaltype_list, get_JournalDetail_list, get_journalstatus_list, \
    JournalDetailType
from nwisefin.settings import logger
from taservice.util.ta_util import DictObj
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission

#test
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_journaltype(request):
    resp_obj = get_Journaltype_list()
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_journaldetailtype(request):
    resp_obj = get_JournalDetail_list()
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@transaction.atomic
@csrf_exempt
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_jventry(request):
    if request.method == 'POST':
        scope = request.scope
        logger.info("start")
        doc_service = DocumentsService(scope)
        logger.info("s3 function end")
        docmodule_obj = DocModule()
        for i in request.FILES.getlist('file'):
            file_name = i.name
            print(file_name, ',file_name')
            extension = file_name.split('.')[-1]
            logger.info("fileextension " + str(file_name) + ' ' + str(extension))
            filetype_check = get_fileextension_val(extension)
            logger.info("filetypecheck " + str(filetype_check))
            if filetype_check is False:
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_FILETYPE)
                error_obj.set_description(ErrorDescription.INVALID_FILETYPE)
                response = HttpResponse(error_obj.get(), content_type="application/json")
                return HttpResponse(response, content_type='application/json')
            logger.info("Fuction Entry")
        jv_data = json.loads(request.data.dict().get('data'))
        # jv_data = json.loads(request.body)
        emp_id = request.employee_id
        print("c1")
        jvdetail = []
        jve_obj = JVEntryrequest(jv_data)
        jv_service = JVEntryService(scope)
        resp_obj = jv_service.jventrycreate(request,jve_obj, emp_id)
        print("jvheader",resp_obj.__dict__)
        jventry_id = resp_obj.id
        print("ecf_id", jventry_id)
        params = dict()
        params['module'] = docmodule_obj.JV
        params['ref_id'] = docmodule_obj.JV
        params['ref_type'] = docmodule_obj.JV
        resp_obj3 = doc_service.upload(request, params)
        logger.info("docupload" + str(resp_obj3))
        document_json = json.loads(resp_obj3.get())['data']
        logger.info("docjson" + str(document_json))
        docfl_obj = jv_service.upload(document_json, jventry_id, emp_id)
        a = jv_data.get("JournalDetail")
        for pr in a:
            jvdetail_obj = JVDetailEntryrequest(pr)
            jvdetail_service = JVDetailService(scope)
            resp_obj1 = jvdetail_service.jvdetailentrycreate(request,jvdetail_obj,jventry_id, emp_id)
            jvdetail_id = resp_obj1.id
            jvdetail.append(jvdetail_id)
            print("jvdetail",resp_obj1.__dict__)
        response = HttpResponse(resp_obj1.get(), content_type='application/json')
        return response
    elif request.method == 'GET':
        return fetch_jventry_list(request)

def fetch_jventry_list(request):
    scope = request.scope
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    emp_id = request.employee_id
    jv_service = JVEntryService(scope)
    response_obj = jv_service.fetch_journal_list(request,vys_page)
    response = HttpResponse(response_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_jventry(request, jv_id):
    if request.method == 'GET':
        scope = request.scope
        emp_id = request.employee_id
        jv_service = JVEntryService(scope)
        resp_obj = jv_service.fetch_jventry(request,jv_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def search_jv(request):
    if request.method == 'GET':
        scope = request.scope
        jecrno = request.GET.get('jecrno')
        jestatus = request.GET.get('jestatus')
        jeamount = request.GET.get('jeamount')
        jerefno = request.GET.get('jerefno')
        jetype = request.GET.get('jetype')
        jebranch = request.GET.get('jebranch')
        created_by = request.GET.get('created_by')
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        jv_service = JVEntryService(scope)
        resp_obj = jv_service.search_jv(request,vys_page,jecrno,jestatus,jeamount,jerefno,jetype,jebranch,created_by)
        return HttpResponse(resp_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_journalaprvl_list(request):
    scope = request.scope
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    emp_id = request.employee_id
    jv_service = JVEntryService(scope)
    response_obj = jv_service.fetch_journalaprvl_list(request,vys_page)
    response = HttpResponse(response_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def delete_jventry(request, jv_id):
    if request.method == 'GET':
        scope = request.scope
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        emp_id = request.employee_id
        jv_service = JVEntryService(scope)
        resp_obj = jv_service.Delete_jventry(request,jv_id, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def delete_jvdentry(request, jv_id):
    if request.method == 'GET':
        scope = request.scope
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        emp_id = request.employee_id
        jvdetail_service = JVDetailService(scope)
        resp_obj = jvdetail_service.Delete_jvdentry(request,jv_id, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

#jvreject
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def jvreject(request):
    if request.method == 'POST':
        jv_data = json.loads(request.body)
        jv_obj = JVEntryrequest(jv_data)
        scope = request.scope
        emp_id = request.employee_id
        jv_service = JVEntryService(scope)
        response_obj = jv_service.status_UpdateRejected(request,jv_obj, emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response


#jvapproved
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def jvapproved(request):
    if request.method == 'POST':
        jv_data = json.loads(request.body)
        jv_obj = JVEntryrequest(jv_data)
        scope = request.scope
        emp_id = request.employee_id
        jv_service = JVEntryService(scope)
        response_obj = jv_service.status_UpdateApproved(request,jv_obj, emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def search_jvrefno(request):
    if request.method == 'GET':
        scope = request.scope
        jerefno = request.GET.get('jerefno')
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        jv_service = JVEntryService(scope)
        resp_obj = jv_service.search_jvrefno(request,jerefno)
        return HttpResponse(resp_obj.get(), content_type='application/json')


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def search_jvupload(request):
    try:
        scope = request.scope
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        emp_id = request.employee_id
        ecf_list_data = NWisefinList()
        if request.method == 'POST' and request.FILES['file']:
            xl_column_name = []
            Credit_amount = 0
            Debit_amount = 0
            column_name = ["EntryType", "Branch", "Category", "Subcategory", "BS", "CC", "CBSGL",
                           "Description", "Amount"]
            files = request.FILES.get('file')
            x = pd.read_excel(files,sheet_name="Sheet1")
            df_data =pd.DataFrame(x)
            filtered_df = df_data.drop(columns=['Description'])
            xl_column_name = list(df_data.columns.values)
            if column_name == xl_column_name:
                try:
                    if filtered_df.isnull().values.any():
                        return JsonResponse(
                            {"MESSAGE": "ERROR_OCCURED", "DATA": "SOME COLUMN IS NULL VALUES"})
                    Credit_amount = round(df_data.loc[df_data['EntryType'] == 'Credit', 'Amount'].sum(), 2)
                    Debit_amount = round(df_data.loc[df_data['EntryType'] == 'Debit', 'Amount'].sum(), 2)
                    if (Credit_amount == Debit_amount):
                        df = df_data.to_dict('records')
                        print('df', df)
                        data_new = df[vys_page.get_offset():vys_page.get_query_limit()]
                        list_length = len(df)
                        if list_length >= 0:
                            for data in data_new:
                                jv_resp = JVDetailEntryresponse()
                                dict = DictObj()
                                jvdata = dict.get_obj(data)
                                from utilityservice.service import api_service
                                api_serv = api_service.ApiService(scope)
                                cat = api_serv.get_cat_code(request, jvdata.Category)
                                sub = api_serv.get_subcat_code(request, jvdata.Subcategory)
                                cc = api_serv.get_cc_code(request, jvdata.CC)
                                bs = api_serv.get_bs_code(request, jvdata.BS)
                                branchcode = api_serv.get_empbrnchdata(jvdata.Branch)
                                if jvdata.EntryType == JournalDetailType.DEBIT_TYPE:
                                    jv_resp.set_EntryType(JournalDetailType.DEBIT)
                                if jvdata.EntryType == JournalDetailType.CREDIT_TYPE:
                                    jv_resp.set_EntryType(JournalDetailType.CREDIT)
                                jv_resp.set_EntryType_id(jvdata.EntryType)
                                jv_resp.set_Branch(branchcode)
                                jv_resp.set_Category(cat)
                                jv_resp.set_Subcategory(sub)
                                jv_resp.set_BS(bs)
                                jv_resp.set_CC(cc)
                                jv_resp.set_CBSGL(jvdata.CBSGL)
                                jv_resp.set_Description(jvdata.Description)
                                jv_resp.set_Amount(jvdata.Amount)
                                ecf_list_data.append(jv_resp)
                        vpage = NWisefinPaginator(df, vys_page.get_index(), 10)
                        ecf_list_data.set_pagination(vpage)
                    return HttpResponse(ecf_list_data.get(), content_type='application/json')
                except Exception as excep:
                    traceback.print_exc()
                    error_obj = NWisefinError()
                    error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                    error_obj.set_description(str(excep))
                    return error_obj
            else:
                traceback.print_exc()
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
                error_obj.set_description("Column name not matched")
                return error_obj
        else:
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
            error_obj.set_description("Column name not matched")
            return error_obj
    except Exception as e:
        traceback.print_exc(True)
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
        error_obj.set_description(str(e))
        return error_obj

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_journalstatus(request):
    resp_obj = get_journalstatus_list()
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

#Transaction details
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_jvtransget(request, No):
    if request.method == 'GET':
        emp_id = request.employee_id
        scope = request.scope
        jvdetail_service = JVDetailService(scope)
        response = jvdetail_service.jv_queuedetails(request,No)
        resp_obj = HttpResponse(response.get(), content_type="application/json")
        return resp_obj

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_file(request,file_id):
    scope = request.scope
    doc_service = DocumentsService(scope)
    emp_id = request.employee_id
    resp_obj = doc_service.doc_download(file_id, emp_id)
    return resp_obj

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def delete_file(request,file_id):
    scope = request.scope
    emp_id = request.employee_id
    jv_service = JVEntryService(scope)
    resp_obj = jv_service.Delete_jvfiles(request,file_id,emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def view_file(request, file_id):
    scope = request.scope
    logger.info("view file Id" + str(file_id))
    doc_service = DocumentsService(scope)
    response = doc_service.file_download(file_id, request)
    return response

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def view_exceltemplate(request):
    try:
        import pandas as pd
        import io
        Bytes = io.BytesIO()
        df_marks = pd.DataFrame({'EntryType': [1,2],'Branch': [101,101],'Category': ['SAL-DIRECTOR','SAL-DIRECTOR'],'Subcategory': ['CONVEYANCE','CONVEYANCE'],
                                 'BS': [11,11],'CC': [111,111],'CBSGL': [426000600,426000600],'Description': ['RECTIFICATION ENTRY','RECTIFICATION ENTRY'],'Amount': [100,100]})
        writer = pd.ExcelWriter(Bytes,engine='xlsxwriter')
        df_marks.to_excel(writer)
        writer.save()
        Bytes.seek(0)
        file_name = 'SampleExcel.xlsx'
        response = StreamingHttpResponse(Bytes, content_type='application/octet-stream')
        response['Content-Disposition'] = 'inline; filename="{}"'.format(file_name)
        print('Excel File is created successfully.')
        return response
    except Exception as e:
        error_obj = NWisefinError()
        error_obj.set_code(ErrorMessage.UNEXPECTED_ERROR)
        error_obj.set_description(str(e))
        return error_obj
