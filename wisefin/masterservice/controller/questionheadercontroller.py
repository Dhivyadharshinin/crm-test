import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from masterservice.data.request.questionheaderrequest import QuestionheaderRequest
from masterservice.service.questionheaderservice import QuestionheaderService
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission


@csrf_exempt
@api_view(['POST', 'GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_question_header(request):
    if request.method == 'POST':
        data_json = json.loads(request.body)
        for x in data_json:
            scope = request.scope
            user_id = request.employee_id
            question_header = QuestionheaderRequest(x)
            question_header_serv = QuestionheaderService(scope)
            req_obj = question_header_serv.create_question_header(question_header, user_id)
        response = HttpResponse(req_obj.get(), content_type='application/json')
        return response


    if request.method == 'GET':
        scope = request.scope
        questionheader_serv = QuestionheaderService(scope)
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        req_obj = questionheader_serv.fetch_questionheader(vys_page, request,scope)
        response = HttpResponse(req_obj.get(), content_type='application/json')
        return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_question_header(request, id):
    if request.method == 'GET':
        scope = request.scope
        questioheader_serv = QuestionheaderService(scope)
        req_obj = questioheader_serv.get_question_header(id)
        response = HttpResponse(req_obj.get(), content_type='application/json')
        return response

    elif request.method == 'DELETE':
        scope = request.scope
        questionheader_serv = QuestionheaderService(scope)
        req_obj = questionheader_serv.del_question_header(id)
        response = HttpResponse(req_obj.get(), content_type='application/json')
        return response



#QUESTION_TYPE AND QUESTION_HEADER
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def type_base_headername(request):
    if request.method == 'GET':
        scope = request.scope
        questionheader_type = QuestionheaderService(scope)
        req_obj = questionheader_type.type_base_headername(request)
        response = HttpResponse(req_obj.get(), content_type='application/json')
        return response


#header_based_question
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def header_based_question(request, id):
    if request.method == 'GET':
        scope = request.scope
        questiontype_serv = QuestionheaderService(scope)
        req_obj = questiontype_serv.header_based_question(id)
        response = HttpResponse(req_obj.get(), content_type='application/json')
        return response