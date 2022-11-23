import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated
from masterservice.data.request.questionsubrequest import QuestionsubRequest
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from masterservice.service.questionsubservice import QuestionsubService


@csrf_exempt
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_questionsub_options(request):
    if request.method == 'POST':
        scope = request.scope
        data_json = json.loads(request.body)
        user_id = request.employee_id
        questionsuboption_req = QuestionsubRequest(data_json)
        questionsub_serv = QuestionsubService(scope)
        req_obj = questionsub_serv.create_questionsub_options(questionsuboption_req,user_id)
        response = HttpResponse(req_obj.get(),content_type='application/json')
        return response

    elif request.method == 'GET':
        scope = request.scope
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        questionsuboption_serv = QuestionsubService(scope)
        req_obj = questionsuboption_serv.fetch_questionsuboption(vys_page)
        response = HttpResponse(req_obj.get(), content_type='application/json')
        return response


@csrf_exempt
@api_view(['GET','DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_questionsub_options(request,id):
    if request.method == 'GET':
        scope = request.scope
        questionsuboption_serv = QuestionsubService(scope)
        req_obj = questionsuboption_serv.get_questionsub_options(id)
        response = HttpResponse(req_obj.get(), content_type='application/json')
        return response


    elif request.method == 'DELETE':
        scope = request.scope
        questionsuboption_serv = QuestionsubService(scope)
        req_obj = questionsuboption_serv.del_questionsub_options(id)
        response = HttpResponse(req_obj.get(), content_type='application/json')
        return response
