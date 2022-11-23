import json
from django.http import HttpResponse

from entryservice.data.request.entryparamtemplaterequest import EntryTemplateRequest
from entryservice.data.request.entryrequest import EntryRequest
from entryservice.service.enrtryparametertemplateservice import ParmaTemplateService
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt

from entryservice.service.faentrytemplateservice import FATemplateService
from entryservice.util.entryutil import Fetch_Data, list_conditionname, get_entry_list
from entryservice.util.entryutil import Fetch_Data
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
#from vysfinutility.data.vysfinpage import VysfinPage
from utilityservice.service.entry_api_service import ApiService


@csrf_exempt
@api_view(['GET','POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_FAquerycondition(request):
    if request.method == 'POST':
        scope = request.scope
        paramtemp_service = FATemplateService(scope)
        query_data = json.loads(request.body)
        emp_id = request.employee_id
        id = query_data['id']
        module_name = query_data['module_name']
        #apdebitamount = query_data['apdebit_amount']
        type = request.GET.get('type')
        if type=='CREDIT':
            resp_obj = paramtemp_service.FAqueryconditioncr_check(id,module_name,emp_id,scope)
            response = HttpResponse(resp_obj.get(), content_type="application/json")
            return response
        else:
            resp_obj = paramtemp_service.FAquerycondition_check(id,module_name,emp_id,scope)
            response = HttpResponse(resp_obj.get(), content_type="application/json")
            return response