import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from vendorservice.data.request.suboptionanswerrequest import SuboptionsanswerRequest
from vendorservice.service.suboptionanswerservice import SuboptionanswerService


@csrf_exempt
@api_view(['POST', 'GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def suboption_create(request):
    if request.method == 'POST':
        data_json = json.loads(request.body)
        scope = request.scope
        user_id = request.employee_id
        suboption_req = SuboptionsanswerRequest(data_json)
        suboption_serv = SuboptionanswerService(scope)
        req_obj = suboption_serv.suboption_create(suboption_req,user_id)
        response = HttpResponse(req_obj.get(), content_type='application/json')
        return response

    elif request.method == 'GET':
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        scope = request.scope
        suboption_serv = SuboptionanswerService(scope)
        req_obj = suboption_serv.fetch_suboption_answer(vys_page)
        response = HttpResponse(req_obj.get(), content_type='application/json')
        return response


@csrf_exempt
@api_view(['GET','DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def suboption_get(request,id):
    if request.method == 'GET':
        scope = request.scope
        suboption_serv = SuboptionanswerService(scope)
        req_serv = suboption_serv.suboption_get(id)
        response = HttpResponse(req_serv.get(), content_type='application/json')
        return response
    elif request.method == 'DELETE':
        scope = request.scope
        suboption_serv = SuboptionanswerService(scope)
        req_serv = suboption_serv.del_suboption(id)
        response = HttpResponse(req_serv.get(), content_type='application/json')
        return response