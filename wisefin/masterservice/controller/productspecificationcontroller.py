import json
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from masterservice.data.request.productspecificationrequest import ProductSpecificationRequest
from masterservice.service.productspecificationservice import ProductSpecificationService
from utilityservice.data.response.nwisefinpage import NWisefinPage
from userservice.service.employeeservice import EmployeeService
from django.db import transaction

@transaction.atomic
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def productspecification(request):
    if request.method == 'POST':
        scope=request.scope
        productspecification_service = ProductSpecificationService(scope)
        product_obj = json.loads(request.body)
        prdspeci_obj = ProductSpecificationRequest(product_obj)
        user_id = request.employee_id
        emp_service = EmployeeService(scope)
        empid = emp_service.get_empid_from_userid(user_id)
        resp_obj = productspecification_service.create_productspec(prdspeci_obj, empid)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
@csrf_exempt
@api_view(['GET', 'POST'])
def productspecification_data(request,number):
    if request.method == 'GET':
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        scope=request.scope
        product_service = ProductSpecificationService(scope)
        resp_obj = product_service.create_productspec_data(request, number,vys_page)
        return HttpResponse(resp_obj.get(), content_type='application/json')


