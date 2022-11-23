import json
from django.db import transaction
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from cmsservice.service.legalclauseservice import LegalClauseService,VowLegalAgreement
from cmsservice.service.superscriptservice import SuperScriptService,VowSuperScriptService
from cmsservice.data.request.leaglclauserequest import LegalRequest
from cmsservice.util.cmsutil import ClausesUtil, AgreementTemplateUtil


@transaction.atomic
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def legal_clause_insert(request):
    if request.method=="POST":
        scope = request.scope
        emp_id = request.employee_id
        body = json.loads(request.body)
        data=LegalRequest(body)
        legal_service = LegalClauseService(scope)
        resp_obj=legal_service.legal_clause_insert(data,emp_id)
        response = HttpResponse(resp_obj.get(), content_type='application/json')
        return response
    if request.method=="GET":
        scope = request.scope
        legal_service = LegalClauseService(scope)
        resp_obj = legal_service.legal_clause_fetch(request)
        response = HttpResponse(resp_obj.get(), content_type='application/json')
        return response
@transaction.atomic
@api_view(['POST', 'GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def subclause(request,parent_id):
    if request.method == "POST":
        scope = request.scope
        emp_id = request.employee_id
        body = json.loads(request.body)
        data = LegalRequest(body)
        legal_service = LegalClauseService(scope)
        resp_obj = legal_service.subclause(data, emp_id,parent_id)
        response = HttpResponse(resp_obj.get(), content_type='application/json')
        return response
    if request.method == "GET":
        scope = request.scope
        legal_service = LegalClauseService(scope)
        resp_obj = legal_service.getsubclause(parent_id)
        response = HttpResponse(resp_obj.get(), content_type='application/json')
        return response


# @transaction.atomic
# @api_view(['POST'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def legal_clause_approval(request,legal_clause_id):
#     if request.method == "POST":
#         scope = request.scope
#         emp_id = request.employee_id
#         data = json.loads(request.body)
#         legal_service = LegalClauseService(scope)
#         resp_obj = legal_service.legal_clause_approval(legal_clause_id,data,emp_id)
#         response = HttpResponse(resp_obj.get(), content_type='application/json')
#         return response


@transaction.atomic
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def proposal_legal_Mapping(request,proposal_id):
    # if request.method == "POST":
    #     scope = request.scope
    #     emp_id = request.employee_id
    #     data = json.loads(request.body)
    #     legal_service = LegalClauseService(scope)
    #     resp_obj = legal_service.proposal_legal_Mapping(data,proposal_id,emp_id)
    #     response = HttpResponse(resp_obj.get(), content_type='application/json')
    #     return response
    if request.method=="GET":
        scope = request.scope
        legal_service = LegalClauseService(scope)
        resp_obj = legal_service.proposallegal_mapping_get(request,proposal_id)
        response = HttpResponse(resp_obj.get(), content_type='application/json')
        return response

@transaction.atomic
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def legal_agreement(request,proposal_id):
    if request.method == "POST":
        scope = request.scope
        emp_id = request.employee_id
        legal_service = LegalClauseService(scope)

        body = json.loads(request.body)
        data = LegalRequest(body)
        clauses_id=body.get("clauses_id")
        resp_obj = legal_service.legal_agreement(data,proposal_id,clauses_id,emp_id)
        response = HttpResponse(resp_obj.get(), content_type='application/json')
        return response
    elif request.method=="GET":
        scope = request.scope
        legal_service = LegalClauseService(scope)
        data=legal_service.legal_agreement_get(proposal_id)
        response = HttpResponse(data, content_type='application/json')
        return response

@transaction.atomic
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def clause_get(request):
    if request.method=="GET":
        data=json.dumps(ClausesUtil.drop_down_arr)
        response = HttpResponse(data, content_type='application/json')
        return response

@transaction.atomic
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def proposal_agreement(request,proposal_id):
    if request.method == "GET":
        scope = request.scope
        legal_service = LegalClauseService(scope)
        resp_obj = legal_service.proposal_agreement(proposal_id,request)
        response = HttpResponse(json.dumps(resp_obj), content_type='application/json')
        return response
@transaction.atomic
@api_view(['GET','DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def legal_clause_get(request,legal_clause_id):
    if request.method=="DELETE":
        scope = request.scope
        emp_id = request.employee_id
        legal_service = LegalClauseService(scope)
        resp_obj = legal_service.legal_clause_delete(legal_clause_id, emp_id)
        response = HttpResponse(resp_obj.get(), content_type='application/json')
        return response
    elif request.method=="GET":
        scope = request.scope
        legal_service = LegalClauseService(scope)
        resp_obj = legal_service.legal_clause_get(legal_clause_id,request)
        response = HttpResponse(resp_obj.get(), content_type='application/json')
        return response

@transaction.atomic
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def legal_agreement_download(request,legal_clause_id):
    scope = request.scope
    legal_service = LegalClauseService(scope)
    resp_obj=legal_service.legal_agreement_download(legal_clause_id)
    return resp_obj


@api_view(['GET'])
def vow_legal_agreement_download(request,legal_clause_id):
    legal_service = VowLegalAgreement(request)
    resp_obj=legal_service.vow_legal_agreement_download(legal_clause_id)
    return resp_obj



@transaction.atomic
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def agreement_moveto_vendor(request,proposal_agreement_id):
    if request.method == "POST":
        scope = request.scope
        emp_id = request.employee_id
        legal_service = LegalClauseService(scope)
        resp_obj=legal_service.agreement_moveto_vendor(proposal_agreement_id,emp_id)
        response = HttpResponse(resp_obj.get(), content_type='application/json')
        return response


@transaction.atomic
@api_view(['POST'])
def vow_agreement_accepted(request,proposal_agreement_id):
    if request.method == "POST":
        legal_service = VowLegalAgreement(request)
        resp_obj=legal_service.vendor_accepted(proposal_agreement_id)
        response = HttpResponse(resp_obj.get(), content_type='application/json')
        return response
    elif request.method=="GET":
        scope = request.scope
        legal_service = LegalClauseService(scope)
        data=legal_service.legal_agreement_get(proposal_agreement_id)
        response = HttpResponse(data, content_type='application/json')
        return response

@transaction.atomic
@api_view(['POST'])
def vow_agreement_return(request,proposal_agreement_id):
    if request.method == "POST":
        legal_service = VowLegalAgreement(request)
        data = json.loads(request.body)
        resp_obj=legal_service.vendor_return(proposal_agreement_id,data)
        response = HttpResponse(resp_obj.get(), content_type='application/json')
        return response

@transaction.atomic
@api_view(['GET'])
def vow_legal_agreement_get(request,proposal_id):
    if request.method == "GET":
        legal_service = VowLegalAgreement(request)
        resp_obj=legal_service.agreement_get(proposal_id)
        response = HttpResponse(resp_obj, content_type='application/json')
        return response

@transaction.atomic
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def legal_clause_typedropdown(request):
    data = json.dumps(AgreementTemplateUtil.arr)
    response = HttpResponse(data, content_type='application/json')
    return response

@transaction.atomic
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def agreement_superscript_comments(request,proposal_id):
    if request.method == "POST":
        scope = request.scope
        legal_service = SuperScriptService(scope)
        data = json.loads(request.body)
        resp_obj=legal_service.superscript_comments(proposal_id,data)
        response = HttpResponse(resp_obj.get(), content_type='application/json')
        return response

    elif request.method=="GET":
        scope = request.scope
        legal_service = SuperScriptService(scope)
        resp_obj=legal_service.get_superscript_comments(proposal_id,request)
        response = HttpResponse(resp_obj.get(), content_type='application/json')
        return response

@transaction.atomic
@api_view(['POST','GET'])
def vow_agreement_superscript(request,agreement_id):
    if request.method == "POST":
        ss_service = VowSuperScriptService(request)
        data = json.loads(request.body)
        resp_obj=ss_service.vow_agreement_superscript(agreement_id,data)
        response = HttpResponse(resp_obj.get(), content_type='application/json')
        return response

    elif request.method =="GET":
        ss_service = VowSuperScriptService(request)
        resp_obj=ss_service.get_vow_agreement_superscript(agreement_id,request)
        response = HttpResponse(resp_obj.get(), content_type='application/json')
        return response


@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def cms_superscript_comments(request,superscript_id):
    if request.method == "POST":
        scope = request.scope
        ss_service = SuperScriptService(scope)
        data = json.loads(request.body)
        emp_id = request.employee_id
        resp_obj=ss_service.cms_superscript_comments(data,superscript_id,emp_id)
        response = HttpResponse(resp_obj.get(), content_type='application/json')
        return response

@csrf_exempt
@api_view(['POST'])
def vow_superscript_comments(request,superscript_id):
    if request.method == "POST":
        ss_service = VowSuperScriptService(request)
        data = json.loads(request.body)
        resp_obj=ss_service.vow_superscript_comments(superscript_id,data)
        response = HttpResponse(resp_obj.get(), content_type='application/json')
        return response