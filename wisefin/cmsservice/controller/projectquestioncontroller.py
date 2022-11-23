import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from cmsservice.data.request.projectquestionrequest import Projectquesrequest, Projectproquesrequest, CMSActivityrequest
from cmsservice.service.projectquestionservice import Projectquesservice,Vow_question_answer
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission


# answer create and view
@csrf_exempt
@api_view(['POST', 'GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_projquestion(request,project_id):
    if request.method == 'POST':
        scope = request.scope
        ans_data = json.loads(request.body)
        arr = []
        for i in ans_data.get('data'):
            ans_obj = Projectquesrequest(i)
            arr.append(ans_obj)
        ans_service = Projectquesservice(scope)
        emp_id = request.employee_id
        response_obj = ans_service.create_projques(arr, project_id,emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response
    elif request.method == 'GET':
        scope = request.scope
        ans_service = Projectquesservice(scope)
        proposal_id = request.GET.get('proposal_id')
        response_obj = ans_service.question_fetch(project_id, proposal_id)
        response = HttpResponse(response_obj.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['POST','GET'])
def proposal_answer(request,project_id):
    if request.method == 'POST':
        ans_data = json.loads(request.body)
        arr = []
        for i in ans_data.get('data'):
            ans_obj = Projectproquesrequest(i)
            arr.append(ans_obj)
        ans_service = Vow_question_answer(request)
        emp_id = request.employee_id
        proposal_id = request.GET.get('proposal_id')
        response_obj = ans_service.create_projproposal(arr, project_id,proposal_id,emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response
    elif request.method == 'GET':
        ans_service = Vow_question_answer(request)
        proposal_id = request.GET.get('proposal_id')
        response_obj = ans_service.fetch_projectquestion(project_id,proposal_id)
        response = HttpResponse(response_obj.get(), content_type="application/json")
        return response


#  proposal catalog
@csrf_exempt
@api_view(['POST', 'GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_Catalog(request,proposal_id):
    if request.method == 'POST':
        scope = request.scope
        cat_data = json.loads(request.body)
        cat_obj = CMSActivityrequest(cat_data)
        ans_service = Projectquesservice(scope)
        emp_id = request.employee_id
        response_obj = ans_service.create_catlog(cat_obj,proposal_id,emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')

    elif request.method == 'GET':
        scope = request.scope
        jv_service = Projectquesservice(scope)
        resp_obj = jv_service.fetch_proposalcatlog(request,proposal_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

