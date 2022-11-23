import json
from django.http import HttpResponse
from entryservice.data.request.entryrequest import EntryRequest
from entryservice.service.entryservice  import EntryService
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from entryservice.data.request.entryoraclecommonrequest import OracleRequest
from entryservice.service.entryoracleservice import EntryOracleService
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
#from vysfinutility.data.vysfinpage import VysfinPage
from utilityservice.service.entry_api_service import ApiService
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def entry_oracle_comman_api(request):
    if request.method == 'POST':
        try:
            scope = request.scope
            entry_data = json.loads(request.body)
            entry_orcle_obj=OracleRequest(entry_data)
            entry_service=EntryOracleService(scope)
            emp_id = request.employee_id
            response_obj = entry_service.journal_entry_api(entry_orcle_obj, emp_id)
            return JsonResponse(response_obj)
        except Exception as e:
            return JsonResponse({"Message": "ERROR_OCCURED_ON_ORACLE_COMMON_API_", "DATA": str(e)})