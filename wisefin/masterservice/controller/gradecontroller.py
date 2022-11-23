import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from utilityservice.service.nwisefinpermission import NWisefinPermission
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from masterservice.data.request.graderequest import GradeRequest, DesignationGradeMappingRequest
from masterservice.service.gradeservice import GradeService, DesignationGradeMappingService
from utilityservice.data.response.nwisefinpage import NWisefinPage


@transaction.atomic
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_grade(request):
   scope = request.scope
   grade_service = GradeService(scope)
   if request.method =='POST':
       body_data=json.loads(request.body)
       grade_request=GradeRequest(body_data)
       user_id=request.employee_id
       resp_obj=grade_service.create_grade(grade_request,user_id)
       response = HttpResponse(resp_obj.get(), content_type="application/json")
       return response
   else:
       query = request.GET.get('query')
       page = request.GET.get('page', 1)
       page = int(page)
       vys_page = NWisefinPage(page, 10)
       resp_obj = grade_service.summary_grade(vys_page,query)
       response = HttpResponse(resp_obj.get(), content_type="application/json")
       return response


@transaction.atomic
@csrf_exempt
@api_view(['GET','DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_grade(request,id):
    scope=request.scope
    grade_service = GradeService(scope)
    if request.method == 'DELETE':
        resp_obj = grade_service.del_grade(id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    else:
        resp_obj = grade_service.fetchgrade(id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@transaction.atomic
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def search_grade(request,name):
     if request.method=='GET':
        scope=request.scope
        grade_service = GradeService(scope)
        resp_obj = grade_service.srch_grade(name)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@transaction.atomic
@csrf_exempt
@api_view(['GET','POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_designationgrademapping(request):
    scope = request.scope
    service = DesignationGradeMappingService(scope)
    if request.method=='POST':
        body_data= json.loads(request.body)
        mapping_request=DesignationGradeMappingRequest(body_data)
        user_id=request.employee_id
        resp=service.create_designationgrademapping(mapping_request,user_id)
        response = HttpResponse(resp.get(), content_type="application/json")
        return response
    else:
        resp=service.summary_designationgrademapping()
        response = HttpResponse(resp.get(), content_type="application/json")
        return response



@transaction.atomic
@csrf_exempt
@api_view(['GET','DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def del_designationgrademapping(request,id):
    scope = request.scope
    service = DesignationGradeMappingService(scope)
    if request.method=='DELETE':
        resp = service.del_designationgrademapping(id)
    else:
        resp = service.fetch_designationgrademapping(id)
    response = HttpResponse(resp.get(), content_type="application/json")
    return response















