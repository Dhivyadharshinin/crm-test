import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from masterservice.data.request.bankrequest import BankRequest
from masterservice.data.request.bsproductrequest import BusinessProductRequest
from masterservice.service.bankservice import BankService
from masterservice.service.bsproductservice import BsproductService
from userservice.service.employeeservice import EmployeeService
from masterservice.models import Bank
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission

#test
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_bsproduct(request):
    if request.method == 'POST':
        scope = request.scope
        emp_id = request.employee_id
        bsproduct_service = BsproductService(scope)
        bsproduct_data = json.loads(request.body)
        bsproduct_obj = BusinessProductRequest(bsproduct_data)
        resp_obj = bsproduct_service.create_bsproduct(bsproduct_obj, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return bsproductcode_list(request)

def bsproductcode_list(request):
    scope = request.scope
    bsproduct_service = BsproductService(scope)
    page = request.GET.get('page', 1)
    query = request.GET.get('query', None)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = bsproduct_service.fetch_bsproductlist(vys_page,query)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
