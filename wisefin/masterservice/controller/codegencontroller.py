import decimal
import json
from datetime import datetime

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from masterservice.data.request.codegenrequest import CodegenRequest
from masterservice.data.response.Hsnresponse import HsnResponse
from masterservice.data.response.apcategoryresponse import ApcategoryResponse
from masterservice.data.response.productresponse import ProductResponse
from masterservice.data.response.uomresponse import UomResponse
from masterservice.models import APsubcategory
from masterservice.service.codegenservice import CodegeneratorService
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def codegenerator_list(request):
    scope = request.scope
    assetdetails_serv=CodegeneratorService(scope)
    query_obj=CodegenRequest(request)
    resp_obj = assetdetails_serv.fetch_codegenerator_list(request,query_obj)
    return resp_obj
def dictdefault(data):
    if isinstance(data,ProductResponse):
        return data.__dict__
    if isinstance(data,ApcategoryResponse):
        return data.__dict__
    if isinstance(data,APsubcategory):
        return data.__dict__
    if isinstance(data,HsnResponse):
        return data.__dict__
    if isinstance(data,UomResponse):
        return data.__dict__
    if isinstance(data,datetime):
        return str(data)
    if isinstance(data,decimal.Decimal):
        return int(data)
    else:
        return str(data)


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_subcat_code_gen(request):
    if request.method == 'POST':
        #print("id",id)
        scope = request.scope
        cgs_serv = CodegeneratorService(scope)
        cgs_data = json.loads(request.body)
        cgs_data['url']=1
        emp_id = request.employee_id
        response_obj = cgs_serv.code_gen_details(cgs_data, emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response