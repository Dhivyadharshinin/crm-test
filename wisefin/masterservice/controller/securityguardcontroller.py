import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import authentication_classes, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from masterservice.data.request.securityguardrequest import SecurityguardRequest, EmployeetypecatRequest
from masterservice.service.securityguardservice import SecurityguardService
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from utilityservice.data.response.nwisefinpage import NWisefinPage
from userservice.service.employeeservice import EmployeeService


@csrf_exempt
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_employeementcat(request):
    if request.method=='POST':
        scope=request.scope
        arrobj=json.loads(request.body)
        user_id = request.employee_id
        subject_service = SecurityguardService(scope)
        emp_service = EmployeeService(scope)
        emp_id = emp_service.get_empid_from_userid(user_id)
        arr_obj=SecurityguardRequest(arrobj)
        resp_obj=subject_service.create_employeementcat(arr_obj,emp_id)
        response=HttpResponse(resp_obj.get(),content_type='application/json')
        return response
    elif request.method == 'GET':
        return employeementcat_list(request)

def employeementcat_list(request):
    scope = request.scope
    subject_service=SecurityguardService(scope)
    user_id = request.employee_id
    emp_service = EmployeeService(scope)
    emp_id = emp_service.get_empid_from_userid(user_id)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = subject_service.employeementcat_list(vys_page, emp_id)
    response = HttpResponse(resp_obj.get(), content_type='application/json')
    return response

@csrf_exempt
@api_view(['DELETE','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def delete_employeementcat(request,employeecat_id):
    if request.method=='DELETE':
        scope=request.scope
        event_service = SecurityguardService(scope)
        user_id = request.employee_id
        resp_obj = event_service.delete_employeementcat(employeecat_id, user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def search_empcatdesc(request):
    scope = request.scope
    subject_service = SecurityguardService(scope)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    query = request.GET.get('query', None)
    resp_obj = subject_service.search_empcatdesc(vys_page, query)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def create_employeementtypecat(request):
    if request.method=='POST':
        scope=request.scope
        arrobj=json.loads(request.body)
        user_id =request.user.id
        subject_service = SecurityguardService(scope)
        arr_obj=EmployeetypecatRequest(arrobj)
        resp_obj=subject_service.create_employeementtypecat(arr_obj,user_id)
        response=HttpResponse(resp_obj.get(),content_type='application/json')
        return response
    elif request.method == 'GET':
        return employeetypemaster_list(request)


def employeetypemaster_list(request):
    scope = request.scope
    subject_service = SecurityguardService(scope)
    user_id = request.employee_id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    emp_cat= request.GET.get('employee_cat')
    query= request.GET.get('query')
    resp_obj = subject_service.employeetypemaster_list(vys_page,emp_cat,query)
    response = HttpResponse(resp_obj.get(), content_type='application/json')
    return response


#  micro service calling apis

from masterservice.models.mastermodels import EmployeementTypemaster,Employeementcatgorymaster,NewStateZone,NewStateZoneMapping
from utilityservice.data.response.nwisefinlist import NWisefinList


@csrf_exempt
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_employee_type(request):

    arr_data = json.loads(request.body)
    id =arr_data['arr']
    obj = EmployeementTypemaster.objects.filter(id__in=id).values('id', 'emptype', 'empcat_id')
    arr = NWisefinList()
    for i in obj:
        data = {"id": i['id'], "name": i['emptype'], "empcat_id": i['empcat_id']}
        arr.append(data)
    response = HttpResponse(arr.get(), content_type='application/json')
    return response

@csrf_exempt
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_employee_type_name(request):
    type = request.GET.get('type', None)
    if type != None:
        obj = EmployeementTypemaster.objects.filter(empcat__empcat=type).values('id', 'emptype', 'empcat_id')
    else:
        obj = EmployeementTypemaster.objects.all().values('id', 'emptype', 'empcat_id')
    arr = NWisefinList()
    for i in obj:
        data = {"id": i['id'], "name": i['emptype'], "empcat_id": i['empcat_id']}
        arr.append(data)
    response = HttpResponse(arr.get(), content_type='application/json')
    return response

@csrf_exempt
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_employee_catgory(request):
    arr_data = json.loads(request.body)
    id = arr_data['arr']
    obj = Employeementcatgorymaster.objects.filter(id__in=id).values('id', 'empcat')
    arr =NWisefinList()
    for i in obj:
        data = {"id": i['id'], "name": i['empcat']}
        arr.append(data)
    response = HttpResponse(arr.get(), content_type='application/json')
    return response

@csrf_exempt
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_state_zone(request):
    arr_data = json.loads(request.body)
    id = arr_data['arr']
    obj = NewStateZone.objects.filter(id__in=id).values('id', 'name','code', 'state_id')
    arr = NWisefinList()
    for i in obj:
        data = {"id": i['id'], "name": i['name'],"code":i['code'], "state_id": i['state_id']}
        arr.append(data)
    response = HttpResponse(arr.get(), content_type='application/json')
    return response

@csrf_exempt
@api_view(['POST','GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_state_zone_mapping(request):
    arr_data = json.loads(request.body)
    id = arr_data['arr']
    obj = NewStateZoneMapping.objects.filter(id__in=id).values('id', 'zone', 'state_id')
    arr = NWisefinList()
    for i in obj:
        data = {"id": i['id'], "zone": i['zone'], "statezone_id": i['state_id']}
        arr.append(data)
    response = HttpResponse(arr.get(), content_type='application/json')
    return response
