import json
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from vendorservice.service.questionnaireservice import QuestionnaireService
from django.http import HttpResponse
from vendorservice.data.request.questionnairerequest import QuestionnaireRequest
from utilityservice.data.response.nwisefinsuccess import SuccessStatus, SuccessMessage, NWisefinSuccess
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription, ErrorMessage
from vendorservice.util.vendorutil import Questionnaire
from vendorservice.service.vendorservice import VendorService


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def bcp_quesitons(request, vendor_id):
    scope = request.scope
    question_service = QuestionnaireService(scope)
    if request.method == 'POST':
        try:
            bcp_data = json.loads(request.body)
            employee_id = request.employee_id
            values = bcp_data['data']
            resp_obj = question_service.bcp_question_list(vendor_id, Questionnaire.BCP_QUESTIONNAIRE)
            resp = resp_obj.data
            vendor_service = VendorService(scope)
            mod_status = vendor_service.get_modification_status(vendor_id)
            for i in values:
                for response in resp:
                    if i['ques_id'] == response.ques_id:
                        if (i['ans_bool'] == response.ans_bool) and (i['remarks'] == response.remarks):
                            pass
                        else:
                            quest_obj = QuestionnaireRequest(i)
                            if mod_status == True:
                                resp_obj = question_service.modify_question_bcp(vendor_id,Questionnaire.BCP_QUESTIONNAIRE,
                                                                                quest_obj,employee_id)
                            else:
                                resp_obj = question_service.create_questions_bcp(vendor_id, Questionnaire.BCP_QUESTIONNAIRE,
                                                                             quest_obj, employee_id)
                            print(resp_obj)

            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
            return HttpResponse(success_obj.get(), content_type='application/json')
        except:
            error_obj = NWisefinError()
            error_obj.set_code(ErrorMessage.INVALID_DATA)
            error_obj.set_description(ErrorDescription.INVALID_DATA)
            return HttpResponse(error_obj.get(), content_type='application/json')
    else:
        resp_obj = question_service.bcp_question_list(vendor_id, Questionnaire.BCP_QUESTIONNAIRE)
        return HttpResponse(resp_obj.get(), content_type='application/json')


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def due_quesitons(request, vendor_id):
    scope = request.scope
    question_service = QuestionnaireService(scope)
    if request.method == 'POST':
        # try:
            due_data = json.loads(request.body)
            employee_id = request.employee_id
            values = due_data['data']
            resp_obj = question_service.due_question_list(vendor_id, Questionnaire.DUE_DILIGENCE)
            resp = resp_obj.data
            vendor_service = VendorService(scope)
            mod_status = vendor_service.get_modification_status(vendor_id)
            for i in values:
                for response in resp:
                    if i['ques_id'] == response.ques_id:
                        if (i['direction'] == response.direction) and (i['remarks'] == response.remarks):
                            pass
                        else:
                            quest_obj = QuestionnaireRequest(i)
                            if mod_status == True:
                                resp_obj = question_service.modify_question_due(vendor_id,Questionnaire.DUE_DILIGENCE,
                                                                                quest_obj, employee_id)
                            else:
                                resp_obj = question_service.create_questions_due(vendor_id, Questionnaire.DUE_DILIGENCE,
                                                                             quest_obj, employee_id)
                            print(resp_obj)

            success_obj = NWisefinSuccess()
            success_obj.set_status(SuccessStatus.SUCCESS)
            success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
            return HttpResponse(success_obj.get(), content_type='application/json')
        # except:
        #     error_obj = NWisefinError()
        #     error_obj.set_code(ErrorMessage.INVALID_DATA)
        #     error_obj.set_description(ErrorDescription.INVALID_DATA)
        #     return HttpResponse(error_obj.get(), content_type='application/json')
    else:
        resp_obj = question_service.due_question_list(vendor_id, Questionnaire.DUE_DILIGENCE)
        return HttpResponse(resp_obj.get(), content_type='application/json')
