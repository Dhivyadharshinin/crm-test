import json
from django.http import HttpResponse, JsonResponse
from reportlab.pdfgen import canvas
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt

from nwisefin.settings import logger
from reportservice.service.vendorstatementservice import VendorstatementService
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_vendorstatement(request):
    if request.method == 'POST':
        try:
            scope = request.scope
            vendorsate_service = VendorstatementService(scope)
            vendor_data = json.loads(request.body)
            Type = request.GET.get('Type')
            supplier_id = vendor_data['supplier_id']
            from_date = vendor_data['from_date']
            page_number = vendor_data['page_number']
            page_size = vendor_data['page_size']
            limit = page_size
            offset = page_number * page_size
            resp_obj = vendorsate_service.fetch_vendorstatementservice(supplier_id, from_date, limit, offset, Type,
                                                                       scope)
            return JsonResponse(resp_obj, safe=False)
        except Exception as e:
            return JsonResponse({"Message": "ERROR_OCCURED_ON_VENDOR_STATEMENT_API_", "DATA": str(e)})


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def download_vendorstatement(request):
    if request.method == 'GET':
        try:
            scope = request.scope
            vendorsate_service = VendorstatementService(scope)
            supplier_id = int(request.GET.get('supplier_id'))
            from_date = request.GET.get('from_date')
            resp_obj = vendorsate_service.download_vendorstatementservice(supplier_id,from_date,scope)
            XLSX_MIME = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            response = HttpResponse(resp_obj, content_type=XLSX_MIME)
            response['Content-Disposition'] = 'attachment; filename="EXCEL_report.xlsx"'
            return response
        except Exception as e:
            return JsonResponse({"Message": "ERROR_OCCURED_ON_VENDOR_STATEMENT_API_", "DATA": str(e)})


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def vendorstatement_eod(request):
    if request.method == 'POST':
        try:
            scope = request.scope
            param_details = json.loads(request.body)
            data = param_details['report_id'][0]
            emp_id = request.employee_id
            obj = []
            if data['operators'] == 'DATE BETWEEN' and data['scheduler'] == 1:
                i = {'value1date': data['value1date'],
                     'value2date': data['value2date'],
                     'master': 1}
                obj.append(i)
                logger.info('Scheduler Starts')
                vendornew = VendorstatementService(scope)
                new = vendornew.vendoreod(scope, emp_id, obj, data)
                return new
        except Exception as e:
            return JsonResponse({"Message": "ERROR_OCCURED_ON_VENDOR_STATEMENT_API_", "DATA": str(e)})

# @api_view(['GET'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def export_fa_invoice_pdf(request,assetsaleheader_id):
#     try:
#         scope = request.scope
#         asset_serv = AssetSale(scope)
#         user_id = request.user.id
#         emp_service = FaApiService(scope)
#         emp_id=request.employee_id
#         # respnse_obj = pr_service.get_prpdf(pr_id,emp_id)
#         # po_data = json.loads(respnse_obj.get())
#
#         respnse_obj = asset_serv.pdf_data_return(assetsaleheader_id,emp_id,request)
#         data = render_to_pdf_fa(respnse_obj)
#     except Exception as excep:
#         traceback.print_exc()
#         error_obj = Error()
#         error_obj.set_code(ErrorMessage.INVALID_DATA)
#         error_obj.set_description(str(excep))
#         response = HttpResponse(error_obj.get(), content_type="application/json")
#         return response
#
#     return data
