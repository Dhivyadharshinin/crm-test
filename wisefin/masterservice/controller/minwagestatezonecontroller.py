import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import authentication_classes, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from masterservice.data.request.minwagestatezonerequest import MinwageRequest

from masterservice.service.minwagestatezoneservice import minwageService

from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from utilityservice.data.response.nwisefinpage import NWisefinPage
from userservice.service.employeeservice import EmployeeService


@csrf_exempt
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_minwage(request):
    if request.method=='POST':
        scope = request.scope
        arrobj=json.loads(request.body)
        user_id = request.employee_id
        subject_service = minwageService(scope)
        emp_service = EmployeeService(scope)
        emp_id = emp_service.get_empid_from_userid(user_id)
        arr_obj=MinwageRequest(arrobj)
        resp_obj=subject_service.create_minwage(arr_obj,emp_id)
        response=HttpResponse(resp_obj.get(),content_type='application/json')
        return response
    elif request.method == 'GET':
        return minwagestate_list(request)

def minwagestate_list(request):
    scope = request.scope
    subject_service=minwageService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = subject_service.minwagestate_list(vys_page)
    response = HttpResponse(resp_obj.get(), content_type='application/json')
    return response