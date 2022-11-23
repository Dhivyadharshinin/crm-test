import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from userservice.service.employeeservice import EmployeeService
from vendorservice.data.request.supplierrequest import ProductRequest
from vendorservice.service.productservice import productservice
from vendorservice.service.supplierservice import AddressService , ContactService
from vendorservice.data.request.supplierrequest import ContactRequest

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
# from masterservice.service.designationservice import DesignationService
from masterservice.service.contacttypeservice import ContactTypeService
from vendorservice.controller.vendorcontroller import VendorService
from django.db import transaction

# supplier product - create , insert , update , delete
@transaction.atomic
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def product(request,vendor_id):
    if request.method == 'POST':
        scope = request.scope
        product_service = productservice(scope)
        contact_service = ContactService(scope)
        product_data = json.loads(request.body)
        employee_id = request.employee_id
        product_obj = ProductRequest(product_data)
        clt1= product_data.get("client_contact1")
        client1= None
        clt2 =product_data.get("client_contact2")
        client2=None
        cust1 = product_data.get("customer_contact1")
        customer1 = None
        cust2 = product_data.get("customer_contact2")
        customer2 = None



        vendor_service = VendorService(scope)
        mod_status = vendor_service.get_modification_status(vendor_id)
        if mod_status:
            if bool(clt1):
                contact_obj = ContactRequest(clt1)
                client1 = contact_service.modification_create_contact(contact_obj, employee_id,vendor_id)
            if bool(clt2):
                contact_obj = ContactRequest(clt2)
                client2 = contact_service.modification_create_contact(contact_obj, employee_id,vendor_id)
            if bool(cust1):
                contact_obj = ContactRequest(cust1)
                customer1 = contact_service.modification_create_contact(contact_obj, employee_id,vendor_id)
            if bool(cust2):
                contact_obj = ContactRequest(cust2)
                customer2 = contact_service.modification_create_contact(contact_obj, employee_id,vendor_id)
            resp_obj = product_service.product_modification(product_obj,employee_id,client1,client2,customer1,customer2,vendor_id)
        else:
            if bool(clt1):
                contact_obj = ContactRequest(clt1)
                client1 = contact_service.create_contact(contact_obj, employee_id,vendor_id)
            if bool(clt2):
                contact_obj = ContactRequest(clt2)
                client2 = contact_service.create_contact(contact_obj, employee_id,vendor_id)
            if bool(cust1):
                contact_obj = ContactRequest(cust1)
                customer1 = contact_service.create_contact(contact_obj, employee_id,vendor_id)
            if bool(cust2):
                contact_obj = ContactRequest(cust2)
                customer2 = contact_service.create_contact(contact_obj, employee_id,vendor_id)
            resp_obj = product_service.create_product(product_obj,employee_id,client1,client2,customer1,customer2,vendor_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_product_list(request,vendor_id)

def fetch_product_list(request,vendor_id):
    scope = request.scope
    product_service = productservice(scope)
    contact_service = ContactService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)

    employee_id = request.employee_id
    resp_obj = product_service.fetch_product_list(request, vys_page, employee_id,vendor_id)
    vendor_service = VendorService(scope)

    x = resp_obj.data
    for i in x:
        cont_id = i.client1_id
        if cont_id is not None:
            contact = contact_service.fetch_contact(cont_id, employee_id)
            i.client1_id = contact

        cont_id = i.client2_id
        if cont_id is not None:
            contact = contact_service.fetch_contact(cont_id, employee_id)
            i.client2_id = contact

        cont_id = i.customer1_id
        if cont_id is not None:
            contact = contact_service.fetch_contact(cont_id, employee_id)
            i.customer1_id = contact

        cont_id = i.customer2_id
        if cont_id is not None:
            contact = contact_service.fetch_contact(cont_id, employee_id)
            i.customer2_id = contact

        vendor_id = i.vendor_id
        vendor_status = vendor_service.get_vendor_status(vendor_id)
        i.q_modify = False
        if (i.created_by == employee_id):
            if (vendor_status == 0 or vendor_status == 1):
                i.q_modify = True

    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
def delete_product(request,product_id,vendor_id):
    scope = request.scope
    product_service = productservice(scope)
    employee_id = request.employee_id
    vendor_service = VendorService(scope)
    mod_status = vendor_service.get_modification_status(vendor_id)
    if mod_status:
        resp_obj = product_service.modification_delete_product( product_id, employee_id,vendor_id)
    else:
        resp_obj = product_service.delete_product(product_id, vendor_id,employee_id)

    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_product(request, product_id,vendor_id):
    if request.method == 'GET':
        scope = request.scope
        product_service = productservice(scope)
        contact_service = ContactService(scope)
        contacttype_service = ContactTypeService(scope)
        # designation_service = DesignationService(scope)
        vendor_service = VendorService(scope)
        employee_id = request.employee_id
        resp_obj = product_service.fetch_product(product_id,vendor_id)

        product_id=resp_obj.client1_id
        if product_id is not None:
            client1 = contact_service.fetch_contact(product_id, employee_id)
            resp_obj.client1_id = client1

        product_id = resp_obj.client2_id
        if product_id is not None:
            client2 = contact_service.fetch_contact(product_id, employee_id)
            resp_obj.client2_id = client2

        product_id = resp_obj.customer1_id
        if product_id is not None:
            customer1 = contact_service.fetch_contact(product_id, employee_id)
            resp_obj.customer1_id = customer1

        product_id = resp_obj.customer2_id
        if product_id is not None:
            customer2 = contact_service.fetch_contact(product_id, employee_id)
            resp_obj.customer2_id = customer2

        #1

        # designation_id = resp_obj.client1_id.designation_id
        # designation = designation_service.fetch_designation(designation_id)
        # resp_obj.client1_id.designation_id = designation
        # #2
        #
        # designation_id = resp_obj.client2_id.designation_id
        # designation = designation_service.fetch_designation(designation_id)
        # resp_obj.client2_id.designation_id = designation
        # 3

        # designation_id = resp_obj.customer1_id.designation_id
        # designation = designation_service.fetch_designation(designation_id)
        # resp_obj.customer1_id.designation_id = designation
        # # 3
        #
        # designation_id = resp_obj.customer2_id.designation_id
        # designation = designation_service.fetch_designation(designation_id)
        # resp_obj.customer2_id.designation_id = designation

        vendor_id = resp_obj.vendor_id
        vendor_status = vendor_service.get_vendor_status(vendor_id)
        resp_obj.q_modify = False
        if (resp_obj.created_by == employee_id):
            if (vendor_status == 0 or vendor_status == 1):
                resp_obj.q_modify = True

        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_product(request,product_id,vendor_id)
