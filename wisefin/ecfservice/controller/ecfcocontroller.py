import json
from datetime import datetime

import pandas as pd
from ecfservice.service.ecfcoservice import Ecfcoservice
from ecfservice.util.ecfutil import get_status_list
from django.http import HttpResponse, StreamingHttpResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission

#listall for loan application
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ecfco_list(request):
    emp_id = request.employee_id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    scope = request.scope
    ecfcoqservice = Ecfcoservice(scope)
    resp_obj=ecfcoqservice.ecfco_list(request,vys_page,emp_id)
    response=HttpResponse(resp_obj.get(),content_type='application/json')
    return response

#Transaction details
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_ecftransget(request, No):
    if request.method == 'GET':
        emp_id = request.employee_id
        scope = request.scope
        ecfcoqservice = Ecfcoservice(scope)
        response = ecfcoqservice.ecf_queuedetails(request,No)
        resp_obj = HttpResponse(response.get(), content_type="application/json")
        return resp_obj


#Search for empquery
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def search_empquery(request):
    if request.method == 'POST':
        grn_obj = json.loads(request.body)
        emp_id = request.employee_id
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        scope = request.scope
        ecfcoqservice = Ecfcoservice(scope)
        response_obj = ecfcoqservice.ecfco_search(request,vys_page,grn_obj,emp_id)
        resp_obj = HttpResponse(response_obj.get(), content_type='application/json')
        return resp_obj

# @api_view(['GET'])
# @authentication_classes([VysfinAuthentication])
# @permission_classes([IsAuthenticated, VysfinPermission])
# def schedule_report_download(request):
#     user_id = request.user.id
#     from vysfinutility.service import api_service
#     api_serv = api_service.ApiService()
#     emp = api_serv.get_emp_id(request, user_id)
#     emp_id = emp['id']
#     download_xl_resp=ecfcoqservice.download_excel(emp_id)
#     return download_xl_resp

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_ecf(request, No):
    emp_id = request.employee_id
    scope = request.scope
    ecfcoqservice = Ecfcoservice(scope)
    response = ecfcoqservice.empqlist(request,No,emp_id)
    resp_obj = HttpResponse(response.get(), content_type="application/json")
    return resp_obj

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_ecfstatus_list(request):
    resp_obj = get_status_list()
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ecfco_download(request):
    emp_id = request.employee_id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    scope = request.scope
    ecfcoqservice = Ecfcoservice(scope)
    resp_obj=ecfcoqservice.ecfco_download(request,vys_page,emp_id)
    import io
    BytesIO = io.BytesIO()
    output = BytesIO
    df = pd.DataFrame.from_records(resp_obj)
    print(df)
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1', index=False)
    print("test",df)
    writer.save()
    output.seek(0)
    print(datetime.now().strftime("%y%m%d_%H%M%S"))
    file_name = 'ECF_REPORT-(' + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ').xlsx'
    response = StreamingHttpResponse(output, content_type='application/octet-stream')
    response['Content-Disposition'] = 'inline; filename="{}"'.format(file_name)
    return response