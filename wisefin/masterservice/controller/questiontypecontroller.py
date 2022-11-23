import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated

from masterservice.data.request.questiontyperequest import QuestiontypeRequest
from masterservice.service.questiontypeservice import QuestiontypeService
from masterservice.util.masterutil import input_composite_type
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from rest_framework.decorators import api_view, authentication_classes, permission_classes


@csrf_exempt
@api_view(['POST', 'GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_question_type(request):
    if request.method == 'POST':
        data_json = json.loads(request.body)
        for x in data_json:
            scope = request.scope
            user_id = request.employee_id
            questiontype = QuestiontypeRequest(x)
            questiontype_serv = QuestiontypeService(scope)
            resp_obj = questiontype_serv.create_question_type(questiontype, user_id)
        response = HttpResponse(resp_obj.get(), content_type='application/json')
        return response

    elif request.method == 'GET':
        scope = request.scope
        questiontype_serv = QuestiontypeService(scope)
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        req_obj = questiontype_serv.fetch_question_type(vys_page, request,scope)
        response = HttpResponse(req_obj.get(), content_type='application/json')
        return response

@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_question_type(request, id):
    if request.method == 'GET':
        scope = request.scope
        questiontype_serv = QuestiontypeService(scope)
        req_obj = questiontype_serv.get_question_type(id)
        response = HttpResponse(req_obj.get(), content_type='application/json')
        return response

    elif request.method == 'DELETE':
        scope = request.scope
        questiontype_serv = QuestiontypeService(scope)
        req_obj = questiontype_serv.del_question_type(id)
        response = HttpResponse(req_obj.get(), content_type='application/json')
        return response



@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def question_type_info(request,type_id):
    if request.method == 'GET':
        scope = request.scope
        # data_json = json.loads(request.body)
        question_type_serv = QuestiontypeService(scope)
        req_obj = question_type_serv.question_type_info(type_id)
        response = HttpResponse(req_obj.get(), content_type='application/json')
        return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def input_type_drop_down(request):
  if request.method == 'GET':
    # query = request.GET.get('query')
    req_obj = input_composite_type()
    response = HttpResponse(req_obj.get(), content_type='application/json')
    return response
