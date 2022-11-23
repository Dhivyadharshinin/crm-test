import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated
from masterservice.data.request.questiontypemapprequest import QuestiontypemappRequest, QuestionflagRequest
from masterservice.service.questiontypemappservice import QuestiontypemappService, Questionflagservices
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from rest_framework.decorators import api_view, authentication_classes, permission_classes
@csrf_exempt
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_questiontype_mapping(request):
    if request.method == 'POST':
        scope = request.scope
        data_json = json.loads(request.body)
        val = data_json['question_id']
        for i in val:
            user_id = request.employee_id
            questiontype = QuestiontypemappRequest(data_json)
            questiontype_serv = QuestiontypemappService(scope)
            req_obj = questiontype_serv.create_questiontype_mapping(questiontype, i, user_id)
            response = HttpResponse(req_obj.get(), content_type='application/json')
        return response

    elif request.method == 'GET':
        scope = request.scope
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        questiontype_serv = QuestiontypemappService(scope)
        req_obj = questiontype_serv.fetch_questiontype_mapping(vys_page,request)
        response = HttpResponse(req_obj.get(), content_type='application/json')
        return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_questiontype_mapping(request, id):
    if request.method == 'GET':
        scope = request.scope
        question_serv = QuestiontypemappService(scope)
        req_obj = question_serv.get_questiontype_mapping(id)
        response = HttpResponse(req_obj.get(), content_type='application/json')
        return response

    elif request.method == 'DELETE':
        scope = request.scope
        question_serv = QuestiontypemappService(scope)
        req_obj = question_serv.del_questiontype_mapping(id)
        response = HttpResponse(req_obj.get(), content_type='application/json')
        return response


def Create_Questionflag(request,type_id,header_id):
    scope = request.scope
    # page = request.GET.get('page', 1)
    question_serv = QuestiontypemappService(scope)
    req_obj = question_serv.create_questionflag(type_id,header_id)

    return req_obj

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def questiontype_mapping_is_checked(request):
    if request.method == 'POST':
        data_json = json.loads(request.body)
        scope = request.scope
        question_serv = QuestiontypemappService(scope)
        question_req = QuestiontypemappRequest(data_json)
        req_obj = question_serv.question_mapping_is_checked(question_req)
        response = HttpResponse(req_obj.get(), content_type='application/json')
        return response

#FLAG_MASTER_CREATE
@csrf_exempt
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_flagmaster(request):
    if request.method == 'POST':
        scope = request.scope
        data_json = json.loads(request.body)
        remove = request.GET.get('remove', 0)
        user_id = request.employee_id
        questionflag_obj = QuestionflagRequest(data_json)
        quesitonflag_serv = Questionflagservices(scope)
        if remove:
            req_obj=quesitonflag_serv.remove_flagmaster(questionflag_obj,user_id)
        else:
             req_obj = quesitonflag_serv.create_flagmaster(questionflag_obj, user_id)

        response = HttpResponse(req_obj.get(), content_type='application/json')
        return response

    elif request.method == 'GET':
        scope = request.scope
        questionflag_serv=Questionflagservices(scope)
        req_obj = questionflag_serv.fetch_flagmaster()
        response = HttpResponse(req_obj.get(),content_type='application/json')
        return response

@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_flagmaster(request, id):
    if request.method == 'GET':
        scope = request.scope
        questionflag_serv = Questionflagservices(scope)
        req_obj = questionflag_serv.get_flagmaster(id)
        response = HttpResponse(req_obj.get(), content_type='application/json')
        return response

    elif request.method == 'DELETE':
        scope = request.scope
        questionflag_serv=Questionflagservices(scope)
        req_obj = questionflag_serv.del_flagmaster(id)
        response = HttpResponse(req_obj.get(), content_type='application/json')
        return response