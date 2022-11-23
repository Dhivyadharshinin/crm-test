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
from vendorservice.data.request.questionvendormappingrequest import Questionansmappingrequest
from vendorservice.service.questionvendormappingservice import QuestionvendormapService


@csrf_exempt
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def question_vendor_mapping(request):
    if request.method == 'POST':
        scope = request.scope
        venans_data = json.loads(request.body)
        venans_service = QuestionvendormapService(scope)
        venans_obj = Questionansmappingrequest(venans_data)
        emp_id = request.employee_id
        response_obj = venans_service.question_answer_mapping(venans_obj,emp_id)
        response = HttpResponse(response_obj.get(), content_type='application/json')
        return response
