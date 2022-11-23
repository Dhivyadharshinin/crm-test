import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from masterservice.data.request.contactrequest import ContactRequest
from masterservice.service.contactservice import ContactService

# MST contact - create , insert , update , delete
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def contact(request):
    if request.method == 'POST':
        scope = request.scope
        contact_service = ContactService(scope)
        contact_data = json.loads(request.body)
        user_id = request.employee_id
        contact_obj = ContactRequest(contact_data)
        resp_obj = contact_service.create_contact(contact_obj,user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'GET':
        return fetch_contact_list(request)

def fetch_contact_list(request):
    scope = request.scope
    contact_service = ContactService(scope)
    user_id = request.employee_id
    resp_obj = contact_service.fetchcontact_list(user_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
def delete_contact(request,contact_id):
    scope = request.scope
    contact_service = ContactService(scope)
    user_id = request.employee_id
    resp_obj = contact_service.deletecontact(contact_id,user_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response

@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def fetch_contact(request, contact_id):
    if request.method == 'GET':
        scope = request.scope
        contact_service = ContactService(scope)
        user_id = request.user.id
        resp_obj = contact_service.fetchcontact(contact_id,user_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response
    elif request.method == 'DELETE':
        return delete_contact(request,contact_id)