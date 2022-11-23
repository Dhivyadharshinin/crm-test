import json
from datetime import datetime
from django.conf import settings
import pdfkit
from django.core.files.base import ContentFile

from django.template import loader
from ecfservice.util.ecfutil import get_ddl_ecf_list, get_Type
from docservice.service.documentservice import DocumentsService
from docservice.util.docutil import DocModule
from ecfservice.data.response.invoiceheaderresponse import Invoiceheaderresponse
from ecfservice.models.ecfmodels import ECFFiles
from ecfservice.service.ecfauditservice import ECFAuditService
from nwisefin.settings import BASE_DIR, logger
# from vysfinutility.service.dbutil import DataBase
from django.http import HttpResponse
from ecfservice.util.ecfutil import get_Type_list, get_Ppx_list, get_Pay_list, get_status_list, get_supplier_list,\
    get_tds_list, get_advancetype, getadvance_list, get_fileextension_val, get_ddl_ecf_list,get_ECF_type   
#test
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
# from wisefinapi.employeeapi import EmployeeAPI
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from ecfservice.data.request.ecfheaderrequest import ECFHeaderrequest
from ecfservice.data.request.invoiceheaderrequest import Invoiceheaderrequest
from ecfservice.data.request.invoiceporequest import Invoiceporequest
from ecfservice.data.request.creditrequest import Creditrequest
from ecfservice.data.request.invoicedetailrequest import Invoicedetailrequest,Debitrequest,ccbsdtlrequest
from ecfservice.service.ecfheaderservice import EcfService
from ecfservice.service.invoiceposervice import InvoicepoService
from ecfservice.service.invoiceheaderservice import InvoiceheaderService
from ecfservice.service.invoicedetailservice import InvoicedetailService
from ecfservice.service.debitservice import DebitService
from ecfservice.service.creditservice import CreditService
# from prservice.service.grninwardservice import GrninwardService
# from userservice.service.employeeservice import EmployeeService
# emp_service = EmployeeAPI()
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.api_service import ApiService
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from ecfservice.data.response.invoiceporesponse import Invoiceporesponse
from ecfservice.data.response.invoicedetailresponse import Invoicedetailresponse,Debitresponse,ccbsdtlresponse
from ecfservice.data.response.creditresponse import Creditresponse
from ecfservice.service.ecfheaderservice import EcfService
#ecfcreate and view


@csrf_exempt
@api_view(['GET','POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])

def create_ecf(request):
    if request.method == 'POST':
        scope = request.scope
        print("rqe",request.body)
        ecf_data = json.loads(request.body)
        ecf_obj = ECFHeaderrequest(ecf_data)
        ecf_service = EcfService(scope)
        emp_id = request.employee_id
        response_obj = ecf_service.ecfcreate(request,ecf_obj, emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response
    elif request.method == 'GET':
        return fetch_ecf_list(request)

def fetch_ecf_list(request):
    scope = request.scope
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    emp_id = request.employee_id
    ecf_service = EcfService(scope)
    response_obj = ecf_service.fetch_ecf_list(request,vys_page, emp_id)
    response = HttpResponse(response_obj.get(), content_type="application/json")
    return response

#ecftypedropdown

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_ecftype(request):
    scope = request.scope
    resp_obj = get_Type_list()
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
#ppxdropdown
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_ppx(request):
    scope = request.scope
    resp_obj = get_Ppx_list()
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

#paytodropdown
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_payto(request,typeid):
    if request.method == 'GET':
        scope = request.scope
        resp_obj = get_Pay_list(typeid)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


#Ecf Submit
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ecf_submit(request):
    if request.method == 'POST':
        ecf_data = json.loads(request.body)
        ecf_obj = ECFHeaderrequest(ecf_data)
        scope = request.scope
        emp_id = request.employee_id
        ecf_service = EcfService(scope)
        response_obj = ecf_service.ECF_Submit(request,ecf_obj, emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response

#ecfheader search
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def search_ecfheader(request):
    if request.method == 'POST':
        ecf_obj = json.loads(request.body)
        scope = request.scope
        emp_id = request.employee_id
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        ecf_service = EcfService(scope)
        resp_obj = ecf_service.fetch_ecf_search(request,ecf_obj,vys_page,emp_id)
        return HttpResponse(resp_obj.get(), content_type='application/json')

#ecfheadersingleget
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetchone_ecfhdr(request, ecf_id):
    if request.method == 'GET':
        scope = request.scope
        emp_id = request.employee_id
        ecf_service = EcfService(scope)
        resp_obj = ecf_service.fetchone_inv_list(request,ecf_id, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_ecf_covernote(request, ecf_id):
    if request.method == 'GET':
        try :
            scope = request.scope
            emp_id = request.employee_id
            #emp_id = 7936
            ecf_service = EcfService(scope)
            resp_obj = ecf_service.fetchone_invoice_pdf_list(request,ecf_id, emp_id)
            ecf_json=json.loads(resp_obj.get())
            print("ecf_json",resp_obj.get())
            image_path = str(BASE_DIR) + "\\ecfservice\\templates\\northern-arclogo.jpg"
            print(image_path)
            ecf_json['img']=image_path
            # Inv_head = ecf_json.pop('Invheader')
            barcodeimage_path = barcode_generate(ecf_json['crno'])
            print("barcode",barcodeimage_path)
            ecf_json['barcodeimage_path'] = barcodeimage_path
            Inv_head = ecf_json.pop('Invheader')
            html = ''
            for record in Inv_head:
                ecf_json['Invheader'] = [record]
                response = render_to_pdf_ecf(ecf_json)
                html+=response
            options = {
                'margin-top': '0.25in',
                'margin-right': '0.5in',
                'margin-bottom': '0.75in',
                'margin-left': '0.5in',
                'enable-local-file-access': None,
                'encoding': 'UTF-8'}
            pdf = pdfkit.from_string(html, False, options)
            gen_filename = str(ecf_json['crno'])
            print("genfile",gen_filename)
            file_name = gen_filename + '-(' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ')'
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename="{}"'.format(file_name)
            return response
        except Exception as excep:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            return error_obj


def render_to_pdf_ecf(ecf_json):
    templates = loader.get_template("ECF_Cover_Note.html")
    html = templates.render(ecf_json)
    return html

#statusdropdown
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_status(request):
    scope = request.scope
    resp_obj = get_status_list()
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_status_ddl(request):
    scope = request.scope
    resp_obj = get_ddl_ecf_list()
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

#Invoiceheadercreate
@transaction.atomic
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_invhdr(request):
    if request.method == 'POST':
        # with transaction.atomic(using=DataBase.ecf_db):
            scope = request.scope
            api_serv = ApiService(scope)
            emp_id = request.employee_id
            rcn_data = json.loads(request.data.dict().get('data'))
            # logger.info("grn data" + str(rcn_data))

            print("json",rcn_data)
            arr = []
            # grn_service = GrninwardService()
            for i in rcn_data:
                header_obj = Invoiceheaderrequest(i)
                invhdr_service = InvoiceheaderService(scope)
                response_obj = invhdr_service.invhdrcreate(request,header_obj, emp_id)
                print("ecfid",response_obj.id)
                print("ecfid",response_obj.totalamount)
                ecfserv=EcfService(scope)
                ecftypeee = ecfserv.fetchone_inv_list(request,response_obj.ecfheader_id,emp_id)
                print("ecftype",ecftypeee.ecftype)
                if ecftypeee.ecftype == "ADVANCE":
                    amount = response_obj.totalamount
                    invtl_data = {"invoiceheader_id":response_obj.id,"unitprice":amount,"amount":amount,"totalamount":amount}
                    invdtl_obj = Invoicedetailrequest(invtl_data)
                    print(invdtl_obj.get_invoiceheader_id())
                    invdtl_service = InvoicedetailService(scope)
                    response_objd = invdtl_service.invdtlcreate(invdtl_obj, emp_id)
                header_id = response_obj.id
                arr.append(response_obj)
                inhdr_data = Invoiceheaderresponse()
                inhdr_data.set_invoiceheader(arr)
                doc_module = 12 ###
                h_file_key = i.get("file_key")
                if not h_file_key is None:
                    for h in h_file_key:
                        if h not in request.FILES:
                            logger.info("grn file key not in fileList" + str(h))
                            print("grn file not in fileList", h)
                            continue
                        logger.info("grn file- key :" + str(h))
                        logger.info("grn fileName :" + str(request.FILES.getlist(h)))
                        file_count=len(request.FILES.getlist(h))
                        flag='po'
                        for j in range(0, file_count):
                            file=request.FILES.getlist(h)[j]
                            file_name=file.name
                            extension = file_name.split('.')[-1]
                            filetype_check = get_fileextension_val(extension)
                            if filetype_check is False:
                                flag='qw'
                                error_obj = NWisefinError()
                                error_obj.set_code(ErrorMessage.INVALID_FILETYPE)
                                error_obj.set_description(ErrorDescription.INVALID_FILETYPE)
                                response = HttpResponse(error_obj.get(), content_type="application/json")
                                return HttpResponse(response, content_type='application/json')
                        if flag!='qw':
                            pass
                            doc_resp_obj = api_serv.doc_upload_ecf(request, doc_module, h)
                            document_json = doc_resp_obj['data']
                            docfl_obj = invhdr_service.upload(document_json,header_id,emp_id)

            response = HttpResponse(inhdr_data.get(),content_type='application/json')
            return response


#Invoicepocreate
@transaction.atomic
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_invpo(request):
    if request.method == 'POST':
        invpo_data = json.loads(request.body)
        scope = request.scope
        emp_id = request.employee_id
        arr=[]
        for i in invpo_data:
            invpo_obj = Invoiceporequest(i)
            invpo_service = InvoicepoService(scope)
            response_obj = invpo_service.invpocreate(invpo_obj, emp_id)
            arr.append(response_obj)
            # print('arr',arr)
        inpo_data = Invoiceporesponse()
        inpo_data.set_invoicepo(arr)
        response = HttpResponse(inpo_data.get(), content_type='application/json')
        return response

#Invoicedetailcreate
@transaction.atomic
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_invoivedtl(request):
    if request.method == 'POST':
        invdtl_data = json.loads(request.body)
        scope = request.scope
        emp_id = request.employee_id
        arr=[]
        for i in invdtl_data:
            invdtl_obj = Invoicedetailrequest(i)
            invdtl_service = InvoicedetailService(scope)
            response_obj = invdtl_service.invdtlcreate(invdtl_obj, emp_id)
            po_id = response_obj.invoice_po
            invdtl_id = response_obj.id
            po_qty=response_obj.quantity
            arr.append(response_obj)
            invpo_service = InvoicepoService(scope)
            response_po = invpo_service.Invpo_update(po_id, invdtl_id, po_qty, emp_id)
            # print('arr',arr)
        indtl_data = Invoicedetailresponse()
        indtl_data.set_invoicedetails(arr)
        response = HttpResponse(indtl_data.get(), content_type='application/json')
        return response

#podropdown
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def po_list(request):
    if request.method =='GET':
        scope = request.scope
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        emp_id = request.employee_id
        invpo_service = InvoicepoService(scope)
        resp_obj=invpo_service.po_list(vys_page,emp_id)
        response=HttpResponse(resp_obj.get(),content_type='application/json')
        return response

#Single pono details
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_ponodtl(request):
    if request.method == 'GET':
        query = request.GET.get('query')
        scope = request.scope
        emp_id = request.employee_id
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        invpo_service = InvoicepoService(scope)
        resp_obj = invpo_service.search_pono_dtl(vys_page,query, emp_id)
        return HttpResponse(resp_obj.get(), content_type='application/json')


#debit & ccbsdtl create
@transaction.atomic
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_debit(request):
    if request.method == 'POST':
        scope = request.scope
        emp_id = request.employee_id
        dbt_data = json.loads(request.body)
        arr=[]
        debitarr=[]
        for i in dbt_data:
            dbt_obj = Debitrequest(i)
            debit_service = DebitService(scope)
            response_obj = debit_service.debitcreate(dbt_obj, emp_id)

            arr.append(response_obj)
            if (response_obj.id != ""):
                debit_id = response_obj.id
                amount=response_obj.amount
                ccbsdtl = i.get("ccbsdtl")
                ccbsdtl_obj = ccbsdtlrequest(ccbsdtl)
                print(ccbsdtl_obj)
                debit_service = DebitService(scope)
                response_obj1 = debit_service.ccbscreate(ccbsdtl_obj, debit_id, emp_id)
                debitarr.append(response_obj)

                deb_data = Debitresponse()
                deb_data.set_debit(arr)
                deb_data.set_ccbs(debitarr)
                response = HttpResponse(deb_data.get(), content_type='application/json')
            else:
                response_obj = NWisefinError()
                response_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
                response_obj.set_description(ErrorDescription.INVALID_REQUEST_ID)
                response =   HttpResponse(response_obj.get(), content_type='application/json')

        return response



#createcreate
@csrf_exempt
@api_view(['GET','POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_credit(request):
    if request.method == 'POST':
        scope = request.scope
        crd_data = json.loads(request.body)
        arr=[]
        for i in crd_data:
            crd_obj = Creditrequest(i)
            emp_id = request.employee_id
            credit_service = CreditService(scope)
            response_obj = credit_service.creditcreate(crd_obj, emp_id)
            arr.append(response_obj)
            # print('arr',arr)
        credit_data = Creditresponse()
        credit_data.set_credit(arr)
        response = HttpResponse(credit_data.get(), content_type='application/json')
        return response

#Invoicepo Update
# @csrf_exempt
# @api_view(['POST'])
# @authentication_classes([VysfinAuthentication])
# @permission_classes([IsAuthenticated, VysfinPermission])
# def update_invpo(request):
#     if request.method == 'POST':
#         ecf_data = json.loads(request.body)
#         ecf_obj = Invoiceporequest(ecf_data)
#         user_id = request.user.id
# from vysfinutility.service import api_service
#         api_serv = api_service.ApiService()
#         emp = api_serv.get_emp_id(request, user_id)
#         emp_id = emp['id']
#         response_obj = invpo_service.Invpo_update(ecf_obj, emp_id)
#         response = HttpResponse(response_obj.get(), content_type='application/json')
#         return response

#ECF Approve
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ecfapprove(request):
    if request.method == 'POST':
        ecf_data = json.loads(request.body)
        ecf_obj = ECFHeaderrequest(ecf_data)
        scope = request.scope
        emp_id = request.employee_id
        ecf_service = EcfService(scope)
        response_obj = ecf_service.status_ECFUpdateApproved(request,ecf_obj, emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response

#ECFNextApproval
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ecfnextapprove(request):
    if request.method == 'POST':
        ecf_data = json.loads(request.body)
        ecf_obj = ECFHeaderrequest(ecf_data)
        scope = request.scope
        emp_id = request.employee_id
        ecf_service = EcfService(scope)
        response_obj = ecf_service.status_ECFNextApprover(request,ecf_data, emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response

#ecfreject
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ecfreject(request):
    if request.method == 'POST':
        pr_data = json.loads(request.body)
        pr_obj = ECFHeaderrequest(pr_data)
        scope = request.scope
        emp_id = request.employee_id
        ecf_service = EcfService(scope)
        response_obj = ecf_service.status_UpdateRejected(request,pr_obj, emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response


#ecfapprovalheader list
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_ecfapproval_list(request):
    if request.method == 'GET':
        scope = request.scope
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        emp_id = request.employee_id
        ecf_service = EcfService(scope)
        response_obj = ecf_service.fetch_approvalecf_list(request,vys_page, emp_id)
        response = HttpResponse(response_obj.get(), content_type="application/json")
        return response

#ecfapprovalheader search
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def search_ecfapprovalheader(request):
    if request.method == 'POST':
        ecf_obj = json.loads(request.body)
        scope = request.scope
        emp_id = request.employee_id
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        ecf_service = EcfService(scope)
        resp_obj = ecf_service.fetch_approvalecf_search(request,ecf_obj,vys_page,emp_id)
        return HttpResponse(resp_obj.get(), content_type='application/json')

#taxcalculation
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_tax(request):
    if request.method == 'POST':
        tax_obj = json.loads(request.body)
        scope = request.scope
        x = tax_obj['code']
        y = x.split("-")
        code = y[0]
        invdtl_service = InvoicedetailService(scope)
        resp_obj = invdtl_service.taxcalculation(tax_obj,code)
        return HttpResponse(resp_obj.get(), content_type='application/json')

#invoicedetail for nonpo,ppx,pettycash
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_invoivedetail(request):
    if request.method == 'POST':
        invdtl_data = json.loads(request.body)
        scope = request.scope
        emp_id = request.employee_id
        arr=[]
        for i in invdtl_data:
            invdtl_obj = Invoicedetailrequest(i)
            invdtl_service = InvoicedetailService(scope)
            response_obj = invdtl_service.invdtlcreate(invdtl_obj, emp_id)
            arr.append(response_obj)

        indtl_data = Invoicedetailresponse()
        indtl_data.set_invoicedetails(arr)
        response = HttpResponse(indtl_data.get(), content_type='application/json')
        return response


#ecf ppx create
@transaction.atomic
@csrf_exempt
@api_view(['GET','POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_ecfppx(request):
    if request.method == 'POST':
        ecf_data = json.loads(request.body)
        ecf_obj = ECFHeaderrequest(ecf_data)
        scope = request.scope
        emp_id = request.employee_id
        ecf_service = EcfService(scope)
        response_ecf = ecf_service.ecfcreate(ecf_obj, emp_id)
        ecf_id=response_ecf.id
        ecf_branchgst =response_ecf.branchgst
        ecf_amt =response_ecf.ecfamount
        invhdr_service = InvoiceheaderService(scope)
        response_inv = invhdr_service.invhdrppx(ecf_id,ecf_branchgst,ecf_amt, emp_id)
        inv_id = response_inv.id
        invdtl_service = InvoicedetailService(scope)
        response_obj = invdtl_service.invdtlppx(inv_id,ecf_amt, emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response

#ecfpayment list
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ecfpayment_list(request,supplier_id,paymode_id):
    if request.method == 'GET':
        scope = request.scope
        query = request.GET.get('query')
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        emp_id = request.employee_id
        credit_service = CreditService(scope)
        response_obj = credit_service.fetch_payment_details(request,vys_page,supplier_id,paymode_id,query, emp_id)
        response = HttpResponse(response_obj.get(), content_type="application/json")
        return response

#invheadersingleget
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetchone_invhdr(request, inv_id):
    if request.method == 'GET':
        scope = request.scope
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        emp_id = request.employee_id
        invhdr_service = InvoiceheaderService(scope)
        resp_obj = invhdr_service.fetchone_inv_list(request, vys_page, inv_id, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

#suppliertypedropdown
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_suppliertype(request):
    scope = request.scope
    resp_obj = get_supplier_list()
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


#invdetailsingleget
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetchone_invdtl(request, invdtl_id):
    if request.method == 'GET':
        scope = request.scope
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        emp_id = request.employee_id
        invdtl_service = InvoicedetailService(scope)
        resp_obj = invdtl_service.fetch_single_invdtl(request,invdtl_id, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
#ecfheaderdelete
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def delete_ecfhdr(request, ecf_id):
    if request.method == 'GET':
        scope = request.scope
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        emp_id = request.employee_id
        ecf_service = EcfService(scope)
        resp_obj = ecf_service.Delete_ecfhdr(request,ecf_id, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

#invhdrdelete
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def delete_invhdr(request, invhdr_id):
    if request.method == 'GET':
        scope = request.scope
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        emp_id = request.employee_id
        invhdr_service = InvoiceheaderService(scope)
        resp_obj = invhdr_service.Delete_invhdr(request,invhdr_id, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

#invdtldelete
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def delete_invdtl(request, invdtl_id):
    if request.method == 'GET':
        scope = request.scope
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        emp_id = request.employee_id
        invdtl_service = InvoicedetailService(scope)
        resp_obj = invdtl_service.Delete_invdtl(request,invdtl_id, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
#debitdelete
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def delete_debit(request, dbt_id):
    if request.method == 'GET':
        scope = request.scope
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        emp_id = request.employee_id
        debit_service = DebitService(scope)
        resp_obj = debit_service.Delete_debit(request,dbt_id, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
#creditdelete
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def delete_credit(request, cdt_id):
    if request.method == 'GET':
        scope = request.scope
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        emp_id = request.employee_id
        credit_service = CreditService(scope)
        resp_obj = credit_service.Delete_credit(request,cdt_id, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

#ecfmodcreate
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_ecfmod(request):
    ecf_data = json.loads(request.body)
    ecf_obj = ECFHeaderrequest(ecf_data)
    scope = request.scope
    emp_id = request.employee_id
    ecf_service = EcfService(scope)
    response_obj = ecf_service.ecfmodcreate(request,ecf_obj, emp_id)
    response = HttpResponse(response_obj.get(), content_type='application/json')
    return response

#Invoiceheadermodcreate
@transaction.atomic
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_invhdrmod(request):
    if request.method == 'POST':
        # with transaction.atomic(using=DataBase.ecf_db):
            scope = request.scope
            api_serv = ApiService(scope)
            emp_id = request.employee_id
            rcn_data = json.loads(request.data.dict().get('data'))
            # logger.info("grn data" + str(rcn_data))

            print("json", rcn_data)
            arr = []
            # grn_service = GrninwardService()
            for i in rcn_data:
                header_obj = Invoiceheaderrequest(i)
                invhdr_service = InvoiceheaderService(scope)
                response_obj = invhdr_service.invhdrcreate(request, header_obj, emp_id)
                header_id = response_obj.id
                arr.append(response_obj)
                inhdr_data = Invoiceheaderresponse()
                inhdr_data.set_invoiceheader(arr)
                doc_module = 13  ###
                h_file_key = i.get("file_key")
                if not h_file_key is None:
                    for h in h_file_key:
                        if h not in request.FILES:
                            logger.info("grn file key not in fileList" + str(h))
                            print("grn file not in fileList", h)
                            continue
                        logger.info("grn file- key :" + str(h))
                        logger.info("grn fileName :" + str(request.FILES.getlist(h)))
                        file_count = len(request.FILES.getlist(h))
                        flag = 'po'
                        for j in range(0, file_count):
                            file = request.FILES.getlist(h)[j]
                            file_name = file.name
                            extension = file_name.split('.')[-1]
                            filetype_check = get_fileextension_val(extension)
                            if filetype_check is False:
                                flag = 'qw'
                                error_obj = NWisefinError()
                                error_obj.set_code(ErrorMessage.INVALID_HEADER_FILETYPE)
                                error_obj.set_description(ErrorDescription.INVALID_HEADER_FILETYPE)
                                response = HttpResponse(error_obj.get(), content_type="application/json")
                                return HttpResponse(response, content_type='application/json')
                        if flag != 'qw':
                            pass
                            doc_resp_obj = api_serv.doc_upload_ecf(request, doc_module, h)
                            document_json = doc_resp_obj['data']
                            docfl_obj = invhdr_service.upload(document_json, header_id, emp_id)
            response = HttpResponse(inhdr_data.get(),content_type='application/json')
            return response
#Invoicepomodcreate
@transaction.atomic
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_invpomod(request):
    if request.method == 'POST':
        invpo_data = json.loads(request.body)
        scope = request.scope
        emp_id = request.employee_id
        for i in invpo_data:
            invpo_obj = Invoiceporequest(i)
            invpo_service = InvoicepoService(scope)
            response_obj = invpo_service.invpomodcreate(invpo_obj, emp_id)
            response = HttpResponse(response_obj.get(), content_type='application/json')
        return response

#Invoicedetailmodcreate
@transaction.atomic
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_invoivedtlmod(request):
    if request.method == 'POST':
        invdtl_data = json.loads(request.body)
        scope = request.scope
        emp_id = request.employee_id
        arr =[]
        for i in invdtl_data:
            invdtl_obj = Invoicedetailrequest(i)
            invdtl_service = InvoicedetailService(scope)
            response_obj = invdtl_service.invdtlmodcreate(invdtl_obj, emp_id)
            po_id = response_obj.invoice_po
            invdtl_id = response_obj.id
            po_qty=response_obj.quantity
            arr.append(response_obj)
            invpo_service = InvoicepoService(scope)
            response_po = invpo_service.Invpo_update(po_id,invdtl_id,po_qty, emp_id)
        indtl_data = Invoicedetailresponse()
        indtl_data.set_invoicedetails(arr)
        response = HttpResponse(indtl_data.get(), content_type='application/json')
        return response

#invoicedetailmod for nonpo,ppx,pettycash
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_invoivedetailmod(request):
    if request.method == 'POST':
        invdtl_data = json.loads(request.body)
        scope = request.scope
        emp_id = request.employee_id
        for i in invdtl_data:
            invdtl_obj = Invoicedetailrequest(i)
            invdtl_service = InvoicedetailService(scope)
            response_obj = invdtl_service.invdtlmodcreate(invdtl_obj, emp_id)
            response = HttpResponse(response_obj.get(), content_type='application/json')
        return response

#debitmod & ccbsdtlmod create
@transaction.atomic
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_debitmod(request):
    if request.method == 'POST':
        scope = request.scope
        emp_id = request.employee_id
        dbt_data = json.loads(request.body)
        arr = []
        debitarr = []
        for i in dbt_data:
            dbt_obj = Debitrequest(i)
            debit_service = DebitService(scope)
            response_obj = debit_service.debitmodcreate(dbt_obj, emp_id)
            arr.append(response_obj)
            if (response_obj.id != ""):
                debit_id = response_obj.id
                amount=response_obj.amount
                ccbsdtl = i.get("ccbsdtl")
                ccbsdtl_obj = ccbsdtlrequest(ccbsdtl)
                print(ccbsdtl_obj)
                debit_service = DebitService(scope)
                response_obj1 = debit_service.ccbscreate(ccbsdtl_obj, debit_id, emp_id)
                debitarr.append(response_obj)
                deb_data = Debitresponse()
                deb_data.set_debit(arr)
                deb_data.set_ccbs(debitarr)
                response = HttpResponse(deb_data.get(), content_type='application/json')
            else:
                response_obj = NWisefinError()
                response_obj.set_code(ErrorMessage.INVALID_REQUEST_ID)
                response_obj.set_description(ErrorDescription.INVALID_REQUEST_ID)
                response = HttpResponse(response_obj.get(), content_type='application/json')
        return response

#creditcreatemod
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_creditmod(request):
    if request.method == 'POST':
        crd_data = json.loads(request.body)
        scope = request.scope
        arr = []
        for i in crd_data:
            crd_obj = Creditrequest(i)
            emp_id = request.employee_id
            credit_service = CreditService(scope)
            response_obj = credit_service.creditmodcreate(crd_obj, emp_id)
            arr.append(response_obj)
            # print('arr',arr)
        credit_data = Creditresponse()
        credit_data.set_credit(arr)
        response = HttpResponse(credit_data.get(), content_type='application/json')
        return response

#suppliertds
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_suptds(request, supplier_id):
    if request.method == 'GET':
        scope = request.scope
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        emp_id = request.employee_id
        credit_service = CreditService(scope)
        resp_obj = credit_service.fetch_suppliertds(request,supplier_id, emp_id)
        response = HttpResponse(json.dumps(resp_obj))
        return response
#tdstaxrate
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_tdstaxrate(request):
    if request.method == 'GET':
        scope = request.scope
        vendor_id = request.GET.get('vendor_id')
        subtax_id = request.GET.get('subtax_id')
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        emp_id = request.employee_id
        credit_service = CreditService(scope)
        resp_obj = credit_service.fetch_taxrate(request,vendor_id,subtax_id,emp_id)
        response = HttpResponse(json.dumps(resp_obj))
        return response

#tdstaxrate
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_ratecal(request, creditamount,tdsamt):
    if request.method == 'GET':
        scope = request.scope
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        emp_id = request.employee_id
        credit_service = CreditService(scope)
        response_obj = credit_service.fetch_ratecal(request,creditamount,tdsamt, emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response

#tdsdropdown
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_tds(request):
    scope = request.scope
    resp_obj = get_tds_list()
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


#overall creation ecf:
@transaction.atomic
@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_ecfheader(request):
    if request.method == 'POST':
        ecf_data = json.loads(request.body)
        ecf_obj = ECFHeaderrequest(ecf_data)
        scope = request.scope
        emp_id = request.employee_id
        print("c1")
        invheader = []
        invdetail = []
        debit = []
        ccbs = []
        ecf_service = EcfService(scope)
        resp_obj = ecf_service.ecfccreate(request,ecf_obj, emp_id)
        print("ecfheader",resp_obj.__dict__)
        ecf_id = resp_obj.id
        print("ecf_id", ecf_id)
        a = ecf_data.get("InvoiceHeaders")
        for pr in a:
            invhdr_obj = Invoiceheaderrequest(pr)
            invhdr_service = InvoiceheaderService(scope)
            resp_obj1 = invhdr_service.invhdrccreate(request,pr.get("file_data"),invhdr_obj,ecf_id, emp_id)
            print("invoiceheader",resp_obj1.__dict__)
            invhdr_id = resp_obj1.id
            invheader.append(invhdr_id)
            b = pr.get("Invoicedetails")
            for i in b:
                invdtl_obj = Invoicedetailrequest(i)
                invdtl_service = InvoicedetailService(scope)
                resp_obj2 = invdtl_service.invdtlccreate(invdtl_obj,invhdr_id, emp_id)
                invdtl_id = resp_obj2.id
                print("Invoicedetails",resp_obj2.__dict__)
                invdetail.append(invdtl_id)
                c = i.get("Debits")
                for y in c:
                    dbt_obj = Debitrequest(y)
                    debit_service = DebitService(scope)
                    resp_obj3 = debit_service.debitccreate(dbt_obj,invdtl_id, emp_id)
                    debit_id = resp_obj3.id
                    debit.append(debit_id)
                    print("debits",resp_obj3.__dict__)
                    d = y.get("Ccbs")
                    for k in d:
                        ccbsdtl_obj = ccbsdtlrequest(k)
                        print(ccbsdtl_obj)
                        debit_service = DebitService(scope)
                        resp_obj4 = debit_service.ccbsccreate(ccbsdtl_obj,debit_id, emp_id)
                        print("ccbs",resp_obj4.__dict__)
                        ccbs_id = resp_obj4.id
                        ccbs.append(ccbs_id)
            a = pr.get("Credit")
            for f in a:
                print("cccred",ccbs)
                crd_obj = Creditrequest(f)
                print("cred",crd_obj.__dict__)
                credit_service = CreditService(scope)
                resp_obj5 = credit_service.creditccreate(crd_obj,invhdr_id, emp_id)
                print("credit",resp_obj5.__dict__)
        ecf_obj = ECFHeaderrequest(ecf_data)
        ecf_service = EcfService(scope)
        response_obj = ecf_service.ECFF_Submit(request, ecf_obj,ecf_id, emp_id)
        print("final",response_obj.__dict__)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response




def barcode_generate(crno):
    import barcode
    from io import BytesIO
    from barcode.writer import ImageWriter
    import base64
    buffer = BytesIO()
    ean = barcode.get('Code128', str(crno), writer=ImageWriter())
    #ean.save(buffer)
    image = ean.render()  # Returns PIL image class
    buffer.seek(0)

    #+str("/ecfservice/templates") BASE_DIR
    #settings.MEDIA_ROOT
    #image.save(settings.MEDIA_ROOT, format="png")  # dunno if your library can do that.
    #img_str = BASE_DIR + str(buffer)+'.png'
    #img_str = base64.b64encode(buffer.read()).decode('utf-8')
    # image = image.save(f"{settings.MEDIA_ROOT}.png")

    #img_path=settings.MEDIA_ROOT+str(datetime.now().strftime("%y%m%d_%H%M%S"))
    img_path=settings.MEDIA_ROOT
    print(f"{img_path}.png")
    image = image.save(f"{img_path}.png")
    image_path=f"{img_path}.png"




    # EAN = barcode.get_barcode_class('Code128')
    # concat_filename =  str(crno) + "_" + str(datetime.now().strftime("%y%m%d_%H%M%S")) + ".png"
    # #save_file = str(create_by) + "_" + str(ecf_no) + "_" + "ecf_barcode"
    # tmp = tempfile.NamedTemporaryFile()
    # with open(tmp.name, 'wb') as f:
    #     EAN(crno, writer=ImageWriter()).write(f)
    # with open(tmp.name, 'rb') as f:
    #     contents = f.read()
    # s3 = boto3.resource('s3')
    # bucket_name = settings.BUCKET_NAME_FOR_ASSETS
    # logger.info('Bucket Name ' + str(bucket_name))
    # s3_obj = s3.Object(bucket_name=bucket_name, key=concat_filename)
    # s3_obj.put(Body=contents)
    # logger.info('s3_obj ' + str(s3_obj))
    # s3_client = boto3.client('s3', 'ap-south-1')
    # logger.info('s3_client ' + str(s3_client))
    # response = s3_client.generate_presigned_url('get_object',
    #                                             Params={'Bucket': bucket_name,
    #                                                     'Key': concat_filename},
    #                                             ExpiresIn=3600)


    return image_path


#OVERALLget
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_ecf(request, ecf_id):
    if request.method == 'GET':
        scope = request.scope
        emp_id = request.employee_id
        ecf_service = EcfService(scope)
        resp_obj = ecf_service.fetch_ecf(request, ecf_id, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

#ecfpaymode for pettycash
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ecfpaymode(request,paymode_id):
    if request.method == 'GET':
        scope = request.scope
        query = request.GET.get('query')
        emp_id = request.employee_id
        credit_service = CreditService(scope)
        response_obj = credit_service.paymode(request,paymode_id,emp_id)
        print("res",response_obj)
        response = HttpResponse(response_obj, content_type="application/json")
        return response

#OVERALLget Based on number
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_ecfno(request, ecf_no):
    if request.method == 'GET':
        scope = request.scope
        emp_id = request.employee_id
        query = request.GET.get('query')
        ecf_service = EcfService(scope)
        resp_obj = ecf_service.fetch_ecfno(request, ecf_no, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

#advancetypedropdown
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_advancetype(request):
    scope = request.scope
    resp_obj = getadvance_list()
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_ecfadv_covernote(request, ecf_id):
    if request.method == 'GET':
        try :
            scope = request.scope
            emp_id = request.employee_id
            #emp_id = 7936
            ecf_service = EcfService(scope)
            resp_obj = ecf_service.fetchone_invoiceadv_pdf_list(request,ecf_id, emp_id)
            ecf_json=json.loads(resp_obj.get())
            print("ecf_json",resp_obj.get())
            image_path = str(BASE_DIR) + "/ecfservice/templates/northern-arclogo.jpg"

            ecf_json['img']=image_path

            barcodeimage_path = barcode_generate(ecf_json['crno'])
            ecf_json['barcodeimage_path'] = barcodeimage_path
            response = render_to_pdfadv_ecf(ecf_json)


            return response
        except Exception as excep:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(str(excep))
            response = HttpResponse(error_obj.get(), content_type="application/json")
            return response


def render_to_pdfadv_ecf(ecf_json):
    templates = loader.get_template("ECF_Covernote_Advance.html")
    html = templates.render(ecf_json)
    options = {
        'margin-top': '0.25in',
        'margin-right': '0.5in',
        'margin-bottom': '0.75in',
        'margin-left': '0.5in',
        'enable-local-file-access': None,
        'encoding': 'UTF-8' }
    pdf = pdfkit.from_string(html, False, options)
    gen_filename = str(ecf_json['crno'])
    file_name=gen_filename + '-(' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ')'
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="{}"'.format(file_name)
    return response

#dropdown show hide
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def employe_role_get(request):
    scope = request.scope
    emp_id = request.employee_id
    emp_role = ECFAuditService(scope)
    resp_obj=emp_role.employee_role(request,emp_id)
    response = HttpResponse(json.dumps(resp_obj), content_type="application/json")
    return response

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

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def view_file(request, file_id):
    scope = request.scope
    logger.info("view file Id" + str(file_id))
    doc_service = DocumentsService(scope)
    response = doc_service.file_download(file_id, request)
    return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def delete_file(request,file_id):
    scope = request.scope
    emp_id = request.employee_id
    ecf_service = EcfService(scope)
    resp_obj = ecf_service.Delete_ecffiles(request,file_id,emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

#OVERALLget Based on number
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_ecfnoo(request, ecf_no):
    if request.method == 'GET':
        scope = request.scope
        emp_id = request.employee_id
        query = request.GET.get('query')
        ecf_service = EcfService(scope)
        resp_obj = ecf_service.fetch_ecfnoo(request, ecf_no, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_ecftypesingle(request,ecftype_id):
    resp_obj = get_Type(int(ecftype_id))
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_status_ddl(request):
    resp_obj = get_ddl_ecf_list()
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

# GSTTYPE
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ds(request,No,branch_id):
    scope = request.scope
    emp_id = request.employee_id
    ecf_service = EcfService(scope)
    resp_obj = ecf_service.ds(request,No,branch_id)
    response = HttpResponse(resp_obj.get(), content_type='application/json')
    return response

#COMMON ECF
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_ecf_common_summary(request):
    if request.method == 'GET':
        page = request.GET.get('page', 1)
        status = request.GET.get('status')
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        user_id = request.user.id
        from utilityservice.service import api_service
        scope = request.scope
        api_serv = api_service.ApiService(scope)
        emp = api_serv.get_emp_id(request, user_id)
        emp_id = emp['id']
        ecf_serv = EcfService(scope)
        response_obj = ecf_serv.fetch_ecf_list_common_smmary(request,vys_page, emp_id,status)
        response = HttpResponse(response_obj.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_apstatus(request):
    if request.method=='POST':
        scope = request.scope
        arrobj=json.loads(request.body)
        emp_id = request.employee_id
        aps = ECFHeaderrequest(arrobj)
        ecf_serv = EcfService(scope)
        apstatus = ecf_serv.apstat(aps,emp_id)
        response = HttpResponse(apstatus.get(), content_type="application/json")
        return response