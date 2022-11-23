import array
import json
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from userservice.data.request.departmentrequest import DepartmentRequest
from userservice.data.request.genralledgerrequest import General_LedgerRequest
from userservice.models import Employee, Department
from userservice.service.departmentservice import DepartmentService
from userservice.service.generalledgerservice import General_Ledger
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.data.response.nwisefinsearch import NwisefinSearch
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
# from utilityservice.service.nw import VysfinUser

from userservice.data.request.addresscontactrequest import ContactRequest, AddressRequest
from userservice.service.addresscontactservice import AddressService, ContactService
import time
from userservice.service.generalledgerservice import General_LedgerService


# @csrf_exempt
@api_view(['GET', 'POST'])
# @authentication_classes([VysfinAuthentication])
# @permission_classes([IsAuthenticated, VysfinPermission])
def general_ledger(request):
    if request.method == 'POST':
        scope = request.scope
        bank_service = General_LedgerService(scope)
        bank_data = json.loads(request.body)
        bank_obj = General_LedgerRequest(bank_data)
        resp_obj = bank_service.create_gl(bank_obj)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


# @csrf_exempt
@api_view(['POST'])
def glfiledata_sync(request):
    scope=request.scope
    bank_service = General_LedgerService(scope)
    if not request.FILES['file'] is None:
        file = request.FILES['file']
        file_str = file.read()
        bank_obj = json.loads(file_str)
        bank_obj = bank_obj['ESM_GL_Master']
        for x in bank_obj:
            bank_obj = General_LedgerRequest(x)
            resp_obj = bank_service.create_gl(bank_obj)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


# @csrf_exempt
@api_view(['GET'])
# @authentication_classes([VysfinAuthentication])
# @permission_classes([IsAuthenticated, VysfinPermission])
def fetch_allgl_list(request):
    scope=request.scope
    datefilter = request.GET.get('date')
    branch_service = General_LedgerService(scope)

    resp_obj = branch_service.Fetch_All_Gl_List(datefilter)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


# @csrf_exempt
@api_view(['GET'])
# @authentication_classes([VysfinAuthentication])
# @permission_classes([IsAuthenticated, VysfinPermission])
def gl_summary(request):
    scope=request.scope
    gl_service = General_LedgerService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = gl_service.fetch_gl_summary(request, vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def gl_activate_inactivate(request):
    scope=request.scope
    data = json.loads(request.body)
    data_request = General_LedgerRequest(data)
    gl_service = General_LedgerService(scope)
    resp_obj = gl_service.gl_activate_inactivate(request, data_request)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
@api_view(['GET'])
@csrf_exempt
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def gl_no_get(request,gl_no):
    scope=request.scope
    gl_service = General_LedgerService(scope)
    # page = request.GET.get('page', 1)
    # page = int(page)
    # vys_page = NWisefinPage(page, 10)
    resp_obj = gl_service.fetch_gl_no_api(request,gl_no)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

