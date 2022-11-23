import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from cmsservice.data.request.cmsquestiontyperequest import Cmsquestiontyperequest, Cmsquestypemaprequest
from cmsservice.service.cmsquestiontypeservice import Cmsquestypeservice, VowQuesansService
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission


# answer create and view
@csrf_exempt
@api_view(['POST', 'GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_cmsquestype(request):
    if request.method == 'POST':
        scope = request.scope
        ans_data = json.loads(request.body)
        ans_obj = Cmsquestiontyperequest(ans_data)
        questype_service = Cmsquestypeservice(scope)
        emp_id = request.employee_id
        response_obj = questype_service.createcmsquestype(ans_obj, emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response


# answer create and view
@csrf_exempt
@api_view(['POST', 'GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_cmsquestypemap(request):
    if request.method == 'POST':
        scope = request.scope
        ans_data = json.loads(request.body)
        ans_obj = Cmsquestypemaprequest(ans_data)
        questype_service = Cmsquestypeservice(scope)
        emp_id = request.employee_id
        response_obj = questype_service.createcmsquestypemap(ans_obj, emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response


@csrf_exempt
@api_view(['POST', 'GET'])
def vow_create_cmsquestype(request):
    questype_service = VowQuesansService(request)
    if request.method == 'POST':
        ans_data = json.loads(request.body)
        ans_obj = Cmsquestiontyperequest(ans_data)
        response_obj = questype_service.vow_createcmsquestype(ans_obj)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response


@csrf_exempt
@api_view(['POST', 'GET'])
def vow_create_cmsquestypemap(request):
    questype_service = VowQuesansService(request)
    if request.method == 'POST':
        ans_data = json.loads(request.body)
        ans_obj = Cmsquestypemaprequest(ans_data)
        response_obj = questype_service.vow_createcmsquestypemap(ans_obj)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response
