import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from utilityservice.service.nwisefinauthenticate import NWisefinAuthentication
from utilityservice.service.nwisefinpermission import NWisefinPermission
from utilityservice.data.response.nwisefinpage import NWisefinPage
from masterservice.data.request.masterbusinesssegmentrequest import MasterBusinessSegmentrequest
from masterservice.service.masterbusinesssegmentservice import MasterBusinessSegmentService

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def master_business_segment(request):
    if request.method == 'POST':
        scope = request.scope
        emp_id = request.employee_id
        businessservice = MasterBusinessSegmentService(scope)
        masterbusinesssegment_obj = json.loads(request.body)
        # user_id = request.employee_id
        # emp_service = EmployeeService(scope)
        # empid = emp_service.get_empid_from_userid(user_id)
        masterbusinesssegment_obj = MasterBusinessSegmentrequest(masterbusinesssegment_obj)
        resp_obj = businessservice.create_masterbusinesssegment(masterbusinesssegment_obj, emp_id)
        response = HttpResponse(resp_obj.get(), content_type="application/json")
        return response


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes([NWisefinAuthentication])
@permission_classes([IsAuthenticated, NWisefinPermission])
def master_business_segment_seatch(request):
    scope = request.scope
    query = request.GET.get('query')
    page = request.GET.get('page', 1)
    page = int(page)
    vys_page = NWisefinPage(page, 10)
    masterservice = MasterBusinessSegmentService(scope)
    response_data = masterservice.fetch_master_businesssegment_search_list(query, vys_page)
    response = HttpResponse(response_data.get(), content_type="application/json")
    return response
