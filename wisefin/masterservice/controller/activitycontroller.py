import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated
from masterservice.data.request.questionrequest import ActivityRequest

from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from masterservice.service.activityservice import Activityservice


@csrf_exempt
@api_view(['POST', 'GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_activity(request):
    if request.method == 'POST':
        # data_json = json.loads(request.body.get('data'))
        request_data = json.loads(request.body)
        sendto_model_data=ActivityRequest(request_data)
        user_id = request.employee_id
        response_model=Activityservice(request.scope).create_activity(sendto_model_data,user_id)
        response = HttpResponse(response_model.get(), content_type='application/json')
        return response
    elif request.method == 'GET':
        scope = request.scope
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        req_obj =Activityservice(scope).Activityget(request,vys_page)
        response = HttpResponse(req_obj.get(), content_type='application/json')
        return response


@csrf_exempt
@api_view(['GET','DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_activity(request, id):
    if request.method == 'GET':
        scope = request.scope
        activity_serv = Activityservice(scope)
        req_obj = activity_serv.get_activity(id)
        response = HttpResponse(req_obj.get(), content_type='application/json')
        return response

    elif request.method == 'DELETE':
        scope = request.scope
        ativity_serv = Activityservice(scope)
        req_obj = ativity_serv.del_activity(id)
        response = HttpResponse(req_obj.get(),content_type='application/json')
        return response

