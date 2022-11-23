from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.http import HttpResponse, JsonResponse
from pprservice.data.request.nac_income_request import ppr_clientrequest
from pprservice.util.pprutility import MASTER_SERVICE

from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from rest_framework.permissions import IsAuthenticated
from pprservice.service.dss_service import DSS_Service
import json
from pprservice.data.request.nac_income_request import ppr_clientrequest, ppr_source_request

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def dss_upload(request):
    scope = request.scope
    if request.method == 'POST':
        file_name = request.FILES.getlist('file')[0].name
        extension = file_name.split('.')[-1]
        scope = request.scope
        dss_service = DSS_Service(scope)
        employee_id = request.employee_id
        import pandas as pd
        import numpy as np
        excel_data = pd.read_excel(request.FILES['file'], engine='openpyxl')
        df1 = pd.DataFrame(excel_data)
        dss_obj = df1.fillna(np.nan).replace([np.nan], [0]).to_dict(orient='records')
        # df1_mask=df1['gl_no']>200000
        # df1=df1[df1_mask]
        # a=df1[df1.gl_no.startswith(3)].index
        # df = df1.drop(a)
        resp_obj = dss_service.dss_upload_date(df1, employee_id)
        return HttpResponse(resp_obj.get(), content_type='application/json')

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def ppr_dssdate_level_list(request):
    scope = request.scope
    if request.method == 'POST':
        filter_obj = json.loads(request.body)
        filter_obj = ppr_source_request(filter_obj)
        pprservice = DSS_Service(scope)
        ppr_data = pprservice.fetch_dssdate_level_list(filter_obj)
        response = HttpResponse(ppr_data.get(), content_type="application/json")
        return response
