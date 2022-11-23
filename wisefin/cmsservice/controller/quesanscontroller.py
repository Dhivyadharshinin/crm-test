import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from cmsservice.data.request.quesansrequest import Quesansrequest, Quesansmaprequest, Quesclassifyrequest, \
    Projansmaprequest, Answermaprequest
from cmsservice.service.quesansservice import Quesansservice, VowQuesansService
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission


# answer create and view
@csrf_exempt
@api_view(['POST', 'GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_answer(request):
    if request.method == 'POST':
        scope = request.scope
        ans_data = json.loads(request.body)
        arr = []
        for i in ans_data.get('data'):
            ans_obj = Quesansrequest(i)
            arr.append(ans_obj)
        ans_service = Quesansservice(scope)
        emp_id = request.employee_id
        response_obj = ans_service.createquesans(request,arr, emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response

    elif request.method == 'GET':
        return fetch_ans_list(request)


def fetch_ans_list(request):
    scope = request.scope
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    emp_id = request.employee_id
    ans_service = Quesansservice(scope)
    question_id = request.GET.get('question_id')
    question_type = request.GET.get('question_type')
    response_obj = ans_service.fetch_ans_list(request, question_id, question_type, vys_page, emp_id)
    response = HttpResponse(response_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['POST', 'GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_answermapp(request):
    if request.method == 'POST':
        scope = request.scope
        ans_data = json.loads(request.body)
        ans_obj = Quesansmaprequest(ans_data)
        ans_service = Quesansservice(scope)
        emp_id = request.employee_id
        response_obj = ans_service.createquesansmap(ans_obj, emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response


@csrf_exempt
@api_view(['POST', 'GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_ansmapp(request):
    if request.method == 'POST':
        scope = request.scope
        ans_data = json.loads(request.body)
        arr = []
        for i in ans_data:
            ans_obj = Answermaprequest(i)
            arr.append(ans_obj)
        ans_service = Quesansservice(scope)
        emp_id = request.employee_id
        response_obj = ans_service.createansmap(arr,emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response


@csrf_exempt
@api_view(['POST', 'GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_quesclassify(request):
    if request.method == 'POST':
        scope = request.scope
        ans_data = json.loads(request.body)
        ans_obj = Quesclassifyrequest(ans_data)
        ans_service = Quesansservice(scope)
        emp_id = request.employee_id
        response_obj = ans_service.createquesclassify(ans_obj, emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response


@csrf_exempt
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_projansmap(request,project_id):
    if request.method == 'POST':
        scope = request.scope
        pro_data = json.loads(request.body)
        arr=pro_data.get('arr')
        # for i in pro_data.get('data'):
            # ans_obj = Projansmaprequest(i)
            # arr.append(ans_obj)
        ans_service = Quesansservice(scope)
        emp_id = request.employee_id
        response_obj = ans_service.createquesprojmap(arr,project_id,emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response
#
# @csrf_exempt
# @api_view(['GET'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def fetch_questypee(request, pro_id):
#     if request.method == 'GET':
#         scope = request.scope
#         emp_id = request.employee_id
#         jv_service = Quesansservice(scope)
#         resp_obj = jv_service.fetch_projquesmap(pro_id)
#         response = HttpResponse(resp_obj.get(), content_type="application/json")
#         return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_questype(request, pro_id):
    if request.method == 'GET':
        scope = request.scope
        proj_service = Quesansservice(scope)
        resp_obj = proj_service.projectquestion(request,pro_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_evaluation(request, prop_id):
    if request.method == 'GET':
        scope = request.scope
        proj_service = Quesansservice(scope)
        type_id = request.GET.get('type_id')
        resp_obj = proj_service.fetch_evaluation(request,prop_id,type_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['POST','GET'])
def vow_create_answer(request,project_id):
    quesans_service = VowQuesansService(request)
    if request.method == 'POST':
        # ans_data = json.loads(request.body)
        ans_data = json.loads(request.data.dict().get('data'))
        arr=[]
        for i in ans_data:
            ans_obj = Quesansrequest(i)
            arr.append(ans_obj)
        response_obj = quesans_service.vow_createquesans(request,arr,project_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response

    elif request.method == 'GET':
        question_type = request.GET.get('question_type')
        response_obj = quesans_service.vow_fetch_ans_list(request,question_type)
        response = HttpResponse(response_obj.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['POST','GET'])
def prop_create_answer(request,proposer_id):
    quesans_service = VowQuesansService(request)
    if request.method == 'POST':
        ans_data = json.loads(request.body)
        question_type = request.GET.get('question_type')
        response_obj = quesans_service.prop_createquesans(request,ans_data,proposer_id,question_type)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response

@csrf_exempt
@api_view(['POST', 'GET'])
def vow_create_answermapp(request):
    quesans_service = VowQuesansService(request)
    if request.method == 'POST':
        ans_data = json.loads(request.body)
        ans_obj = Quesansmaprequest(ans_data)
        response_obj = quesans_service.vow_createquesansmap(ans_obj)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response


@csrf_exempt
@api_view(['POST', 'GET'])
def vow_createansmap(request):
    quesans_service = VowQuesansService(request)
    if request.method == 'POST':
        ans_data = json.loads(request.body)
        arr = []
        for i in ans_data.get('data'):
            ans_obj = Answermaprequest(i)
            arr.append(ans_obj)
        ref_id = request.GET.get('ref_id')
        ref_type = request.GET.get('ref_type')
        response_obj = quesans_service.vow_createansmap(arr,ref_id,ref_type)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response


@csrf_exempt
@api_view(['POST', 'GET'])
def vow_quesclassify(request):
    quesans_service = VowQuesansService(request)
    if request.method == 'POST':
        ans_data = json.loads(request.body)
        ans_obj = Quesclassifyrequest(ans_data)
        response_obj = quesans_service.vow_quesclassify(ans_obj)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response

@csrf_exempt
@api_view(['GET'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_vow_questype(request, pro_id):
    quesans_service = VowQuesansService(request)
    if request.method == 'GET':
        resp_obj = quesans_service.vow_projectquestion(request,pro_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def final_evaluation(request,project_id):
    if request.method == 'GET':
        scope = request.scope
        q_service=Quesansservice(scope)
        resp_obj = q_service.fetch_final_evaluation(request,project_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response\

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def q_approval_status_check(request,proposal_id):
    if request.method == 'GET':
        scope = request.scope
        q_service=Quesansservice(scope)
        resp_obj = q_service.approval_status_check(proposal_id)
        response = HttpResponse(resp_obj, content_type="application/json")
        return response

# @csrf_exempt
# @api_view(['GET'])
# def test_q(request):
#     if request.method == 'GET':
#         scope = request.scope
#         q_service=Quesansservice(scope)
#         vendor_id= request.GET.get('vendor_id')
#         proposal_id= request.GET.get('proposal_id')
#         resp_obj = q_service.test(vendor_id,proposal_id)
#         response = HttpResponse(resp_obj, content_type="application/json")
#         return response