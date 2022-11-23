import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from docservice.service.documentservice import DocumentsService
from nwisefin.settings import logger
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage, ErrorDescription
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess, SuccessStatus, SuccessMessage
from utilityservice.service.api_service import ApiService
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from vendorservice.data.request.questionanswerrequest import QuestionanswerRequest
from vendorservice.data.request.questionvendormappingrequest import Questionansmappingrequest
from vendorservice.data.request.suboptionanswerrequest import SuboptionsanswerRequest
from vendorservice.service.questionanswerservice import QuestionanswerService
from vendorservice.service.questionvendormappingservice import QuestionvendormapService
from vendorservice.service.suboptionanswerservice import SuboptionanswerService
from vendorservice.util.vendorutil import get_approval_type_val, get_fileextension_atma
from utilityservice.data.response.nwisefinerror import NWisefinError



@csrf_exempt
@api_view(['POST', 'GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def question_answer_create(request):
    if request.method == 'POST':
        data_json = json.loads(request.body)
        scope = request.scope
        user_id = request.employee_id
        venans_obj = Questionansmappingrequest(data_json)
        ven_ans_mapping = QuestionvendormapService(scope)
        ven_map = ven_ans_mapping.question_answer_mapping(venans_obj, user_id)
        print("vendor_mapping", ven_map.vendor_id)
        vendor_id = ven_map.vendor_id
        answer = data_json.get("answers")
        arr = []
        sub_options = []
        for x in answer:
            question_req = QuestionanswerRequest(x)
            question_serv = QuestionanswerService(scope)
            question_ans_id = question_serv.question_answer_create(question_req, vendor_id, user_id)
            answer_id = question_ans_id.id
            input_value = x.get('input_value')
            sub_question_serv = SuboptionanswerService(scope)
            for y in input_value:
                suboption_req = SuboptionsanswerRequest(y)
                sub_options_create = sub_question_serv.suboption_create(suboption_req,user_id,answer_id)
                print(sub_options_create)
            if answer_id is None:
                error_msg = NWisefinError()
                error_msg.set_code('INVALID_ID')
                response = HttpResponse(error_msg.get(), content_type='application/json')
                return response
            arr.append(question_ans_id)
            # question_answer_suboption=SuboptionanswerService(scope)
            sub_option = x.get("sub_question")
            print("sub_question",sub_option)
            for i in sub_option:
                sub_option_req = QuestionanswerRequest(i)
                if answer_id!=None:
                    sub_option_resp=question_serv.question_answer_create(sub_option_req, vendor_id, user_id)
                    answer_id_val =sub_option_resp.id
                    sub_options.append(sub_option_resp)
                    input_value_sub = i.get('input_value')
                    for y in input_value_sub:
                        sub_answer_req = SuboptionsanswerRequest(y)
                        sub_answer_serv = SuboptionanswerService(scope)
                        sub_answer_insert = sub_answer_serv.suboption_create(sub_answer_req, user_id, answer_id_val)
                        print(sub_answer_insert)


        resp = NWisefinSuccess()
        resp.set_status(SuccessStatus.SUCCESS)
        resp.set_message(SuccessMessage.CREATE_MESSAGE)
        response = HttpResponse(resp.get(), content_type='application/json')
        return response

    elif request.method == 'GET':
        scope = request.scope
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        question_serv = QuestionanswerService(scope)
        req_obj = question_serv.fetch_question_answer(vys_page)
        response = HttpResponse(req_obj.get(), content_type='application/json')
        return response



@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def question_answer_get(request, id):
    if request.method == 'GET':
        scope = request.scope
        question_serv = QuestionanswerService(scope)
        req_obj = question_serv.question_answer_get(id)
        response = HttpResponse(req_obj.get(), content_type='application/json')
        return response

    elif request.method =="DELETE":
        scope = request.scope
        question_serv = QuestionanswerService(scope)
        req_serv = question_serv.del_question_answer(id)
        response = HttpResponse(req_serv.get(), content_type='application/json')
        return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def questioin_suboption_get(request, question_id):
    if request.method == 'GET':
        scope = request.scope
        question_answer_serv = QuestionanswerService(scope)
        sub_answer_serv = SuboptionanswerService(scope)
        question_ans_list = question_answer_serv.get_answer_req(question_id)

        if len(question_ans_list)>0:
            question_ans = question_answer_serv.question_answer_get(question_ans_list[0].id)
            sub_ans_question = sub_answer_serv.get_suboptions_answer(question_id)
            question_ans.subquestion=sub_ans_question
            response = HttpResponse(question_ans.get(), content_type='application/json')
            return response

        else:
            pass

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def approval_dropdown_val(request):
    if request.method == 'GET':
        approval_val = get_approval_type_val()
        response = HttpResponse(approval_val.get(), content_type='application/json')
        return response

@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_upload(request,vendor_id):
    if request.method == 'POST':
        scope = request.scope
        pro_data = json.loads(request.data.dict().get("data"))
        question_serv = QuestionanswerService(scope)
        emp_id = request.employee_id
        api_serv = ApiService(scope)
        question_req = QuestionanswerRequest(pro_data)
        question_ans_id = question_serv.question_answer_create(question_req, vendor_id, emp_id)
        answer_id = question_ans_id.id
        doc_module = {"module":17,"ref_id":1,"ref_type":1}  ###
        file_data = request.FILES.getlist('file')
        print("file",file_data)
        for file in file_data:
            file_name = file.name
            extension = file_name.split('.')[-1]
            filetype_check = get_fileextension_atma(extension)
            if filetype_check:
                doc_resp_obj = api_serv.doc_upload_atma(request, doc_module)
                document_json = doc_resp_obj['data']
                response_obj = question_serv.upload(document_json, answer_id, emp_id)
                print("response",response_obj)
                resp = NWisefinSuccess()
                resp.set_status(SuccessStatus.SUCCESS)
                resp.set_message(SuccessMessage.CREATE_MESSAGE)
                response = HttpResponse(response_obj.get(), content_type='application/json')
                return response
            else:
                pass

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_file(request,file_id):
    scope = request.scope
    doc_service = DocumentsService(scope)
    emp_id = request.employee_id
    resp_obj = doc_service.doc_download(file_id, emp_id)
    return resp_obj

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def delete_file(request,file_id):
    scope = request.scope
    emp_id = request.employee_id
    question_serv = QuestionanswerService(scope)
    resp_obj = question_serv.Delete_quesfiles(request,file_id,emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

#Transaction details
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_questransget(request, No):
    if request.method == 'GET':
        emp_id = request.employee_id
        scope = request.scope
        question_serv = QuestionanswerService(scope)
        type = request.GET.get('type')
        response = question_serv.ques_queuedetails(request,No,type)
        resp_obj = HttpResponse(json.dumps(response), content_type="application/json")
        return resp_obj

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def view_file(request, file_id):
    scope = request.scope
    logger.info("view file Id" + str(file_id))
    doc_service = DocumentsService(scope)
    response = doc_service.file_download(file_id, request)
    return response


@csrf_exempt
@api_view(['POST', 'GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def question_answer_create1(request):
    if request.method == 'POST':
        data_json = json.loads(request.body)
        scope = request.scope
        user_id = request.employee_id
        venans_obj = Questionansmappingrequest(data_json)
        ven_ans_mapping = QuestionvendormapService(scope)
        ven_map = ven_ans_mapping.question_answer_mapping(venans_obj, user_id)
        print("vendor_mapping", ven_map.vendor_id)
        vendor_id = ven_map.vendor_id
        answer = data_json.get("answers")
        arr = []
        sub_options = []
        for x in answer:
            question_req = QuestionanswerRequest(x)
            question_serv = QuestionanswerService(scope)
            question_ans_id = question_serv.question_answer_create1(question_req, vendor_id, user_id)
            answer_id = question_ans_id.id
            input_value = x.get('input_value')
            sub_question_serv = SuboptionanswerService(scope)
            for y in input_value:
                suboption_req = SuboptionsanswerRequest(y)
                sub_options_create = sub_question_serv.suboption_create(suboption_req,user_id,answer_id)
                print(sub_options_create)
            if answer_id is None:
                error_msg = NWisefinError()
                error_msg.set_code('INVALID_ID')
                response = HttpResponse(error_msg.get(), content_type='application/json')
                return response
            arr.append(question_ans_id)
            # question_answer_suboption=SuboptionanswerService(scope)
            sub_option = x.get("sub_question")
            print("sub_question",sub_option)
            for i in sub_option:
                sub_option_req = QuestionanswerRequest(i)
                if answer_id!=None:
                    sub_option_resp=question_serv.question_answer_create1(sub_option_req, vendor_id, user_id)
                    answer_id_val =sub_option_resp.id
                    sub_options.append(sub_option_resp)
                    input_value_sub = i.get('input_value')
                    for y in input_value_sub:
                        sub_answer_req = SuboptionsanswerRequest(y)
                        sub_answer_serv = SuboptionanswerService(scope)
                        sub_answer_insert = sub_answer_serv.suboption_create(sub_answer_req, user_id, answer_id_val)
                        print(sub_answer_insert)


        resp = NWisefinSuccess()
        resp.set_status(SuccessStatus.SUCCESS)
        resp.set_message(SuccessMessage.CREATE_MESSAGE)
        response = HttpResponse(resp.get(), content_type='application/json')
        return response

@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_activitytransget(request,No):
    if request.method == 'GET':
        emp_id = request.employee_id
        scope = request.scope
        question_serv = QuestionanswerService(scope)
        type = request.GET.get('type')
        # activity = request.GET.get('activity')
        response = question_serv.activity_queuedetails(request,No,type)
        resp_obj = HttpResponse(json.dumps(response), content_type="application/json")
        return resp_obj


@csrf_exempt
@api_view(['POST', 'GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def activity_answer_create(request):
    if request.method == 'POST':
        data_json = json.loads(request.body)
        scope = request.scope
        user_id = request.employee_id
        venans_obj = Questionansmappingrequest(data_json)
        ven_ans_mapping = QuestionvendormapService(scope)
        ven_map = ven_ans_mapping.question_answer_mapping(venans_obj, user_id)
        print("vendor_mapping", ven_map.Activity)
        activity_id = ven_map.Activity
        vendor_id = ven_map.vendor_id
        answer = data_json.get("answers")
        arr = []
        sub_options = []
        for x in answer:
            question_req = QuestionanswerRequest(x)
            question_serv = QuestionanswerService(scope)
            question_ans_id = question_serv.activity_answer_create(question_req, activity_id, user_id,vendor_id)
            answer_id = question_ans_id.id
            input_value = x.get('input_value')
            sub_question_serv = SuboptionanswerService(scope)
            for y in input_value:
                suboption_req = SuboptionsanswerRequest(y)
                sub_options_create = sub_question_serv.suboption_create(suboption_req, user_id, answer_id)
                print(sub_options_create)
            if answer_id is None:
                error_msg = NWisefinError()
                error_msg.set_code('INVALID_ID')
                response = HttpResponse(error_msg.get(), content_type='application/json')
                return response
            arr.append(question_ans_id)
            # question_answer_suboption=SuboptionanswerService(scope)
            sub_option = x.get("sub_question")
            print("sub_question", sub_option)
            for i in sub_option:
                sub_option_req = QuestionanswerRequest(i)
                if answer_id != None:
                    sub_option_resp = question_serv.activity_answer_create(sub_option_req, activity_id, user_id,vendor_id)
                    answer_id_val = sub_option_resp.id
                    sub_options.append(sub_option_resp)
                    input_value_sub = i.get('input_value')
                    for y in input_value_sub:
                        sub_answer_req = SuboptionsanswerRequest(y)
                        sub_answer_serv = SuboptionanswerService(scope)
                        sub_answer_insert = sub_answer_serv.suboption_create(sub_answer_req, user_id, answer_id_val)
                        print(sub_answer_insert)

        resp = NWisefinSuccess()
        resp.set_status(SuccessStatus.SUCCESS)
        resp.set_message(SuccessMessage.CREATE_MESSAGE)
        response = HttpResponse(resp.get(), content_type='application/json')
        return response

@csrf_exempt
@api_view(['POST', 'GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def activity_answer_create1(request):
    if request.method == 'POST':
        data_json = json.loads(request.body)
        scope = request.scope
        user_id = request.employee_id
        venans_obj = Questionansmappingrequest(data_json)
        ven_ans_mapping = QuestionvendormapService(scope)
        ven_map = ven_ans_mapping.question_answer_mapping(venans_obj, user_id)
        print("vendor_mapping", ven_map.Activity)
        activity_id = ven_map.Activity
        vendor_id = ven_map.vendor_id
        answer = data_json.get("answers")
        arr = []
        sub_options = []
        for x in answer:
            question_req = QuestionanswerRequest(x)
            question_serv = QuestionanswerService(scope)
            question_ans_id = question_serv.activity_answer_create1(question_req, activity_id, user_id,vendor_id)
            answer_id = question_ans_id.id
            input_value = x.get('input_value')
            sub_question_serv = SuboptionanswerService(scope)
            for y in input_value:
                suboption_req = SuboptionsanswerRequest(y)
                sub_options_create = sub_question_serv.suboption_create(suboption_req, user_id, answer_id)
                print(sub_options_create)
            if answer_id is None:
                error_msg = NWisefinError()
                error_msg.set_code('INVALID_ID')
                response = HttpResponse(error_msg.get(), content_type='application/json')
                return response
            arr.append(question_ans_id)
            # question_answer_suboption=SuboptionanswerService(scope)
            sub_option = x.get("sub_question")
            print("sub_question", sub_option)
            for i in sub_option:
                sub_option_req = QuestionanswerRequest(i)
                if answer_id != None:
                    sub_option_resp = question_serv.activity_answer_create1(sub_option_req, activity_id, user_id,vendor_id)
                    answer_id_val = sub_option_resp.id
                    sub_options.append(sub_option_resp)
                    input_value_sub = i.get('input_value')
                    for y in input_value_sub:
                        sub_answer_req = SuboptionsanswerRequest(y)
                        sub_answer_serv = SuboptionanswerService(scope)
                        sub_answer_insert = sub_answer_serv.suboption_create(sub_answer_req, user_id, answer_id_val)
                        print(sub_answer_insert)

        resp = NWisefinSuccess()
        resp.set_status(SuccessStatus.SUCCESS)
        resp.set_message(SuccessMessage.CREATE_MESSAGE)
        response = HttpResponse(resp.get(), content_type='application/json')
        return response
