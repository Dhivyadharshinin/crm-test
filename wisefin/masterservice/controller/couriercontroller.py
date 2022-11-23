import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from inwardservice.service.inwardservice import InwardService
from userservice.service.employeeservice import EmployeeService
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.api_service import ApiService
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from masterservice.data.request.courierrequest import CourierRequest
from masterservice.service.contactservice import ContactService
from masterservice.service.addressservice import AddressService
from masterservice.data.request.addressrequest import AddressRequest
from masterservice.data.request.contactrequest import ContactRequest
from masterservice.service.courierservice import CourierService

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def courier(request):
    if request.method == 'POST':
        scope = request.scope
        inward_service = InwardService(scope)
        courier_service = CourierService(scope)
        courier_data = json.loads(request.body)
        user_id = request.employee_id
        emp_service = EmployeeService(scope)
        # emp_id = emp_service.get_empid_from_userid(user_id)
        courier_data['all_branch'] = True
        courier_obj = CourierRequest(courier_data)
        add_id=None
        cont_id=None

        if courier_data.get("address") is not None:
            scope = request.scope
            address_service = AddressService(scope)
            address = courier_data.get("address")
            address_obj = AddressRequest(address)
            add_id = address_service.create_address(address_obj, user_id)

        if courier_data.get("contact") is not None:
            scope = request.scope
            contact_service = ContactService(scope)
            contact = courier_data.get("contact")
            contact_obj = ContactRequest(contact)
            cont_id = contact_service.create_contact(contact_obj, user_id)

        resp_obj = courier_service.create_courier(courier_obj,add_id,cont_id,user_id)
        courier_obj=json.loads(resp_obj.get())
        api_obj=ApiService(scope)
        branch_id=api_obj.get_empbranch_empid(request,user_id)
        courier_id=courier_obj['id']
        courier_br = inward_service.courier_branch(branch_id, courier_id)
        print(courier_id,branch_id,'branch_id',courier_br)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_courier_list(request)


def fetch_courier_list(request):
    scope = request.scope
    courier_service = CourierService(scope)
    user_id = request.employee_id
    emp_service = EmployeeService(scope)
    emp_id = emp_service.get_empid_from_userid(user_id)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    query = request.GET.get('query', None)
    resp_obj = courier_service.fetch_courier_list(vys_page,emp_id,query)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_courier(request,courier_id):
    if request.method == 'GET':
        scope = request.scope
        emp_id = request.employee_id
        courier_service = CourierService(scope)
        # user_id = request.user.id
        resp_obj = courier_service.fetchcourier(courier_id,emp_id)

        # address_service = AddressService()
        # add_id = resp_obj.address_id
        # address = address_service.fetch_address(add_id,user_id)
        # resp_obj.address_id = address
        #
        # contact_service = ContactService()
        # contact_id = resp_obj.contact_id
        # contact = contact_service.fetchcontact(contact_id)
        # resp_obj.contact_id = contact

        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_courier(request,courier_id)


@csrf_exempt
def delete_courier(request,courier_id):
    scope = request.scope
    emp_id = request.employee_id
    courier_service = CourierService(scope)
    # user_id=request.user.id
    resp_obj = courier_service.deletecourier(courier_id,emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def search_courier(request):
    if request.method == 'GET':
        user_id = request.user.id
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        query = None
        query = request.GET.get('query', None)
        scope = request.scope
        courier_service = CourierService(scope)
        resp_obj = courier_service.search_courier(request, query, vys_page)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

#inward
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def courier_search(request):
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    query = request.GET.get('query', None)
    scope = request.scope
    courier_service = CourierService(scope)
    resp_obj = courier_service.courier_search(query, vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

#inward
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def courier_summarysearch(request):
    scope = request.scope
    courier_service = CourierService(scope)
    name = request.GET.get('name')
    code = request.GET.get('code')
    contact_person = request.GET.get('contact_person')
    query = {"name": name, "code": code, "contact_person": contact_person}
    print(query)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = courier_service.courier_summarysearch(query, vys_page)
    response = HttpResponse(resp_obj.get(), content_type='application/json')
    return response