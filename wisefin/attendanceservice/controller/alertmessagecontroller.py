from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from rest_framework.permissions import IsAuthenticated
from utilityservice.data.response.nwisefinpage import NWisefinPage
from django.http import HttpResponse
from attendanceservice.service.allertservice import AlertService
import json
from ipware import get_client_ip


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def update_alert_message(request, alert_id):
    scope = request.scope
    alert_serv = AlertService(scope)
    update_alert = alert_serv.update_status(alert_id)
    response = HttpResponse(update_alert.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def alert(request):
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    employee_id = request.employee_id
    scope = request.scope
    alert_serv = AlertService(scope)
    summary = alert_serv.alert_summary(vys_page, employee_id)
    response = HttpResponse(summary.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET', 'DELETE'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def get_alert(request, alert_id):
    scope = request.scope
    alert_serv = AlertService(scope)
    if request.method == 'GET':
        resp_obj = alert_serv.fetch_alert_message(alert_id)
    else:
        resp_obj = alert_serv.delete_alert_message(alert_id)
    response = HttpResponse(resp_obj.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
def get_ip(request):
    val = get_client_ip(request)
    ip = val[0]
    client_ip, is_routable = get_client_ip(request)
    data = {'IP':client_ip, 'is_routable':is_routable}
    resp_obj = json.dumps(data, indent=4)
    response = HttpResponse(resp_obj, content_type="application/json")
    return response
