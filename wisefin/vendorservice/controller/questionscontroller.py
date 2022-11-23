import json
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from userservice.service.employeeservice import EmployeeService
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.vendorclassification_api import Vendormaster
from vendorservice.data.request.supplierrequest import ProfileRequest
from vendorservice.service.profileservice import ProfileService
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from vendorservice.service.questionanswerservice import QuestionanswerService
from vendorservice.service.questionservice import Qestionservice
from vendorservice.util.vendorutil import get_periodicity_list


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
#vendor_id
def evaluate_vendor(request,vendor_id):
    if request.method == 'GET':
        employee_id = request.employee_id
        scope = request.scope
        service = Qestionservice(scope)
        rep=service.fetch_vendoreval(request,vendor_id)
        if rep!={}:
            api = Vendormaster(scope)
            rep = api.get_vendorclassfication_type_api(rep)
            resp = json.loads(rep)

            if len(resp)>0:
                for x in resp['data']:
                    type_id = x['type_id']['id']
                    req_obj1 = api.get_vendortypemapping(vendor_id,type_id)
                    print("vendor_type_mapping", req_obj1)
                    x['mapping']=req_obj1
                    for y in range(len(x['question'])):
                        if len(x['question'][y]['sub_question'])>0:
                            for subquestion in range(len(x['question'][y]['sub_question'])):
                                print(subquestion)
                                ans_val = QuestionanswerService(scope)
                                sub_id = x['question'][y]['sub_question'][subquestion]['id']
                                obj = ans_val.question_answer_get_val(vendor_id, sub_id, type_id)
                                x['question'][y]['sub_question'][subquestion].__setitem__('answer_text', obj)
                        ans_val = QuestionanswerService(scope)
                        question_id=x['question'][y]['id']
                        req_obj = ans_val.question_answer_get_val(vendor_id,question_id,type_id)
                        x['question'][y].__setitem__('answer_text', req_obj)
                rep = json.dumps(resp, default=lambda o: o.__dict__,
                              sort_keys=True, indent=4)
        else:
            rep='[]'
        response = HttpResponse(rep, content_type="application/json")

        return  response

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def evaluate_suppliermapping(request,vendor_id):
    if request.method == 'GET':
        employee_id = request.employee_id
        scope = request.scope
        api = Vendormaster(scope)
        # service = Qestionservice(scope)
        rep=api.get_supplieractivity(vendor_id)
        repp = rep
        print("rep",rep)
        # supp = rep['rel_type']
        # print("supp",supp)
        # acty = rep['activity_id']
        # print("supp1", acty)
        if len(rep)>0:
            rep = api.get_vendorclassfication_mapping(repp)
            resp = json.loads(rep)
            print("resp",resp)
            if len(resp)>0:
                for x in resp['data']:
                    for type in x['type_data']:
                        type_id = type['type_id']['id']
                        activity_id = type['Activity']['id']
                        req_obj1 = api.get_vendortypemapping1(vendor_id,type_id,activity_id)
                        # print("vendor_type_mapping", req_obj1)
                        type['mapping']=req_obj1
                        for y in range(len(type['question'])):
                            for subquestion in range(len(type['question'][y]['sub_question'])):
                                print(subquestion)
                                ans_val = QuestionanswerService(scope)
                                question_id = type['question'][y]['sub_question'][subquestion]['id']
                                req_obj = ans_val.question_answer_get_val1(vendor_id, question_id, type_id,activity_id)
                                type['question'][y]['sub_question'][subquestion].__setitem__('answer_text', req_obj)
                            ans_val = QuestionanswerService(scope)
                            question_id=type['question'][y]['id']
                            req_obj = ans_val.question_answer_activity_mapping(vendor_id,question_id,type_id,activity_id)
                            type['question'][y].__setitem__('answer_text', req_obj)
                    rep = json.dumps(resp, default=lambda o: o.__dict__,
                                  sort_keys=True, indent=4)
        else:
            rep='[]'
        response = HttpResponse(rep, content_type="application/json")

        return  response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def evaluate_vendor_doc(request, vendor_id):
    if request.method == 'GET':
        scope = request.scope
        service = Qestionservice(scope)
        page = request.GET.get('page', 1)
        page = int(page)
        query = request.GET.get('query', None)
        vys_page = NWisefinPage(page, 10)
        rep = service.fetch_vendoreval(request,vendor_id)
        if rep!={}:
            api = Vendormaster(scope)
            resp = api.get_vendorclassfication_doc_api(rep,vys_page,query)
            response = HttpResponse(resp.get(), content_type='application/json')
        else:
            resp={"data":'[]'}
            response =HttpResponse(resp, content_type='application/json')
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_periodcity(request):
    scope = request.scope
    resp_obj = get_periodicity_list()
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response
