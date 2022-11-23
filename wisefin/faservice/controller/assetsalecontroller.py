
import json
import traceback
from datetime import datetime

from django.db import transaction
from django.http import HttpResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
import pdfkit
from django.template import loader

from faservice.service.assetdetailsservice import AssetDetailsService
from faservice.service.assetsaleservice import AssetSale
from faservice.service.assettransferservice import AssetTransfer
from faservice.util.FaApiService import FaApiService
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from utilityservice.data.response.nwisefinpage import NWisefinPage
from nwisefin.settings import BASE_DIR, logger
from faservice.data.request.assetidrequest import AssetidRequest
from faservice.service.assetidservice import AssetidService
from faservice.util.fautil_valid import source_valdaition
from faservice.util.fautil import get_sourcetype_list, dictdefault
from utilityservice.data.response.nwisefinerror import NWisefinError as Error
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription,ErrorMessage



@csrf_exempt
@api_view([ 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_assetsale(request):
    scope = request.scope
    if request.method == 'POST':
        assetvalue_filter_json = json.loads(request.body)
        user_id = request.user.id
        emp_service = FaApiService(scope)
        assetsale_serv = AssetSale(scope)
        emp_id=request.employee_id
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        resp_obj = assetsale_serv.get_assetsale_list(vys_page,assetvalue_filter_json,emp_id,request)
        response = HttpResponse(json.dumps(resp_obj,default=dictdefault))
        return response

@api_view([ 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_assetsale(request):
    scope = request.scope
    if request.method == 'POST':
        assetvalue_filter_json = json.loads(request.body)
        user_id = request.user.id
        emp_service = FaApiService(scope)
        assetsale_serv = AssetSale(scope)
        emp_id=request.employee_id
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        resp_obj = assetsale_serv.fetch_assetsale_list(vys_page,assetvalue_filter_json,emp_id,request)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@api_view([ 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_assetsalechecker(request):
    scope = request.scope
    if request.method == 'POST':
        assetvalue_filter_json = json.loads(request.body)
        user_id = request.user.id
        emp_service = FaApiService(scope)
        assetsale_serv = AssetSale(scope)
        emp_id=request.employee_id
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        resp_obj = assetsale_serv.get_assetsalechecker(vys_page,assetvalue_filter_json,emp_id,request)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response





@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_assetsale(request):
    scope = request.scope
    if request.method == 'POST':
        asset_json = json.loads(request.body)
        logger.info('FAL_ASSETSALEMAKE_DATA:{}'.format(asset_json))
        asset_serv = AssetSale(scope)
        user_id = request.user.id
        emp_service = FaApiService(scope)
        emp_id=request.employee_id
        resp_obj = asset_serv.make_assetsale(asset_json, emp_id,request)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def assetsaleapprove(request):
    scope = request.scope
    if request.method == 'POST':
        asset_json = json.loads(request.body)
        logger.info('FAL_ASSETSALE_APPROVE_DATA:{}'.format(asset_json))
        asset_serv = AssetSale(scope)
        user_id = request.user.id
        emp_service = FaApiService(scope)
        emp_id=request.employee_id
        assetdetails_serv=AssetDetailsService(scope)
        list_of_barcode=asset_serv.barcodelist_return(asset_json)

        assetdetails_serv=assetdetails_serv.parentchildvalidation(list_of_barcode)
        if 'valid asset' != assetdetails_serv.status:

            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_ASSETSALE)
            response = HttpResponse(error_obj.get(), content_type="application/json")
            return response

        sale_approver_val = asset_serv.sale_approver_validation(asset_json, emp_id)
        if sale_approver_val is True:
            error_obj = Error()
            error_obj.set_code(ErrorMessage.INVALID_REQUEST)
            error_obj.set_description(ErrorDescription.INVALID_VALUECHANGEAPPROVER)
            response = HttpResponse(error_obj.get(), content_type="application/json")
            return response




        resp_obj = asset_serv.assetsaleapprove(asset_json, emp_id,request)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response



@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def export_fa_invoice_pdf(request,assetsaleheader_id):
    try:
        scope = request.scope
        asset_serv = AssetSale(scope)
        user_id = request.user.id
        emp_service = FaApiService(scope)
        emp_id=request.employee_id
        # respnse_obj = pr_service.get_prpdf(pr_id,emp_id)
        # po_data = json.loads(respnse_obj.get())

        respnse_obj = asset_serv.pdf_data_return(assetsaleheader_id,emp_id,request)
        data = render_to_pdf_fa(respnse_obj)
    except Exception as excep:
        traceback.print_exc()
        error_obj = Error()
        error_obj.set_code(ErrorMessage.INVALID_DATA)
        error_obj.set_description(str(excep))
        response = HttpResponse(error_obj.get(), content_type="application/json")
        return response

    return data


def render_to_pdf_fa(fa_data):
    #template = loader.get_template("fa_template.html")
    if int(fa_data['is_salenote']) == 1:
        templates = loader.get_template("FA_Template_Sale_Note.html")
    elif int(fa_data['is_salenote']) == 0:
        templates = loader.get_template("FA_Template_Sale_Invoice.html")
    fa_json = fa_data
    # print(fa_json)
    #html = template.render(fa_json)
    html = templates.render(fa_json)
    options = {
        'margin-top': '0.25in',
        'margin-right': '0.5in',
        'margin-bottom': '0.75in',
        'margin-left': '0.5in',
        'enable-local-file-access': None,
        'encoding': 'UTF-8',
    }
    pdf = pdfkit.from_string(html, False, options)
    # print("pdf", html)

    if int(fa_data['is_salenote']) == 1:
        gen_filename = 'FA_Sale_Note_PDF'
    elif int(fa_data['is_salenote']) == 0:
        gen_filename = 'FA_Sale_Invoice_PDF'
    file_name=gen_filename + '-(' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ')'
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="{}"'.format(file_name)


    return response