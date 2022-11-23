import json

from nwisefin.settings import logger
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from masterservice.data.request.financialyearrequest import FinancialYearRequest
from masterservice.service.financialyearservice import Financial_year_service
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def financial_year(request):
    if request.method == 'POST':
        scope = request.scope
        fin_serv = Financial_year_service(scope)
        fin_data = json.loads(request.body)
        fin_obj = FinancialYearRequest(fin_data)
        emp_id = request.employee_id
        resp_obj = fin_serv.create_finyear(fin_obj, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return financial_year_summary(request)


def financial_year_summary(request):
    scope = request.scope
    fin_serv = Financial_year_service(scope)
    emp_id = request.employee_id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    query = request.GET.get('query', None)
    resp_obj = fin_serv.fetch_finyr_list(request,vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def finyr_activate_inactivate(request):
    if request.method == 'POST':
        scope = request.scope
        fin_serv = Financial_year_service(scope)
        fin_obj = json.loads(request.body)
        finyr_obj = FinancialYearRequest(fin_obj)
        resp_obj = fin_serv.finyr_activate_inactivate(request,finyr_obj)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response