import json
from apservice.data.request.apinvoicedetailrequest import APccbsDetailsRequest
from apservice.service.apinvoicedetailsservice import APInvoiceDetailService
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission


@csrf_exempt
@api_view(['GET','POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def apdebit_ccbs(request,apdebit_id):
    if request.method == 'POST':
        from utilityservice.service import api_service
        ap_data = json.loads(request.body)
        scope = request.scope
        apcredit_serv=APInvoiceDetailService(scope)
        emp_id = request.employee_id
        apinvdtl_list = NWisefinList()
        for i in ap_data['ccbs']:
            apccbsdebit_obj = APccbsDetailsRequest(i)
            apccbs_resp = apcredit_serv.apccbs_create(apccbsdebit_obj,apdebit_id, emp_id)
            apinvdtl_list.append(apccbs_resp)
        response = HttpResponse(apinvdtl_list.get(), content_type='application/json')
        return response
    elif request.method == 'GET':
        return fetch_apdebit_ccbs_list(request,apdebit_id)

def fetch_apdebit_ccbs_list(request,apdebit_id):
    from utilityservice.service import api_service
    scope = request.scope
    apcredit_serv=APInvoiceDetailService(scope)
    emp_id = request.employee_id
    resp_obj = apcredit_serv.fetch_apdebit_ccbs_list(request,apdebit_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_apdebit_ccbs_single(request,ccbs_id):
    if request.method == 'GET':
        from utilityservice.service import api_service
        scope = request.scope
        apinvdtls_serv=APInvoiceDetailService(scope)
        emp_id = request.employee_id
        resp_obj = apinvdtls_serv.get_apdebit_ccbs_single(request,ccbs_id,emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_apdebit_ccbs_single(request, ccbs_id)


def delete_apdebit_ccbs_single(request, ccbs_id):
    from utilityservice.service import api_service
    scope = request.scope
    apdebit_serv=APInvoiceDetailService(scope)
    emp_id = request.employee_id
    resp_obj = apdebit_serv.apdebit_ccbs_single_delete(ccbs_id, emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response