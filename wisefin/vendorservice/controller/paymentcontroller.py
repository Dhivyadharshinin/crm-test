import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from vendorservice.service.paymentservice import paymentservice
from userservice.service.employeeservice import EmployeeService
from vendorservice.data.request.paymentrequest import PaymentRequest
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from masterservice.service.bankservice import BankService
from masterservice.service.bankbranchservice import BankBranchService
from masterservice.service.paymodeservice import PaymodeService
from vendorservice.service.branchservice import branchservice
from vendorservice.service.vendorservice import VendorService
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from utilityservice.data.response.nwisefinerror import NWisefinError
# payment - create , insert , update , delete


@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
@csrf_exempt
def payment(request, branch_id):
    branch_code = request.GET.get('code', None)
    scope = request.scope
    vendor_service = VendorService(scope)
    if (branch_code is None) or (branch_code == ''):
        pass
    else:
        branch_id = vendor_service.get_branch_code_by_id(branch_code)
        if branch_id is None:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_DATA)
            response = HttpResponse(error_obj.get(), content_type="application/json")
            return response
    if request.method == 'POST':
        payment_service = paymentservice(scope)
        payment_data = json.loads(request.body)
        payment_obj = PaymentRequest(payment_data)
        employee_id = request.employee_id
        vendor_id = payment_service.get_vendor_id(branch_id)
        mod_status = vendor_service.get_modification_status(vendor_id)
        if mod_status:
            resp_obj = payment_service.payment_modification(payment_obj, employee_id, branch_id, vendor_id)
        else:
            resp_obj = payment_service.create_payment(payment_obj, employee_id, branch_id, vendor_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_payment_list(request, branch_id)


def fetch_payment_list(request, branch_id):
    scope = request.scope
    payment_service = paymentservice(scope)
    employee_id = request.employee_id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = payment_service.fetch_payment_list(request, vys_page, employee_id, branch_id)
    bank_service = BankService(scope)
    bankbranch_service = BankBranchService(scope)
    paymode_service = PaymodeService(scope)
    branch_service = branchservice(scope)
    x = resp_obj.data
    for i in x:
        bank_id = i.bank_id
        bank = bank_service.fetch_bank(bank_id, employee_id)
        i.bank_id = bank
        branch_id = i.branch_id
        branch = bankbranch_service.fetch_bankbranch(branch_id, employee_id)
        i.branch_id = branch

        paymode_id = i.paymode_id
        paymode = paymode_service.fetchpaymode(paymode_id)
        i.paymode_id = paymode

        supplierbranch_id = i.supplierbranch_id
        supplierbranch = branch_service.fetch_branch(supplierbranch_id)
        i.supplierbranch_id = supplierbranch

        vendor_status = branch_service.get_vendorstatus_branch(supplierbranch_id)
        i.q_modify = False
        if (i.created_by == employee_id):
            if (vendor_status == 0 or vendor_status == 1):
                i.q_modify = True
        # modification
        # i.q_modify = True

    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
def delete_payment(request,branch_id,payment_id):
    scope = request.scope
    payment_service = paymentservice(scope)
    employee_id = request.employee_id
    vendor_service = VendorService(scope)
    vendor_id = payment_service.get_vendor_id(branch_id)
    mod_status = vendor_service.get_modification_status(vendor_id)
    if mod_status:
        resp_obj = payment_service.modification_delete_payment(payment_id,vendor_id,employee_id,branch_id)
    else:
        resp_obj = payment_service.inactive_payment(payment_id,vendor_id,employee_id,branch_id)

    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_payment(request, branch_id, payment_id):
    branch_code = request.GET.get('code', None)
    scope = request.scope
    vendor_service = VendorService(scope)
    if (branch_code is None) or (branch_code == ''):
        pass
    else:
        branch_id = vendor_service.get_branch_code_by_id(branch_code)
        if branch_id is None:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_DATA)
            response = HttpResponse(error_obj.get(), content_type="application/json")
            return response
    if request.method == 'GET':
        payment_service = paymentservice(scope)
        bank_service = BankService(scope)
        bankbranch_service = BankBranchService(scope)
        paymode_service = PaymodeService(scope)
        branch_service = branchservice(scope)
        employee_id = request.employee_id
        resp_obj = payment_service.fetch_payment(payment_id)

        bank_id = resp_obj.bank_id
        bank = bank_service.fetch_bank(bank_id, employee_id)
        resp_obj.bank_id = bank

        branch_id = resp_obj.branch_id
        branch = bankbranch_service.fetch_bankbranch(branch_id, employee_id)
        resp_obj.branch_id = branch

        paymode_id = resp_obj.paymode_id
        paymode = paymode_service.fetchpaymode(paymode_id)
        resp_obj.paymode_id = paymode

        supplierbranch_id = resp_obj.supplierbranch_id
        supplierbranch = branch_service.fetch_branch(supplierbranch_id)
        resp_obj.supplierbranch_id = supplierbranch

        vendor_status = branch_service.get_vendorstatus_branch(supplierbranch_id)
        resp_obj.q_modify = False
        if (resp_obj.created_by == employee_id):
            if (vendor_status == 0 or vendor_status == 1):
                resp_obj.q_modify = True
        # modificaton
        resp_obj.q_modify = True

        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_payment(request,branch_id,payment_id)


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def supplier_payment(request,branch_id):
    scope = request.scope
    payment_service = paymentservice(scope)
    employee_id = request.employee_id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = payment_service.fetch_payment_list(request, vys_page,employee_id,branch_id)
    bank_service = BankService(scope)
    # bankbranch_service = BankBranchService()
    paymode_service = PaymodeService(scope)
    branch_service = branchservice(scope)
    x = resp_obj.data
    for i in x:
        bank_id = i.bank_id
        if (bank_id == 0) | (bank_id == None) | (bank_id == -1):
            i.bank_id = ""
        else:
            bank = bank_service.fetch_bank(bank_id, employee_id)
            i.bank_id = bank

        # branch_id = i.branch_id
        # branch = bankbranch_service.fetch_bankbranch(branch_id, employee_id)
        # i.branch_id = branch

        paymode_id = i.paymode_id
        paymode = paymode_service.fetchpaymode(paymode_id)
        i.paymode_id = paymode
        #
        supplierbranch_id = i.supplierbranch_id
        # supplierbranch = branch_service.fetch_branch(supplierbranch_id)
        # i.supplierbranch_id = supplierbranch

        vendor_status = branch_service.get_vendorstatus_branch(supplierbranch_id)
        i.q_modify = False
        if (i.created_by == employee_id):
            if (vendor_status == 0 or vendor_status == 1):
                i.q_modify = True
        # modification
        # i.q_modify = True
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
@api_view([ 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
@csrf_exempt
def payment_activeflag(request):
    if request.method == 'POST':
        scope = request.scope
        payment_service = paymentservice(scope)
        payment_data = json.loads(request.body)
        payment_json=payment_data
        payment_obj = PaymentRequest(payment_data)
        employee_id = request.employee_id
        vendor_service = VendorService(scope)
        vendor_id = payment_service.get_vendor_id(payment_data['supplierbranch_id']['id'])
        mod_status = vendor_service.get_modification_status(vendor_id)
        if mod_status:
            resp_obj = payment_service.modification_paymentactive(payment_obj,payment_data['supplierbranch_id']['id'],vendor_id,employee_id)
        else:
            resp_obj = payment_service.paymentactiveflagservice(payment_obj)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated,NWisefinPermission])
def getcreditgl(request,branch_id,paymode_id):
    if request.method == 'GET':
        scope = request.scope
        payment_service = paymentservice(scope)
        resp_obj = payment_service.supplierpayment(branch_id,paymode_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated,NWisefinPermission])
def getcreditpay(request,branch_id):
    if request.method == 'GET':
        scope = request.scope
        payment_service = paymentservice(scope)
        emp_id = request.employee_id
        resp_obj = payment_service.fetch_creditpayment(branch_id,emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
