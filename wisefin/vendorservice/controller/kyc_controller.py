import json
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from rest_framework.permissions import IsAuthenticated
from vendorservice.service.kyc_service import KYCService
from vendorservice.data.request.kyc_request import KYCRequest
from nwisefin.settings import logger
from docservice.util.docutil import DocModule
from vendorservice.service.vendorservice import VendorService
from vendorservice.util.vendorutil import VendorRefType
from docservice.service.documentservice import DocumentsService
from utilityservice.data.response.nwisefinsuccess import SuccessStatus,SuccessMessage,NWisefinSuccess
from django.http import HttpResponse
from utilityservice.data.response.nwisefinpage import NWisefinPage

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def kyc_create(request, vendor_id):
    if request.method == 'POST':
        scope = request.scope
        kyc_service = KYCService(scope)
        kyc_data = request.data.dict().get('kyc_details')
        kyc_json = json.loads(kyc_data)
        employee_id = request.employee_id
        docmodule_obj = DocModule()
        vendor_service = VendorService(scope)
        mod_status = vendor_service.get_modification_status(vendor_id)
        kyc_list = []
        for kyc in kyc_json:
            kyc_obj = KYCRequest(kyc)
            file_id = kyc_obj.report_file_id
            logger.info("report_file_id" + str(file_id))
            ref_id=0
            if mod_status is True:
                resp_obj = kyc_service.create_kyc_modification(vendor_id,kyc_obj,employee_id)
            else:
                resp_obj = kyc_service.create_kyc(vendor_id,kyc_obj,employee_id)
            params = dict()
            params['module'] = docmodule_obj.VENDOR
            params['ref_id'] = resp_obj.id
            params['ref_type'] = VendorRefType.VENDOR_KYC
            tab_type = VendorRefType.VENDOR_KYC
            file_val = str(kyc_json.index(kyc))
            try:
                if not request.FILES[file_val] is None:
                    doc_service = DocumentsService(scope)
                    doc_obj = doc_service.multiple_upload(request, params, file_val)
                    value = kyc_service.multiple_document_upload(resp_obj,tab_type,request,doc_obj,file_val)

            except KeyError:
                logger.info('No attachment')
            id = resp_obj.get_id()
            tab_type = VendorRefType.VENDOR_KYC
            data_obj = kyc_service.vendor_file_data(id, tab_type)
            resp_obj.report_file_id = data_obj
            kyc_list.append(resp_obj)
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        response = HttpResponse(success_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_kyc_list(request,vendor_id)


def fetch_kyc_list(request, vendor_id):
    scope = request.scope
    kyc_service = KYCService(scope)
    employee_id = request.employee_id
    page = request.GET.get('page',1)
    page = int(page)
    vys_page = NWisefinPage(page,10)
    resp_obj = kyc_service.fetch_kyc_list(request, vys_page, vendor_id)
    response = HttpResponse(resp_obj.get(),content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_kyc(request,vendor_id,kyc_id):
    if request.method == 'GET':
        scope = request.scope
        kyc_service = KYCService(scope)
        vendor_service = VendorService(scope)
        employee_id = request.employee_id
        resp_obj = kyc_service.fetch_kyc(kyc_id,employee_id)
        tab_type = VendorRefType.VENDOR_KYC
        data_obj = kyc_service.vendor_file_data(kyc_id, tab_type)
        if resp_obj.modify_status != 2:
            resp_obj.report_file_id = data_obj.data
        else:
            data_obj1 = kyc_service.vendor_file_data(resp_obj.modify_ref_id, tab_type)
            fileary = vendor_service.append_doc(data_obj.data, data_obj1.data)
            resp_obj.report_file_id = fileary

        vendor_id = resp_obj.vendor_id
        vendor_status = vendor_service.get_vendor_status(vendor_id)
        resp_obj.q_modify = False
        if (resp_obj.created_by == employee_id):
            if (vendor_status == 0 or vendor_status == 1):
                resp_obj.q_modify = True

        # for modification testing
        resp_obj.q_modify = True

        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

    elif request.method == 'DELETE':
        resp_data = kyc_delete(request, vendor_id,kyc_id)
        return resp_data


def kyc_delete(request, vendor_id,kyc_id):
    scope = request.scope
    employee_id = request.employee_id
    kyc_service = KYCService(scope)
    vendor_service = VendorService(scope)
    mod_status = vendor_service.get_modification_status(vendor_id)
    if mod_status is True:
        kyc_obj = kyc_service.modification_delete_kyc(vendor_id, kyc_id, employee_id)
    else:
        kyc_obj = kyc_service.delete_kyc(vendor_id, kyc_id, employee_id)
    response = HttpResponse(kyc_obj.get(), content_type="application/json")
    return response
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def kyc(request, vendor_id):
    if request.method == 'POST':
        scope = request.scope
        kyc_service = KYCService(scope)
        kyc_data = request.data.dict().get('data')
        kyc_json = json.loads(kyc_data)
        employee_id = request.employee_id
        docmodule_obj = DocModule()
        vendor_service = VendorService(scope)
        mod_status = vendor_service.get_modification_status(vendor_id)
        kyc_obj = KYCRequest(kyc_json)
        file_id = kyc_obj.report_file_id
        logger.info("report_file_id" + str(file_id))
        ref_id=0
        if mod_status is True:
            resp_obj = kyc_service.create_kyc_modification(vendor_id,kyc_obj,employee_id)
        else:
            resp_obj = kyc_service.create_kyc(vendor_id,kyc_obj,employee_id)
        params = dict()
        params['module'] = docmodule_obj.VENDOR
        params['ref_id'] = resp_obj.id
        params['ref_type'] = VendorRefType.VENDOR_KYC
        tab_type = VendorRefType.VENDOR_KYC

        try:
            if not request.FILES['file'] is None:
                doc_service = DocumentsService(scope)
                doc_obj = doc_service.upload(request, params)
                value = kyc_service.document_upload(resp_obj,tab_type,request,doc_obj)

        except KeyError:
            logger.info('No attachment')
        id = resp_obj.get_id()
        tab_type = VendorRefType.VENDOR_KYC
        data_obj = kyc_service.vendor_file_data(id, tab_type)
        resp_obj.report_file_id = data_obj
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
