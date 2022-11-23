import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from masterservice.data.response.appversionresponse import AppVersionResponse
from masterservice.service.appversion_server import AppVersionServerService
from masterservice.service.appversionservice import AppVersionService
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def version(request):
    if request.method == 'POST':
        emp_id = request.employee_id
        scope = request.scope
        appVersion_Service = AppVersionService(scope)
        app_data = json.loads(request.body)
        app_obj=AppVersionResponse(app_data)
        resp_obj = appVersion_Service.AppVersionData(app_obj, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_version(request)


def fetch_version(request):
    user_id = request.employee_id
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    scope = request.scope
    appVersion_Service = AppVersionService(scope)
    resp_obj = appVersion_Service.AppVersion(request,user_id,vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def appversion_activate_inactivate(request):
    if request.method == 'POST':
        scope = request.scope
        app_serv = AppVersionService(scope)
        fin_obj = json.loads(request.body)
        app_obj = AppVersionResponse(fin_obj)
        resp_obj = app_serv.appversion_activate_inactivate(request,app_obj)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@csrf_exempt
# @api_view(['GET'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_version_server(request,entity_id):
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    appVersionServer_Service = AppVersionServerService()
    resp_obj = appVersionServer_Service.AppVersion_Server(entity_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


# @csrf_exempt
# @api_view(['GET'])
# @authentication_classes([NWisefinAuthentication])
# @permission_classes([IsAuthenticated, NWisefinPermission])
# def fetch_Schema_Dropdown(request):
#     user_id = request.employee_id
#     scope = request.scope
#     appConfig_Service = CONFIGDBService(scope)
#     resp_obj = appConfig_Service.AppSchemaDropDown(request,scope)
#     response = HttpResponse(resp_obj.get(), content_type="application/json")
#     return response
