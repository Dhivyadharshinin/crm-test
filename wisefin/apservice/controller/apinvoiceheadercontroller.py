import json
import sys
import traceback
from django.db import transaction
from apservice.data.request.apinvoiceheaderrequest import APInvoiceheaderrequest
from apservice.service.apdocumentservice import APDocumentService
from apservice.service.apinvoiceheaderservice import APInvoiceheaderService
from apservice.service.apservice import APService
from apservice.util.aputil import get_yes_or_no_list, ap_get_api_caller, ap_post_api_caller, APRefType, AP_Status, \
    get_apfileextension_val
from docservice.service.documentservice import DocumentsService
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpage import NWisefinPage, NWisefinPageExtra
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_apinwardinvhdr(request):
    if request.method == 'POST':
        try:
            #with transaction.atomic(using=DataBase.AP_DB):
            from utilityservice.service import api_service
            from apservice.service.apheaderservice import APHeaderService
            scope = request.scope
            aphdr_serv = APHeaderService(scope)
            ap_data = json.loads(request.data.dict().get('data'))
            crno_duplicate_val = aphdr_serv.apheader_duplicate_validation(ap_data['crno'])
            if crno_duplicate_val is True:
                error_obj = NWisefinError()
                error_obj.set_code('Duplicate crno')
                error_obj.set_description('This crno is already exist')
                response = HttpResponse(error_obj.get(), content_type="application/json")
                return response
            emp_id = request.employee_id
            ap_serv=APService(scope)
            response_obj=ap_serv.ap_create(request,ap_data,emp_id)
            response = HttpResponse(response_obj.get(), content_type='application/json')
            return response
        except Exception  as excep:
            traceback.print_exc()
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep)+" - "+ str(filename)+", line_no : "+str(line_number)+str(', exception_type : {c} '.format(c=type(excep).__name__)))
            response = HttpResponse(error_obj.get(), content_type='application/json')
            return response


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_apinvoiceheader(request,apheader_id):
    if request.method == 'POST':
        try:
            #with transaction.atomic(using=DataBase.AP_DB):
            from utilityservice.service import api_service
            ap_data = json.loads(request.data.dict().get('data'))
            emp_id = request.employee_id
            return_list = NWisefinList()

            for invhdr_json in ap_data['invoiceheader']:
                if "file_key" in invhdr_json:
                    if invhdr_json["file_key"] != None and len(invhdr_json["file_key"]) > 0:
                        for file_key in invhdr_json["file_key"]:
                            file_count = len(request.FILES.getlist(file_key))
                            for i in range(0, file_count):
                                file = request.FILES.getlist(file_key)[i]
                                file_name = file.name
                                extension = file_name.split('.')[-1]
                                filetype_check = get_apfileextension_val(extension)
                                print("filetype_check ",filetype_check)
                                if filetype_check != False:
                                    error_obj = NWisefinError()
                                    error_obj.set_code(ErrorMessage.INVALID_FILETYPE)
                                    error_obj.set_description(str(file_name) + " - This Is Invalid File Format")
                                    response = HttpResponse(error_obj.get(), content_type="application/json")
                                    return response


            file_list=None
            for apinvhdr_json in ap_data['invoiceheader']:
                scope = request.scope
                apinvhdr_obj = APInvoiceheaderrequest(apinvhdr_json)
                apinvhdr_serv = APInvoiceheaderService(scope)
                apinvhdr_response = apinvhdr_serv.apinvhdrcreate(request,file_list,apinvhdr_json, apinvhdr_obj, apheader_id, emp_id)
                return_list.append(apinvhdr_response)


            response = HttpResponse(return_list.get(), content_type='application/json')
            return response
        except Exception as excep:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            traceback.print_exc()
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep) + " - " + str(filename) + ", line_no: " + str(line_number) + str(
                ', exception_type : {c} '.format(c=type(excep).__name__)))
            return HttpResponse(error_obj.get(), content_type='application/json')




@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_pocket_apinwardinvoicehdr(request,inwarddtl_id):
    if request.method == 'GET':
        scope = request.scope
        apinward_service=APInvoiceheaderService(scope)
        emp_id = request.employee_id
        response_obj = apinward_service.get_pocket_apinvoiceheader(request, emp_id,inwarddtl_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_yes_ror_no_dropdown(request):
    if request.method == 'GET':
        emp_id = request.employee_id
        resp_obj = get_yes_or_no_list()
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def apstatus_update(request):
    if request.method == 'POST':
        scope = request.scope
        ap_data = json.loads(request.body)
        apinvoicehdr_service = APInvoiceheaderService(scope)
        emp_id = request.employee_id
        print('emp_id ',emp_id)
        if int(ap_data['status_id']) == AP_Status.APPROVED:
            apqueue_data=apinvoicehdr_service.maker_as_approver_validation(ap_data['apinvoicehdr_id'],emp_id)
            if apqueue_data != False:
                return HttpResponse(apqueue_data.get(), content_type="application/json")
            actual_apstatus = [AP_Status.PENDING_FOR_APPROVAL, AP_Status.AP_INITIATE]
            apstatus_validation = apinvoicehdr_service.apstatus_update_validation(ap_data['apinvoicehdr_id'],actual_apstatus)
            if apstatus_validation != False:
                return HttpResponse(apstatus_validation.get(), content_type="application/json")
        if int(ap_data['status_id']) == AP_Status.PAYMENT_INITIATE:
            actual_apstatus = [AP_Status.APPROVED,AP_Status.PAY_INITIATE]
            apstatus_validation = apinvoicehdr_service.apstatus_update_validation(ap_data['apinvoicehdr_id'], actual_apstatus)
            if apstatus_validation != False:
                return HttpResponse(apstatus_validation.get(), content_type="application/json")
        resp_obj = apinvoicehdr_service.apstatus_change(request,ap_data,emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def apdedupe_check(request,apinvoiveheader_id):
    if request.method == 'GET':
        scope = request.scope
        dedupe_type = request.GET.get('type')
        apinvoicehdr_service = APInvoiceheaderService(scope)
        emp_id = request.employee_id
        print('emp_id ',emp_id)
        resp_obj = apinvoicehdr_service.apdedupe_check(request,dedupe_type,apinvoiveheader_id,emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_apinvoiceheader(request):
    if request.method == 'POST':
        scope = request.scope
        ap_data = json.loads(request.body)
        apinvoicehdr_service=APInvoiceheaderService(scope)
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        emp_id = request.employee_id
        response_obj = apinvoicehdr_service.get_apinwardinvoiceheader(request,ap_data,vys_page, emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def supplierpaymentacctno_validation(request):
    if request.method == 'POST':
        scope = request.scope
        ap_data = json.loads(request.body)
        apinvoicehdr_service=APInvoiceheaderService(scope)
        emp_id = request.employee_id
        response_obj = apinvoicehdr_service.supplierpaymentacctno_val(request,ap_data, emp_id)
        response = HttpResponse(response_obj, content_type='application/json')
        return response


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_preparepayment(request):
    if request.method == 'POST':
        scope = request.scope
        ap_data = json.loads(request.body)
        apinvoicehdr_service=APInvoiceheaderService(scope)
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPageExtra(page, 25)
        emp_id = request.employee_id
        response_obj = apinvoicehdr_service.fetch_preparepayment(request,ap_data,vys_page, emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_paymentfile(request):
    if request.method == 'POST':
        scope = request.scope
        ap_data = json.loads(request.body)
        apinvoicehdr_service=APInvoiceheaderService(scope)
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPageExtra(page, 25)
        emp_id = request.employee_id
        response_obj = apinvoicehdr_service.fetch_paymentfile(request,ap_data,vys_page, emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def upload_payment(request):
    if request.method == 'POST':
        scope = request.scope
        manual_action = request.GET.get('manual', None)
        ap_data=None
        if manual_action:
            ap_data = json.loads(request.data.dict().get('data'))
        apinvoicehdr_service=APInvoiceheaderService(scope)
        emp_id = request.employee_id
        response_obj = apinvoicehdr_service.paymentstatus_update(request,ap_data, emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def paymentdetails_download(request,bankdetails_id):
    if request.method == 'POST':
        scope = request.scope
        ap_data = json.loads(request.body)
        apinvoicehdr_service=APInvoiceheaderService(scope)
        emp_id = request.employee_id
        response_obj = apinvoicehdr_service.payment_excel_download(request,ap_data,bankdetails_id, emp_id)
        #response = HttpResponse(response_obj), content_type='application/json')
        return response_obj



@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_bounce_summary(request):
    if request.method == 'POST':
        scope = request.scope
        filter_data = json.loads(request.body)
        apinvoicehdr_service=APInvoiceheaderService(scope)
        page = request.GET.get('page', 1)
        type = request.GET.get('type')
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        emp_id = request.employee_id
        response_obj = apinvoicehdr_service.get_bounce(request,filter_data,vys_page,type, emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_apbounce_single(request,apinvheader_id):
    if request.method == 'GET':
        scope = request.scope
        apinvoicehdr_service=APInvoiceheaderService(scope)
        emp_id = request.employee_id
        resp_obj = apinvoicehdr_service.single_get_bounce( request,apinvheader_id, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@csrf_exempt
@api_view(['GET','DELETE','POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_apinvoicehdr_single(request,apinvheader_id):
    if request.method == 'GET':
        scope = request.scope
        apinvoicehdr_service=APInvoiceheaderService(scope)
        emp_id = request.employee_id
        resp_obj = apinvoicehdr_service.single_get_apinwardinvoiceheader(request,apinvheader_id,emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_apinvoicehdr_single(request,apinvheader_id)
    elif request.method == 'POST':
        return update_entry_flag_apinvoicehdr_single(request,apinvheader_id)

#
# def get_apinvhdr_using_apinvhdr(request, apinvheader_id):
#     scope = request.scope
#     apinvoicehdr_service = APInvoiceheaderService(scope)
#     emp_id = request.employee_id
#     resp_obj = apinvoicehdr_service.get_apinvhdr_using_apinvhdr(apinvheader_id)
#     response = HttpResponse(json.dumps(resp_obj), content_type="application/json")
#     return response


def delete_apinvoicehdr_single(request,apinvheader_id):
    scope = request.scope
    apinvoicehdr_service=APInvoiceheaderService(scope)
    emp_id = request.employee_id
    resp_obj = apinvoicehdr_service.apinvoiceheader_delete(apinvheader_id,emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


def update_entry_flag_apinvoicehdr_single(request,apinvheader_id):
    scope = request.scope
    apinvoicehdr_service=APInvoiceheaderService(scope)
    emp_id = request.employee_id
    ap_data = json.loads(request.body)
    entry_flag=ap_data['entry_flag']
    resp_obj = apinvoicehdr_service.apinvoiceheader_update_entry_flag(apinvheader_id,entry_flag,emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_supplierreport(request,supplier_id,apinvheader_id):
    if request.method == 'GET':
        scope = request.scope
        apinward_service=APInvoiceheaderService(scope)
        emp_id = request.employee_id
        subtax_id = request.GET.get('subtax_id')
        response_obj = apinward_service.fetch_supplier_report(request,supplier_id,apinvheader_id,subtax_id, emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response


@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ap_common_summary(request):
    if request.method == 'POST':
        from utilityservice.service import api_service
        ap_data = json.loads(request.body)
        scope = request.scope
        apinvoicehdr_service=APInvoiceheaderService(scope)
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        api_serv = api_service.ApiService(scope)
        emp_id = request.employee_id
        response_obj = apinvoicehdr_service.fetch_ap_common_summary(request,ap_data,vys_page, emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response




@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_approved_apcrno(request, apcrno):
    if request.method == 'GET':
        scope = request.scope
        apinward_service = APInvoiceheaderService(scope)
        emp_id = request.employee_id
        response_obj = apinward_service.fetch_approved_crno(apcrno)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response



@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def view_validation(request,apinvoicehdr_id):
    if request.method == 'GET':
        scope = request.scope
        apinvoicehdr_service = APInvoiceheaderService(scope)
        emp_id = request.employee_id
        preparepayment = request.GET.get('preparepayment', False)
        print('emp_id ',emp_id)
        print('preparepayment ',preparepayment)
        print('Is preparepayment false ',preparepayment == False)
        print('Is preparepayment true  ',preparepayment == 'true')
        print('Is preparepayment  ',type(preparepayment))
        actual_apstatus=[AP_Status.APPROVED,AP_Status.PAY_INITIATE]
        if preparepayment == False:
            apqueue_data=apinvoicehdr_service.maker_as_approver_validation(apinvoicehdr_id,emp_id)
            actual_apstatus = [AP_Status.PENDING_FOR_APPROVAL,AP_Status.AP_INITIATE]
            if apqueue_data != False:
                return HttpResponse(apqueue_data.get(), content_type="application/json")
        #Dynamic Status Validation
        print('actual_apstatus ',actual_apstatus)
        apstatus_validation=apinvoicehdr_service.apstatus_update_validation(apinvoicehdr_id,actual_apstatus)
        if apstatus_validation != False:
            return HttpResponse(apstatus_validation.get(), content_type="application/json")
        # while Successfully Loaded
        success_obj = NWisefinSuccess()
        success_obj.set_status("Success")
        success_obj.set_message("Successfully Loaded")
        response = HttpResponse(success_obj.get(), content_type="application/json")
        return response