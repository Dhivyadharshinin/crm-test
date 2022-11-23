import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import authentication_classes, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from utilityservice.data.response.nwisefinpage import NWisefinPage
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from masterservice.service.leavegrademappingservice import GradeMappingService


# leave grade mapping
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def grade_leave_mapping(request):
    scope = request.scope
    employee_id = request.employee_id
    service = GradeMappingService(scope)
    if request.method == 'POST':
        leave_data = json.loads(request.body)
        resp = service.gradeleave_mapping(leave_data, employee_id)

        response = HttpResponse(resp.get(), content_type="application/json")
        return response

    elif request.method == 'GET':
        grade = request.GET.get('grade')
        month , year = None,None
        resp = service.get_leave_grade(grade,month,year)
        resp = json.dumps(resp,indent=4)
        response = HttpResponse(resp, content_type="application/json")
        return response