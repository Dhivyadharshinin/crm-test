import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import authentication_classes, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from masterservice.data.request.minwagestatezonerequest import MinwageRequest
from masterservice.data.request.statezonecitymasterrequest import statezonecityRequest

from masterservice.service.minwagestatezoneservice import minwageService
from masterservice.service.statezonecitymasterservice import statezonecityService

from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from utilityservice.data.response.nwisefinpage import NWisefinPage


@csrf_exempt
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_statezone(request):
    if request.method=='POST':
        arrobj=json.loads(request.body)
        user_id = request.employee_id
        subject_service = statezonecityService()
        emp_id = user_id
        arr_obj=statezonecityRequest(arrobj)
        resp_obj=subject_service.create_statezone(arr_obj,emp_id)
        response=HttpResponse(resp_obj.get(),content_type='application/json')
        return response
    elif request.method == 'GET':
        return minwagestate_list(request)
def minwagestate_list(request):
    subject_service=statezonecityService()
    user_id = request.employee_id
    emp_id = user_id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = subject_service.minwagestate_list(vys_page)
    response = HttpResponse(resp_obj.get(), content_type='application/json')
    return response