import json
from apservice.data.request.paymentrequest import PaymentHeaderRequest
from apservice.service.paymentheaderservice import PreparePapmentService
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_preparepayment(request):
    if request.method == 'POST':
        status_update = request.GET.get('status_update',None)
        scope = request.scope
        ap_data = json.loads(request.body)
        ap_service=PreparePapmentService(scope)
        emp_id = request.employee_id
        if status_update:
            response_obj = ap_service.preparepaymen_status_update(ap_data,emp_id)
        else:
            apinvoiceheader_id=ap_data['payment_dtls'][0]['apinvhdr_id']
            payment_obj = PaymentHeaderRequest(ap_data)
            validation_pvno = ap_service.validation_pvno_using_apinvoiceheader_id(apinvoiceheader_id)
            if validation_pvno:
                error_obj = NWisefinSuccess()
                error_obj.set_status('Duplicate crno')
                error_obj.set_message("This crno's pvno is already exist")
                response = HttpResponse(error_obj.get(), content_type="application/json")
                return response
            response_obj = ap_service.create_paymentheader_and_details(payment_obj,ap_data['payment_dtls'], emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response



@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_payment_and_inward_details(request,crno):
    if request.method == 'GET':
        scope = request.scope
        ap_service=PreparePapmentService(scope)
        emp_id = request.employee_id
        response_obj = ap_service.get_payment_and_inward_details(request, crno,emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response