from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from rest_framework.permissions import IsAuthenticated
from attendanceservice.util.attendanceutil import holiday_type_summary, attendance_summary_type
from django.http import HttpResponse


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def holiday_type(request):
    resp = holiday_type_summary()
    response = HttpResponse(resp.get(), content_type="application/json")
    return response


@csrf_exempt
@api_view(['GET'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def attendance_type_summary(request):
    resp = attendance_summary_type()
    response = HttpResponse(resp.get(), content_type="application/json")
    return response
