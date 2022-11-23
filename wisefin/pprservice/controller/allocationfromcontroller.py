import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from utilityservice.data.response.nwisefinlist import NWisefinList
from pprservice.data.request.allocationfromrequest import AllocationFromRequest
from pprservice.service.allocationfromservice import AllocationService
from userservice.service.employeeservice import EmployeeService
from masterservice.models import Bank


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def allocation(request):
    if request.method == 'POST':
        scope=request.scope
        allocation_service = AllocationService(scope)
        allocation_data = json.loads(request.body)
        allocation_obj = AllocationFromRequest(allocation_data)

        empid = request.employee_id
        resp_obj = allocation_service.create_allocation(allocation_obj, empid)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    # elif request.method == 'GET':
    #     return fetch_allocationfrom_list(request)

#
# def fetch_allocationfrom_list(request):
#     allocation_service = AllocationService()
#     user_id = request.user.id
#     page = request.GET.get('page', 1)
#     query = request.GET.get('query', None)
#     allocation_from = request.GET.get('allocation_from', None)
#     allocation_level = request.GET.get('allocation_level', None)
#     costdriver = request.GET.get('costdriver', None)
#     page = int(page)
#     vys_page = VysfinPage(page, 10)
#     resp_obj = allocation_service.fetch_allocationfrom_list(vys_page,allocation_from,allocation_level,costdriver)
#     response = HttpResponse(resp_obj.get(), content_type="application/json")
#     return response
#
#
# @csrf_exempt
# @api_view(['GET', 'DELETE'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def fetch_allocationfrom(request,allocationfrom_id):
#     if request.method == 'GET':
#         allocation_service = AllocationService()
#         user_id = request.user.id
#         resp_obj = allocation_service.fetch_allocationfrom(allocationfrom_id,user_id)
#         response = HttpResponse(resp_obj.get(), content_type="application/json")
#         return response
#     elif request.method == 'DELETE':
#         return delete_allocationfrom(request,allocationfrom_id)
#
#
# @csrf_exempt
# def delete_allocationfrom(request,allocationfrom_id):
#     business_service = AllocationService()
#     user_id = request.user.id
#     resp_obj = business_service.delete_allocationfrom(allocationfrom_id,user_id)
#     response = HttpResponse(resp_obj.get(), content_type="application/json")
#     return response
