from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
import json
from django.http import HttpResponse
from utilityservice.data.response.nwisefinpage import NWisefinPage
from masterservice.service.apsectorservice import SectorService
from masterservice.data.request.apsectorrequest import Apsectorrequest
from userservice.service.employeeservice import EmployeeService


#sector
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def Apsector(request):
    if request.method == 'POST':
        scope = request.scope
        sectorservice = SectorService(scope)
        sector_obj = json.loads(request.body)
        sector_obj = Apsectorrequest(sector_obj)
        user_id = request.employee_id
        emp_service = EmployeeService(scope)
        empid = emp_service.get_empid_from_userid(user_id)
        resp_obj = sectorservice.create_sector(sector_obj,empid)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response







@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def sector_search(request):
    user_id = request.employee_id
    scope = request.scope
    query = request.GET.get('query')
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    scope = request.scope
    sector_service = SectorService(scope)
    response_data = sector_service.fetch_sector_search_list(query,vys_page)
    response = HttpResponse(response_data.get(), content_type="application/json")
    return response
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def apsector_activate_inactivate(request):
    if request.method == 'POST':
        scope=request.scope
        apsector_service = SectorService(scope)
        apsector_obj = json.loads(request.body)
        ap_obj = Apsectorrequest(apsector_obj)
        resp_obj = apsector_service.apsector_activate_inactivate(request,ap_obj)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response