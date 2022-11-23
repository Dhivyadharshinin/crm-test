import pandas
from django.http import HttpResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from faservice.data.request.assetheaderrequest  import AssetHeaderRequest
from faservice.service.assetheaderservice  import AssetheaderService
from nwisefin.settings import logger
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
import json
from django.db.models import Q
from utilityservice.data.response.nwisefinpage import NWisefinPage
from faservice.util.fautil_valid import date_validation
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess,SuccessMessage,SuccessStatus
from utilityservice.data.response.nwisefinerror import NWisefinError as Error
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription,ErrorMessage
from faservice.util.fautil import Fa_Doctype
from django.db import transaction
#@transaction.atomic (using='fa_service')
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def createassetheader(request):
    if request.method == 'POST':
        scope=request.scope
        assethead_serv = AssetheaderService(scope)
        assetheader_obj = json.loads(request.body)
        logger.info('FAL_ASSETHEADER_DATA:{}'.format(assetheader_obj))
        # user_id = request.user.id
        # emp_id=request.employee_id
        headerobj = AssetHeaderRequest(assetheader_obj)
        resp_obj = assethead_serv.create_assetheader(headerobj)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
