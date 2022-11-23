import json
from django.http import HttpResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from reportservice.service.reportservice import ReportService
from reportservice.util.reportutil import Fetch_Data
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_moduledropdown(request):
    if request.method == 'GET':
        scope = request.scope
        reporttemp_service = ReportService(scope)
        # user_id = request.employee
        resp_obj = reporttemp_service.fetch_moduledropdownservice()
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_modulenamedropdown(request,module_id):
    if request.method == 'GET':
        scope = request.scope
        reporttemp_service = ReportService(scope)
        resp_obj = reporttemp_service.fetch_modulenamedropdownservice(module_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@csrf_exempt
@api_view(['GET','POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_displayname(request):
    if request.method == 'GET':
        scope = request.scope
        trans_id = request.GET.get('trans_id')
        dynamic_query = Fetch_Data(scope)
        query = dynamic_query.dynamic_query(trans_id,scope)
        query = json.dumps(query, indent=6)
        return HttpResponse(query, content_type='application/json')


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_moduleparameter(request):
    if request.method == 'POST':
        scope = request.scope
        paramtemp_service = ReportService(scope)
        paramname_details = json.loads(request.body)
        module_id = paramname_details['module_id']
        report_id = paramname_details['report_id']
        paramname = paramname_details['rep_temp_name']
        columnname = paramname_details['data_filter_report']
        filtername = paramname_details['data']
        columnname = json.dumps(columnname)
        columnname = list(columnname)
        columnname[16] = ''
        columnname[-2] = ''
        columnname = ''.join(columnname)
        filtername = json.dumps(filtername)
        filtername = list(filtername)
        filtername[18] = ''
        filtername[-2] = ''
        filtername = ''.join(filtername)
        emp_id = request.employee_id
        resp_obj = paramtemp_service.create_moduleparameter(module_id, report_id, emp_id, paramname,
                                                            columnname, filtername, scope)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response