import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from userservice.service.employeeservice import EmployeeService
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from masterservice.data.request.channelrequest import ChannelRequest
from masterservice.service.channelservice import ChannelService

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def channel(request):
    if request.method == 'POST':
        scope = request.scope
        emp_id = request.employee_id
        channel_service = ChannelService(scope)
        channel_obj = json.loads(request.body)
        cha_obj = ChannelRequest(channel_obj)
        user_id = request.employee_id
        emp_service = EmployeeService()
        emp_id = emp_service.get_empid_from_userid(user_id)
        resp_obj = channel_service.create_documenttype(cha_obj,emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
       return fetch_channel_list(request)

def fetch_channel_list(request):
        scope = request.scope
        channel_service = ChannelService(scope)
        emp_id = request.employee_id
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        query = request.GET.get('query', None)
        resp_obj = channel_service.fetch_channel_list(vys_page,query)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_channel(request, channel_id):
    if request.method == 'GET':
        scope = request.scope
        channel_service = ChannelService(scope)
        emp_id = request.employee_id
        resp_obj = channel_service.fetchchannel(channel_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
         return delete_channel(request, channel_id)
def delete_channel(request, channel_id):
    scope = request.scope
    emp_id = request.employee_id
    channel_service = ChannelService(scope)
    # user_id = request.user.id
    resp_obj = channel_service.delete_channel(channel_id,emp_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def search_channel(request):
    if request.method == 'GET':
        user_id = request.user.id
        page = request.GET.get('page', 1)
        page = int(page)
        vys_page = NWisefinPage(page, 10)
        query = None
        query = request.GET.get('query', None)
        scope = request.scope
        channel_service = ChannelService(scope)
        resp_obj = channel_service.search_channel(request, query, vys_page)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response

#inward
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def channel_summarysearch(request):
    scope = request.scope
    channel_service = ChannelService(scope)
    name = request.GET.get('name')
    code = request.GET.get('code')
    query = {"name": name, "code": code}
    print(query)
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    resp_obj = channel_service.channel_summarysearch(query, vys_page)
    response = HttpResponse(resp_obj.get(), content_type='application/json')
    return response

#inward
@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def channel_search(request):
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    query = request.GET.get('query', None)
    scope = request.scope
    channel_service = ChannelService(scope)
    resp_obj = channel_service.channel_search(query, vys_page)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response