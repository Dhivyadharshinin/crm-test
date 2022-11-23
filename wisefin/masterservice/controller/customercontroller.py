import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from masterservice.data.request.addressrequest import AddressRequest
from masterservice.data.request.contactrequest import ContactRequest
from masterservice.data.request.customerrequest import CustomerRequest
from masterservice.service.addressservice import AddressService
from masterservice.service.contactservice import ContactService
from masterservice.service.customerservice import CustomerService
from nwisefin.settings import logger
from masterservice.util.masterutil import get_category_type_list
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from masterservice.data.request.apcategoryrequest import ApcategoryRequest
from masterservice.service.apcategoryservice import CategoryService
from utilityservice.data.response.nwisefinpage import NWisefinPage
from userservice.service.employeeservice import EmployeeService
from masterservice.models.mastermodels import APsubcategory
from utilityservice.data.response.nwisefinlist import NWisefinList

#customer
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_customer(request):
    if request.method == 'POST':
        scope = request.scope
        emp_id = request.employee_id
        customer_service = CustomerService(scope)
        customer_json = json.loads(request.body)
        cus_obj = CustomerRequest(customer_json)
        user_id = request.employee_id
        # emp_service = EmployeeService(scope)

        if  customer_json.get("address") is not None :
            address_service = AddressService(scope)
            address = customer_json.get("address")
            address['pincode_id']=1
            address['city_id']=1
            address['district_id']=1
            address_obj = AddressRequest(address)
            add_id = address_service.create_address(address_obj, user_id)


        if customer_json.get("contact") is not None:
            contact_service = ContactService(scope)
            contact = customer_json.get("contact")
            contact['type_id'] =1
            contact['designation_id'] =1
            contact['name'] = customer_json['customer_name']
            contact['email'] = 'FA Customer'
            contact_obj = ContactRequest(contact)
            cont_id = contact_service.create_contact(contact_obj, user_id)
        resp_obj = customer_service.create_customer(cus_obj,add_id,cont_id, emp_id,request)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
       return fetch_customer_list(request)
def fetch_customer_list(request):
        scope = request.scope
        customer_service = CustomerService(scope)
        emp_id = request.employee_id
        page = request.GET.get('page', 1)
        name = request.GET.get('name', None)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        resp_obj = customer_service.fetch_customer_list(vys_page,name,emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

#TA
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ta_state_id(request,city_name):
    if request.method=='GET':
        scope = request.scope
        city=CustomerService(scope)
        # city_name = request.GET.get('city_name', city_name)
        state=city.city_name(city_name)
        response=HttpResponse(state, content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ta_category_id(request,id):
    if request.method=='GET':
        scope = request.scope
        category=CustomerService(scope)
        category_id=category.ecf_category_code(id)
        response=HttpResponse(category_id, content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ta_subcategory_id(request,id):
    if request.method=='GET':
        scope = request.scope
        subcategory=CustomerService(scope)
        subcategory_id=subcategory.ecf_subcategory_code(id)
        response=HttpResponse(subcategory_id, content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def category_no_get(request,id):
    if request.method=='GET':
        scope = request.scope
        category=CustomerService(scope)
        category_id=category.ap_cat_no_get(id)
        response=HttpResponse(category_id, content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def subcategory_no_get(request,no,id):
    if request.method=='GET':
        scope = request.scope
        subcategory=CustomerService(scope)
        subcategory_id=subcategory.ap_subcat_no_get(no,id)
        response=HttpResponse(subcategory_id, content_type="application/json")
        return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ta_get_catgory(request):
    if request.method == "POST":
        scope=request.scope
        tour_reason = request.GET.get('reason')
        service = CustomerService(scope)
        resp_obj=service.ta_reason_category(tour_reason)
        response = HttpResponse(resp_obj, content_type='application/json')
        return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ta_get_subcatgory(request):
    if request.method == "POST":
        scope=request.scope
        category_no = request.GET.get('no')
        expense=request.GET.get('name')
        service = CustomerService(scope)
        resp_obj=service.ta_sub_category(category_no,expense)
        response = HttpResponse(resp_obj, content_type='application/json')
        return response


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def commodity_ta(request):
    if request.method == "POST":
        scope=request.scope
        commodity_name=request.GET.get('commodity_name')
        service = CustomerService(scope)
        resp_obj=service.ta_commodity(commodity_name)
        return HttpResponse(resp_obj, content_type='application/json')


