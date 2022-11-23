import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from masterservice.service.question_groupmapping_service import Questioner_mapping, VowQuesansprojService


@csrf_exempt
@api_view(['POST', 'GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def question_group_mapping(request,type_id):
    if request.method=="POST":
        scope=request.scope
        employee_id=request.employee_id
        is_remove = request.GET.get('is_remove')
        data=json.loads(request.body)
        cls=Questioner_mapping(scope)
        response_obj=cls.question_mapping_add(type_id,data,is_remove,employee_id)
        response = HttpResponse(response_obj.get(), content_type="application/json")
    elif request.method=="GET":
        scope = request.scope
        employee_id = request.employee_id
        cls = Questioner_mapping(scope)
        response_obj=cls.question_group_get(type_id)
        response = HttpResponse(response_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_questype(request, pro_id):
    if request.method == 'GET':
        scope = request.scope
        proj_service = Questioner_mapping(scope)
        resp_obj = proj_service.projectquestion(pro_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['POST','GET'])
def vow_fetch_projansw(request,pro_id):
    quesans_service = VowQuesansprojService(request)
    if request.method == 'GET':
        resp_obj = quesans_service.vow_projectquestion(request,pro_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response