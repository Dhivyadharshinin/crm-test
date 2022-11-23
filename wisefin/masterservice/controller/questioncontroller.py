import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated

from masterservice.controller.questiontypemappcontroller import Create_Questionflag
from masterservice.data.request.questionrequest import QuestionRequest
from masterservice.data.request.questionsubrequest import QuestionsubRequest
from masterservice.models import Questions
from masterservice.service.questionsubservice import QuestionsubService
from utilityservice.data.response.nwisefinlist import NWisefinList
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from masterservice.service.questionservice import QuestionService


@csrf_exempt
@api_view(['POST', 'GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_question(request):
    if request.method == 'POST':
        # data_json = json.loads(request.body.get('data'))
        data_json = json.loads(request.body)
        for x in data_json:
            input_type = x['input_type']
            header_id = x['header_id']
            type_id = x['type_id']
            scope = request.scope
            user_id = request.employee_id
            question_req = QuestionRequest(x)
            question_serv = QuestionService(scope)
            question_id = question_serv.create_question(question_req, user_id, input_type)
            subquestion_serv = QuestionsubService(scope)
            sub_question_val = x.get('Input_value')
            sub_question = x.get("sub_question")
            print("sub_question", sub_question)
            print(sub_question_val)
            for y in sub_question_val:
                sub_option_req = QuestionsubRequest(y)
                sub_question_val_obj = subquestion_serv.create_questionsub_options(sub_option_req, user_id, question_id)
            for i in sub_question:
                input_type_sub = i['input_type']
                sub_options_req = QuestionRequest(i)
                if question_id!=None:
                    sub_options_id =question_serv.create_question_info(sub_options_req, user_id, input_type_sub, question_id,header_id, type_id)
                    sub_question_serv = QuestionsubService(scope)
                    sub_question_val = i.get("Input_value")
                    for s in sub_question_val:
                        sub_option_req = QuestionsubRequest(s)
                        sub_question_val_resp = sub_question_serv.create_questionsub_options(sub_option_req, user_id,
                                                                                       sub_options_id)


        resp = NWisefinSuccess()
        resp.set_status(SuccessStatus.SUCCESS)
        resp.set_message(SuccessMessage.CREATE_MESSAGE)
        response = HttpResponse(resp.get(), content_type='application/json')
        return response


    elif request.method == 'GET':
        scope = request.scope
        page = request.GET.get('page', 1)
        is_all = request.GET.get('all', 0)
        is_type = request.GET.get('type_id',None)
        is_header = request.GET.get('header_id',None)

        page = int(page)
        vys_page = NWisefinPage(page, 10)
        question_serv = QuestionService(scope)
        if is_all:
            type_mapping = Create_Questionflag(request, is_type, is_header)
            req_obj = question_serv.fetch_all_questions(is_type,is_header)
        else:
            req_obj = question_serv.fetch_question(vys_page,request)
        response = HttpResponse(req_obj.get(), content_type='application/json')
        return response


@csrf_exempt
@api_view(['GET','DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_question(request, id):
    if request.method == 'GET':
        scope = request.scope
        question_serv = QuestionService(scope)
        req_obj = question_serv.get_question(id)
        response = HttpResponse(req_obj.get(), content_type='application/json')
        return response


    elif request.method == 'DELETE':
        scope = request.scope
        question_serv = QuestionService(scope)
        req_obj = question_serv.del_question_serv(id)
        response = HttpResponse(req_obj.get(), content_type='application/json')
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def question_typeget(request,type_id):
    if request.method == 'GET':
        scope = request.scope
        question_serv = QuestionService(scope)
        question_list = question_serv.get_question_type(type_id)
        response = HttpResponse(question_list.get(), content_type='application/json')
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_question_sub_question(request, question_id):
    if request.method == 'GET':
        scope = request.scope
        question_serv = QuestionService(scope)
        sub_question_serv = QuestionsubService(scope)
        question_list = question_serv.get_question_req(question_id)
        arr = NWisefinList()
        if len(question_list) > 0:
            question = question_serv.get_questions(question_list[0].id)
            sub_question = question_serv.get_sub_question_arr(question_id)
            question.sub_question = sub_question
            arr.append(question)
            # sub_question_val = sub_question_serv.get_questionsuboptions(question_id)
            # question.Input_value = sub_question_val
            response = HttpResponse(arr.get(), content_type='application/json')
            return response

        else:
            pass
            # resp = Error()
            # resp.set_description(ErrorMessage.INVALID_DATA)
            # resp.set_code('400')
            # response = HttpResponse(resp.get(), content_type='application/json')
            # return response








