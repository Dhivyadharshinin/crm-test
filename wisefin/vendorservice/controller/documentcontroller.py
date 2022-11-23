import json
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from utilityservice.data.response.nwisefinsuccess import SuccessStatus,SuccessMessage,NWisefinSuccess
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinerror import NWisefinError
from docservice.service.documentservice import DocumentsService
from docservice.util.docutil import DocModule
from userservice.service.employeeservice import EmployeeService
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from django.http import HttpResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from vendorservice.service.documentservice import DocumentService
from vendorservice.data.request.documentrequest import DocumentRequest
from userservice.models import Employee
from vendorservice.models import VendorFileAttachment
from vendorservice.util.vendorutil import VendorRefType
import datetime
import boto3
# from memoservice.models import Documents
from masterservice.service.docugroupservice import DocumentGroupService
from vendorservice.service.vendorservice import VendorService
from django.conf import settings


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def single_document(request, vendor_id):
    if request.method == 'POST':
        scope = request.scope
        document_service = DocumentService(scope)
        document_data = json.loads(request.data.dict().get('data'))
        # logger.info(document_data)
        employee_id = request.employee_id
        document_obj = DocumentRequest(document_data)
        docmodule_obj = DocModule()
        file_id=document_obj.file_id
        logger.info("file_id " + str(document_obj.file_id))
        vendor_service = VendorService(scope)
        mod_status = vendor_service.get_modification_status(vendor_id)
        ref_id=0
        if mod_status is True:
            resp_obj = document_service.modification_create_document(document_obj, employee_id, vendor_id, ref_id)
        else:
            resp_obj = document_service.create_document(document_obj, employee_id, vendor_id, ref_id)
        params = dict()
        params['module'] = docmodule_obj.VENDOR
        params['ref_id']=resp_obj.id
        params['ref_type'] = VendorRefType.VENDOR_DOCUMENT
        tab_type=VendorRefType.VENDOR_DOCUMENT


        try:
            if not request.FILES['file'] is None:
                # if document_obj.id != None :
                #     data = document_service.aws_file_data(file_id)
                #     f_name = data.gen_file_name
                #     logger.info("f_name",f_name)
                #     s3 = boto3.resource("s3")
                #     obj = s3.Object(bucket_name="vysfin-assets-uat",key=f_name )
                #     obj.delete()
                #     logger.info("deleted --")

                file_count = len(request.FILES.getlist('file'))
                doc_service = DocumentsService(scope)
                doc_obj = doc_service.upload(request, params)
                doco_service = DocumentService(scope)
                value = doco_service.document_upload(resp_obj,tab_type,request,doc_obj)


        except KeyError:
            logger.info('No attachment')
            if(file_id != None):
                ref_id = file_id
        id = resp_obj.get_id()
        tab_type = VendorRefType.VENDOR_DOCUMENT
        data_obj = document_service.vendor_file_data(id, tab_type)
        resp_obj.file_id = data_obj
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_document_list(request,vendor_id)


def fetch_document_list(request,vendor_id):
    scope = request.scope
    document_service = DocumentService(scope)
    employee_id = request.employee_id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)

    resp_obj = document_service.fetch_document_list(employee_id,request,vys_page,vendor_id)
    vendor_service = VendorService(scope)
    docu_service = DocumentGroupService(scope)

    x = resp_obj.data
    for i in x:
        id=i.id
        tab_type= VendorRefType.VENDOR_DOCUMENT
        data_obj = document_service.vendor_file_data(id,tab_type)
        i.file_id = data_obj.data

        vendor_id = i.partner_id
        vendor_status = vendor_service.get_vendor_status(vendor_id)
        i.q_modify = False
        if (i.created_by == employee_id):
            if (vendor_status == 0 or vendor_status == 1):
                i.q_modify = True

        # for modification testing
        i.q_modify = True

        docgroup_id = i.docgroup_id
        docugroup = docu_service.fetch_docugroup(docgroup_id)
        i.docgroup_id = docugroup

    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_document(request,vendor_id,document_id):
    scope = request.scope
    branch_code = request.GET.get('code', None)
    if (branch_code is None) or (branch_code == ''):
        pass
    else:
        vendor_service = VendorService(scope)
        vendor_id = vendor_service.get_vendor_code_by_id(branch_code)
        if vendor_id is None:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_DATA)
            response = HttpResponse(error_obj.get(), content_type="application/json")
            return response
    if request.method == 'GET':
        document_service = DocumentService(scope)
        vendor_service=VendorService(scope)
        employee_id = request.employee_id
        resp_obj = document_service.fetch_document(document_id)

        docu_service = DocumentGroupService(scope)
        docgroup_id = resp_obj.docgroup_id
        docugroup = docu_service.fetch_docugroup(docgroup_id)
        resp_obj.docgroup_id = docugroup
        tab_type = VendorRefType.VENDOR_DOCUMENT
        data_obj = document_service.vendor_file_data(document_id, tab_type)
        if resp_obj.modify_status!=2:
            resp_obj.file_id = data_obj.data
        else:
            data_obj1 = document_service.vendor_file_data(resp_obj.modify_ref_id, tab_type)
            fileary=vendor_service.append_doc(data_obj.data,data_obj1.data)
            resp_obj.file_id = fileary


        vendor_service = VendorService(scope)
        vendor_id = resp_obj.partner_id
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
        return delete_document(request,vendor_id,document_id)


@csrf_exempt
def delete_document(request,vendor_id,document_id):
    scope = request.scope
    document_service = DocumentService(scope)
    vendor_service = VendorService(scope)
    employee_id = request.employee_id
    mod_status = vendor_service.get_modification_status(vendor_id)
    if mod_status is True:
        resp_obj = document_service.modification_delete_document(document_id,vendor_id,employee_id)
    else:
        resp_obj = document_service.delete_document(document_id,vendor_id,employee_id)

    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def document(request, vendor_id):
    scope = request.scope
    branch_code = request.GET.get('code', None)
    if (branch_code is None) or (branch_code == ''):
        pass
    else:
        vendor_service = VendorService(scope)
        vendor_id = vendor_service.get_vendor_code_by_id(branch_code)
        if vendor_id is None:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_DATA)
            response = HttpResponse(error_obj.get(), content_type="application/json")
            return response
    if request.method == 'POST':
        document_service = DocumentService(scope)
        document_data = json.loads(request.data.dict().get('data'))
        employee_id = request.employee_id
        vendor_service = VendorService(scope)
        mod_status = vendor_service.get_modification_status(vendor_id)
        docmodule_obj = DocModule()
        document_list = []
        for document in document_data:
            document_obj = DocumentRequest(document)
            attachment = document_obj.attachment
            file_id=document_obj.file_id
            logger.info("file_id "+ str(document_obj.file_id))
            ref_id=0
            if mod_status is True:
                resp_obj = document_service.modification_create_document(document_obj, employee_id, vendor_id, ref_id)
            else:
                resp_obj = document_service.create_document(document_obj, employee_id, vendor_id, ref_id)
            params = dict()
            params['module'] = docmodule_obj.VENDOR
            params['ref_id']=resp_obj.id
            params['ref_type'] = VendorRefType.VENDOR_DOCUMENT
            tab_type=VendorRefType.VENDOR_DOCUMENT
            try:
                if (attachment is not None) or(attachment!=""):
                    if not request.FILES[attachment] is None:
                        attachment = str(attachment)
                        doc_service = DocumentsService(scope)
                        doc_obj = doc_service.multiple_upload(request,params,attachment)
                        doco_service = DocumentService(scope)
                        value = doco_service.multiple_document_upload(resp_obj,tab_type,request,doc_obj,attachment)


            except KeyError:
                logger.info('No attachment')
                if(file_id != None):
                    ref_id = file_id
            id = resp_obj.get_id()
            tab_type = VendorRefType.VENDOR_DOCUMENT
            data_obj = document_service.vendor_file_data(id, tab_type)
            resp_obj.file_id = data_obj
            document_list.append(resp_obj)
        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        response = HttpResponse(success_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_document_list(request,vendor_id)
