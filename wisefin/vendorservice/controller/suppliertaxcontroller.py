import json

from django.http import HttpResponse , StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from docservice.util.docutil import DocModule
from docservice.service.documentservice import DocumentsService
from vendorservice.service.documentservice import DocumentService as vendordocument
from userservice.service.employeeservice import EmployeeService
from vendorservice.util.vendorutil import VendorRefType
from vendorservice.data.request.suppliertaxrequest import TaxRequest
from vendorservice.service.suppliertaxservice import TaxService
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from masterservice.service.taxservice import TaxMasterService
from masterservice.service.subtaxservice import SubTaxService
from masterservice.service.taxrateservice import TaxRateService
import datetime
import boto3
# from memoservice.models import Documents
from vendorservice.models import VendorFileAttachment, SupplierTax
from vendorservice.service.documentservice import DocumentService
from vendorservice.service.branchservice import branchservice
from vendorservice.controller.vendorcontroller import VendorService
from django.conf import settings
from django.db import transaction
from vendorservice.util.vendormandatory import VendorMandatory
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage


@transaction.atomic
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
#vendor_id
def suppliertax(request,branch_id):
    if request.method == 'POST':
        employee_id = request.employee_id
        scope = request.scope
        tax_data=json.loads(request.data.dict().get('data'))
        tax_obj=TaxRequest(tax_data)
        vendor_mand = VendorMandatory()
        tax_validate = vendor_mand.suppliertax(tax_obj)
        if tax_validate['checker'] == False:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(tax_validate['response'])
            return HttpResponse(error_obj.get(), content_type="application/json")
        file_id = tax_obj.attachment
        tax_service = TaxService(scope)
        docmodule_obj = DocModule()
        # logger.info(ref_id)
        vendor_service = VendorService(scope)
        # vendor_id = tax_service.get_vendor_id(branch_id)
        mod_status = vendor_service.get_modification_status(branch_id)
        ref_id=0
        if mod_status is True:
            resp_obj = tax_service.modification_create_suppliertax(tax_obj ,branch_id, employee_id, ref_id,branch_id)
        else:
            resp_obj = tax_service.create_suppliertax(tax_obj,branch_id, employee_id,ref_id,branch_id)
        params = dict()
        params['module'] = docmodule_obj.VENDOR
        params['ref_id'] = resp_obj.id
        params['ref_type'] = VendorRefType.VENDOR_SUPPLIERTAX
        tab_type = VendorRefType.VENDOR_SUPPLIERTAX

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
                # for i in range(0, file_count):
                doc_service = DocumentsService(scope)
                doc_obj = doc_service.upload(request, params)
                doco_service = DocumentService(scope)
                value = doco_service.document_upload(resp_obj, tab_type, request, doc_obj)

                    # file = request.FILES.getlist('file')[i]
                    # file_name = file.name
                    # file_name_new = 'memo_' + str(
                    #     datetime.datetime.now().strftime("%y%m%d_%H%M%S")) + file_name
                    # contents = file
                    # s3 = boto3.resource('s3')
                    # s3_obj = s3.Object(bucket_name=settings.BUCKET_NAME_FOR_ASSETS, key=file_name_new)
                    # s3_obj.put(Body=contents)
                    # doc = VendorFileAttachment()
                    # doc.representtabel_id = resp_obj.get_id()
                    # doc.tab_type = VendorRefType.VENDOR_SUPPLIERTAX
                    # doc.file_name = file.name
                    # doc.gen_file_name = file_name_new
                    # doc.save()

        except KeyError:
            logger.info('No attachment')
            if(file_id != None):
                ref_id = file_id
        id = resp_obj.get_id()
        tab_type = VendorRefType.VENDOR_DOCUMENT
        doc_serv = vendordocument(scope)
        data_obj = doc_serv.vendor_file_data(id, tab_type)
        resp_obj.file_id = data_obj
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_suppliertax_list(request,branch_id)


def fetch_suppliertax_list(request, vendor_id):
    employee_id = request.employee_id
    scope = request.scope
    director_service = TaxService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = director_service.fetch_suppliertax_list(request, vys_page,employee_id,vendor_id)
    document_service = DocumentService(scope)
    branch_service = branchservice(scope)
    taxmaster_service = TaxMasterService(scope)
    subtax_service = SubTaxService(scope)
    taxrate_service = TaxRateService(scope)

    x = resp_obj.data
    for i in x:
        id = i.id
        tab_type = VendorRefType.VENDOR_SUPPLIERTAX
        data_obj = document_service.vendor_file_data(id, tab_type)
        if len(data_obj.data) != 0:
            i.attachment = data_obj.data
        else:
            i.attachment = None

        supplierbranch_id = i.vendor_id
        # supplierbranch = branch_service.fetch_branch(supplierbranch_id)
        # i.branch_id = supplierbranch

        tax1_id = i.tax
        if tax1_id!=-1:
            tax = taxmaster_service.fetch_tax(tax1_id, employee_id)
            i.tax = tax
        subtax_id = i.subtax
        if subtax_id!=-1:
            subtax = subtax_service.fetch_subtax(subtax_id, employee_id)
            i.subtax = subtax
        if i.taxrate == 0:
            i.taxrate = None
        else:
            taxrate_id = i.taxrate
            taxrate = taxrate_service.fetch_taxrate(taxrate_id, employee_id)
            i.taxrate = taxrate

        # tax_id = i.id
        # tax = taxmaster_service.fetch_tax(tax_id, user_id)
        # i.tax = tax

        vendor_status = director_service.get_vendorstatus_tax(supplierbranch_id)
        i.q_modify = False
        if (i.created_by == employee_id):
            if (vendor_status == 0 or vendor_status == 1):
                i.q_modify = True
        # modification
        # i.q_modify = True

    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_suppliertax(request, branch_id, tax_id):
    if request.method == 'GET':
        employee_id = request.employee_id
        scope = request.scope
        tax_service = TaxService(scope)
        taxmaster_service=TaxMasterService(scope)
        subtax_service=SubTaxService(scope)

        taxrate_service=TaxRateService(scope)
        resp_obj = tax_service.fetch_suppliertax(tax_id)

        tax1_id = resp_obj.tax
        tax = taxmaster_service.fetch_tax(tax1_id, employee_id)
        resp_obj.tax = tax
        subtax_id = resp_obj.subtax
        subtax = subtax_service.fetch_subtax(subtax_id, employee_id)
        resp_obj.subtax = subtax
        if resp_obj.taxrate==0:
            resp_obj.taxrate = None
        else:
            taxrate_id = resp_obj.taxrate
            taxrate = taxrate_service.fetch_taxrate(taxrate_id, employee_id)
            resp_obj.taxrate = taxrate


        document_service = DocumentService(scope)
        vendor_service=VendorService(scope)


        tab_type = VendorRefType.VENDOR_SUPPLIERTAX
        data_obj = document_service.vendor_file_data(tax_id, tab_type)
        if resp_obj.modify_status != 2:
            if len(data_obj.data) != 0:
                resp_obj.attachment = data_obj.data
            else:
                resp_obj.attachment = None
        else:
            data_obj1 = document_service.vendor_file_data(resp_obj.modify_ref_id, tab_type)
            fileary = vendor_service.append_doc(data_obj.data, data_obj1.data)
            if len(fileary) != 0:
                resp_obj.attachment = fileary
            else:
                resp_obj.attachment = None




        # branch_service = branchservice()
        supplierbranch_id = resp_obj.vendor_id
        vendor_status = tax_service.get_vendorstatus_tax(supplierbranch_id)
        resp_obj.q_modify = False
        if (resp_obj.created_by == employee_id):
            if (vendor_status == 0 or vendor_status == 1):
                resp_obj.q_modify = True

        #modification
        resp_obj.q_modify = True

        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_suppliertax(request, branch_id, tax_id)


def delete_suppliertax(request, branch_id, tax_id):
    employee_id = request.employee_id
    scope = request.scope
    tax_service = TaxService(scope)
    vendor_service = VendorService(scope)
    vendor_id = tax_service.get_vendor_id(branch_id)
    mod_status = vendor_service.get_modification_status(vendor_id)
    if mod_status is True:
        resp_obj = tax_service.modification_delete_suppliertax( tax_id,employee_id,vendor_id,branch_id)
    else:
        resp_obj = tax_service.delete_suppliertax(tax_id, employee_id,vendor_id,branch_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def supplier_tax(request, vendor_id):
    employee_id = request.employee_id
    scope = request.scope
    director_service = TaxService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = director_service.fetch_suppliertax_list(request, vys_page,employee_id,vendor_id)
    document_service = DocumentService(scope)
    branch_service = branchservice(scope)
    taxmaster_service = TaxMasterService(scope)
    subtax_service = SubTaxService(scope)
    taxrate_service = TaxRateService(scope)

    x = resp_obj.data
    for i in x:
        # id = i.id
        # tab_type = VendorRefType.VENDOR_SUPPLIERTAX
        # data_obj = document_service.vendor_file_data(id, tab_type)
        # if len(data_obj.data) != 0:
        #     i.attachment = data_obj.data
        # else:
        #     i.attachment = None
        #
        supplierbranch_id = i.vendor_id
        # supplierbranch = branch_service.fetch_branch(supplierbranch_id)
        # i.branch_id = supplierbranch

        tax1_id = i.tax
        if tax1_id!=-1:
            tax = taxmaster_service.fetch_tax(tax1_id, employee_id)
            i.tax = tax
            taxname = i.tax.name

        subtax_id = i.subtax
        if subtax_id!=-1:
            subtax = subtax_service.fetch_subtax(subtax_id, employee_id)
            i.subtax = subtax
            subtax_name = subtax.name

        isTDSExempt = i.isexcempted  # TDS_Exempt

        if i.taxrate == 0:
            i.taxrate = None
            taxRate = None          # Tax_Rate
        else:
            taxrate_id = i.taxrate
            taxrate = taxrate_service.fetch_taxrate(taxrate_id, employee_id)
            i.taxrate = taxrate
            # taxRate = i.taxrate.rate  # Tax_Rate

        # tax_id = i.id
        # tax = taxmaster_service.fetch_tax(tax_id, user_id)
        # i.tax = tax

        vendor_status = director_service.get_vendorstatus_tax(supplierbranch_id)
        i.q_modify = False
        if (i.created_by == employee_id):
            if (vendor_status == 0 or vendor_status == 1):
                i.q_modify = True
        # modification
        # i.q_modify = True
        print(i)

    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

#subtax getlist
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_subtaxlist(request):
    subtax_ids = json.loads(request.body)
    scope = request.scope
    supplier_tax_serv = TaxService(scope)
    response = supplier_tax_serv.fetch_subtaxlist(subtax_ids)
    # subtax_id2 = subtax_ids['vendor_id']
    # obj = SupplierTax.objects.filter(vendor_id__in=subtax_id2).values('id', 'branch_id','vendor_id','subtax_id')
    # subtax_list_data = NWisefinList()
    # for i in obj:
    #     data = {"id": i['id'], "branch_id": i['branch_id'],"vendor_id": i['vendor_id'],"subtax_id":i['subtax_id']}
    #     subtax_list_data.append(data)
    return HttpResponse(response, content_type='application/json')
